# 2026-09-26_per-request-proxy-timeout

**Date:** 2026-09-26
**Previous version:** 2026-09-20_housekeeping-extract-field-and-deprecations

## State

Generation asks the proxy for a 300s read timeout; every other call keeps the proxy default.

## Changes from previous version

Infrastructure only. **No prompt changed in this version**, so any difference in
output quality against `2026-09-20_housekeeping-extract-field-and-deprecations` is
sampling variance, not a change we made.

### Why

The proxy Space hard-coded `httpx.AsyncClient(timeout=60.0)`. Generation currently
takes 12–26s, so 60s was never binding — but it rules out every reasoning-capable
model on HF Inference Providers, which routinely exceed 60s on an 11-field prompt.
Worse, the failure mode is silent-ish and expensive: the proxy raises HTTP 500 on
timeout, and `call_proxy` only retries 503/504, so a slow call dies on the first
attempt while the provider has most likely already generated (and billed) the output.

Generation is a once-per-session call where latency genuinely does not matter. It is
the one call type that should be allowed to wait.

### What changed

- **`config.py`** — added `PROXY_TIMEOUT_GENERATION = 300` and
  `PROXY_TIMEOUT_MARGIN = 30`. `REQUEST_TIMEOUT` is unchanged at 180.
- **`providers.py`** — `call_proxy` takes `proxy_timeout: Optional[float] = None`.
  When set, it is sent as `"timeout"` in the payload and the client-side
  `requests` timeout becomes `max(REQUEST_TIMEOUT, proxy_timeout + MARGIN)`.
  When `None`, the field is omitted entirely and behaviour is byte-identical to
  the previous version. `CallResult` gained a `proxy_timeout` field, which reaches
  the run JSON through `to_dict()`.

### Outside `game_state/`, and therefore NOT in this snapshot

- **`tools/simulator.py`** — `_call_with_parse_retry` gained a `proxy_timeout`
  parameter, and `generate_character` passes `config.PROXY_TIMEOUT_GENERATION`.
  This is the only call site that opts in. Not versioned here; see
  `UNTRACKED_UNITY_NOTE` in `tools/save_version.py`.
- **The proxy Space** (`jejunepixels/noexit-proxy`, `app.py`) — added
  `timeout: float = 60.0` to `ChatRequest`, clamped to `[1, 600]`, with the connect
  timeout pinned at 10s so a dead provider fails fast. Deployed 2026-09-26 and
  verified live. **The Space is not under version control here at all** — if this
  harness is ever restored to an older version, the Space does not roll back with it.
  That is safe in this direction (older callers omit the field and get 60s), but a
  newer harness against an older Space would silently get 60s with no error.

### Why the margin exists

`REQUEST_TIMEOUT` (client) must exceed the proxy's read timeout, otherwise the
client gives up first and we learn nothing about what the provider was doing. With
the proxy at 300 and the client at 330, the proxy's timeout always fires first and
returns a real error.

### Deliberately not done

- **`max_tokens` is still dropped by the proxy.** `ChatRequest` does not declare it
  and pydantic v2 silently discards undeclared fields. Verified live on the current
  deploy: a call sending `max_tokens: 75` returned 96 completion tokens. The index
  bears this out across history — 28 of 52 dialogue calls exceed the 75-token cap,
  the longest is 2,479, and `finish_reason` is `"stop"` in all 52, never `"length"`.
  So `MAX_TOKENS_DIALOGUE = 75` has never been enforced. Left alone deliberately,
  because fixing the pass-through is not a one-line change: it would activate a cap
  that has never been active (truncating dialogue mid-sentence), and
  `MAX_TOKENS_GENERATION = 0` would start being sent literally, which on an
  OpenAI-compatible API means zero tokens or a validation error, not "unlimited".
  **Check whether `APIRequestHandler.cs` sends `max_tokens` the same way — if it
  does, the Unity Inspector's token limits are decorative in the shipped game too.**
- **No model change.** `MODEL_GENERATION` is still
  `Qwen/Qwen3-235B-A22B-Instruct-2507`. This version only makes a slower model
  *possible*; it does not adopt one.
- **`top_p`, `top_k` and `reasoning_effort` remain unforwardable** for the same
  pydantic reason as `max_tokens`. Relevant because Qwen's guidance for the
  Thinking variants is ~0.6 temperature with `top_p` 0.95, and `TEMP_GENERATION`
  is 0.95 — so a reasoning model cannot currently be run at its recommended
  sampling settings.
- **No `<think>` handling.** Nothing in `game_state/` or `tools/` strips reasoning
  blocks; `providers.py` reads `choices[0].message.content` directly. Whether
  reasoning arrives inline or in a separate `reasoning_content` field varies by
  provider, and the router load-balances across several — so this could work on one
  call and fail on the next. `extract_field` takes the *first* `**Field**` match
  from position 0, so a heading drafted inside a reasoning block would win over the
  real answer, `character_parse_complete` would pass, and the parse retry would
  never fire. **This must be solved before any thinking model is used for
  generation.**

### Unknown

HF Spaces' own ingress may cap request duration below our 600s clamp. Not
discoverable without a genuinely slow call, so it will surface the first time a
long generation runs.

## Unity files to update

- **config.py** ->
  - CharacterController.cs -- 'temp' field (shared by TEMP_DIALOGUE/TEMP_ADDRESSING/TEMP_NARRATOR -- changing just one of these three constants has no independent Unity equivalent; verify all three still agree before treating this as a clean port)
  - CharacterController.cs -- useQween0_6, useHuggingFaceProvider toggles
  - CharacterGenerator.cs -- temperature, age Random.Range(25,65), gender assignment
  - ModelNamesController -- model strings
- **providers.py** ->
  - APIRequestHandler.cs -- SendOpenAIRequest
  - InfoExtractorHandler.cs -- ExtractInfo

**Porting note:** Unity needs none of this. It omits the `timeout` field and keeps
the proxy's 60s default, which is what it has always had. Port only if Unity is ever
made to generate characters with a slow model. The one item above that *does* warrant
a look at the C# is the `max_tokens` question under "Deliberately not done".
