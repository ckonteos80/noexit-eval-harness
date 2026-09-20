"""
Wrappers for the noexit proxy and info extractor HuggingFace Spaces.
Mirrors APIRequestHandler.cs and InfoExtractorHandler.cs.

CHANGE (harness eval loop): call_proxy and call_info_extractor now return a
CallResult object instead of a bare string. CallResult.content holds the reply
text (as before); the other fields carry the metadata the experiment store needs
(tokens, response time, retries, requested vs served model, finish_reason).

Migration note for callers: replace `x = call_proxy(...)` usage of `x` as a
string with `x.content`. See simulator.py for the updated call sites.
"""

import requests
import time
from dataclasses import dataclass
from typing import Optional, Any

from game_state import config


class ProxyError(Exception):
    """Raised when the proxy returns a non-success response after retries."""
    pass


class InfoExtractorError(Exception):
    """Raised when the info extractor fails after retries."""
    pass


@dataclass
class CallResult:
    """
    Everything one LLM call produced, for the experiment record.

    content         : the reply text (what callers previously received directly)
    requested_model : the model string we asked for
    served_model    : the model the provider actually served (can differ, e.g. -Turbo)
    prompt_tokens / completion_tokens / total_tokens / cached_tokens:
                      token usage as reported by the endpoint; None if unavailable
                      (the info extractor does not report usage)
    finish_reason   : why generation stopped ("stop", "length", ...); None if n/a
    response_time_s : wall-clock seconds from first request attempt to success
    retry_count     : how many retries happened before success (0 = first try)
    cold_start      : True if any retry was triggered by a 503/504 (space warming up)
    provider        : provider routing used ("hf"/"openai") — None for the extractor
    temperature     : temperature used — None for the extractor
    max_tokens      : max_tokens setting used — None for the extractor
    endpoint        : which URL was hit
    """
    content: str
    requested_model: Optional[str] = None
    served_model: Optional[str] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None
    finish_reason: Optional[str] = None
    response_time_s: Optional[float] = None
    retry_count: int = 0
    cold_start: bool = False
    provider: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    endpoint: Optional[str] = None

    def to_dict(self) -> dict:
        """Flat dict for storing in the run record / SQLite index."""
        return {
            "content": self.content,
            "requested_model": self.requested_model,
            "served_model": self.served_model,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "cached_tokens": self.cached_tokens,
            "finish_reason": self.finish_reason,
            "response_time_s": self.response_time_s,
            "retry_count": self.retry_count,
            "cold_start": self.cold_start,
            "provider": self.provider,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "endpoint": self.endpoint,
        }


def call_proxy(
    system: str,
    user: str,
    model: str,
    temperature: float,
    max_tokens: int,
    provider: Optional[str] = None,
    retry_attempts: int = 2,
) -> CallResult:
    """
    POST to the noexit proxy, mirroring APIRequestHandler.SendOpenAIRequest.

    Returns a CallResult (use .content for the reply text).

    Differences from Unity:
    - Does NOT strip newlines from messages (Unity has a bug doing this).
    - Retries on 503/504/timeout/connection errors, up to retry_attempts.

    Raises ProxyError on final failure.
    """
    if provider is None:
        provider = config.PROVIDER

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": max_tokens,
        "provider": provider,
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "noexit-harness",
    }

    last_error = None
    retry_count = 0
    cold_start = False
    t0 = time.time()

    for attempt in range(retry_attempts + 1):
        try:
            response = requests.post(
                config.PROXY_URL,
                json=payload,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            last_error = f"Connection error: {e}"
            if attempt < retry_attempts:
                retry_count += 1
                time.sleep(10)
                continue
            raise ProxyError(f"Proxy call failed after {attempt + 1} attempts: {last_error}")

        if response.status_code == 200:
            try:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                if not content:
                    raise ProxyError(f"Proxy returned empty content. Raw: {response.text[:500]}")

                usage = data.get("usage", {}) or {}
                finish_reason = None
                try:
                    finish_reason = data["choices"][0].get("finish_reason")
                except (KeyError, IndexError):
                    pass

                return CallResult(
                    content=content,
                    requested_model=model,
                    served_model=data.get("model"),
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    total_tokens=usage.get("total_tokens"),
                    cached_tokens=usage.get("cached_tokens"),
                    finish_reason=finish_reason,
                    response_time_s=round(time.time() - t0, 3),
                    retry_count=retry_count,
                    cold_start=cold_start,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    endpoint=config.PROXY_URL,
                )
            except (KeyError, IndexError, ValueError) as e:
                raise ProxyError(f"Malformed proxy response: {e}. Raw: {response.text[:500]}")

        # Retryable status codes (cold start, timeout)
        if response.status_code in (503, 504):
            last_error = f"HTTP {response.status_code}: {response.text[:200]}"
            if attempt < retry_attempts:
                retry_count += 1
                cold_start = True
                time.sleep(10)
                continue

        # Non-retryable
        raise ProxyError(
            f"Proxy returned HTTP {response.status_code}: {response.text[:500]}"
        )

    raise ProxyError(f"Proxy call failed after {retry_attempts + 1} attempts: {last_error}")


def call_info_extractor(text: str, system_prompt: str, retry_attempts: int = 2) -> CallResult:
    """
    POST to the info extractor space, mirroring InfoExtractorHandler.ExtractInfo.

    Returns a CallResult (use .content for the extracted info, or the literal
    "none" if nothing was found). Token fields are None — the extractor endpoint
    does not report usage.

    Raises InfoExtractorError on final failure (but typically the extractor
    returns "none" rather than erroring on edge cases).
    """
    payload = {
        "text": text,
        "system_prompt": system_prompt,
    }

    headers = {"Content-Type": "application/json"}

    last_error = None
    retry_count = 0
    cold_start = False
    t0 = time.time()

    for attempt in range(retry_attempts + 1):
        try:
            response = requests.post(
                config.INFO_EXTRACTOR_URL,
                json=payload,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            last_error = f"Connection error: {e}"
            if attempt < retry_attempts:
                retry_count += 1
                time.sleep(5)
                continue
            raise InfoExtractorError(f"Info extractor failed after {attempt + 1} attempts: {last_error}")

        if response.status_code == 200:
            try:
                data = response.json()
                result = (data.get("result", "") or "").strip()
                if not result:
                    result = "none"
                return CallResult(
                    content=result,
                    requested_model="qwen3-0.6B-info-extractor" if config.USE_QWEN_0_6 else "qwen3-4B-info-extractor",
                    served_model=None,
                    response_time_s=round(time.time() - t0, 3),
                    retry_count=retry_count,
                    cold_start=cold_start,
                    endpoint=config.INFO_EXTRACTOR_URL,
                )
            except ValueError as e:
                raise InfoExtractorError(f"Malformed extractor response: {e}. Raw: {response.text[:500]}")

        if response.status_code in (503, 504):
            last_error = f"HTTP {response.status_code}"
            if attempt < retry_attempts:
                retry_count += 1
                cold_start = True
                time.sleep(5)
                continue

        raise InfoExtractorError(
            f"Info extractor returned HTTP {response.status_code}: {response.text[:500]}"
        )

    raise InfoExtractorError(f"Info extractor failed after {retry_attempts + 1} attempts: {last_error}")
