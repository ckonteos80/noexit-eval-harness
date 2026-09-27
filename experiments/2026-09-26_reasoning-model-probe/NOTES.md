# 2026-09-26 — Reasoning model probe

**Question:** can a reasoning model be used for character generation? Specifically: does the
reasoning arrive inline as `<think></think>` in `content`, or in a separate field? That
decides whether `extract_field` needs to strip it.

Both probes sent **the real generation prompt**, not a toy one — same cost, and it previews
output quality as well as response shape.

## Probe 1 — `Qwen/Qwen3-235B-A22B-Thinking-2507`: failed, informatively

**HTTP 500 after 120.7 seconds**, wrapping a `504 Gateway Time-out` from upstream. No body,
so nothing is saved here.

Three things came out of that failure:

- **The HF router has a gateway timeout at roughly 120s.** Our proxy had just been raised to
  a 300s clamp in `2026-09-26_per-request-proxy-timeout`; that clamp sits *above* a ceiling
  we do not control. Reaching this model needs streaming, which the proxy does not support.
- **The proxy masks every upstream status as HTTP 500.** The Space log shows
  `ERROR:app:Unexpected error: 504` — the `raise HTTPException(504)` inside the `try` is
  caught by the generic `except Exception` and re-raised as 500. Because `call_proxy` only
  retries on 503/504, it therefore **never retries**. `cold_start` is `false` on all 288
  calls in `index.sqlite` and has never once been true. Still unfixed; it is in the Space,
  outside this repo's version control.
- The margin design from the previous version did its job: instead of a blind client-side
  hang we got a precise upstream error with a timestamp.

**Correction:** I had said a proxy timeout would be retried twice. It is not — a 500 falls
straight through to `raise ProxyError` and the session dies on the first attempt.

## Probe 2 — `openai/gpt-oss-120b`: worked, and found a different bug

`gpt-oss-120b_response.json` is the full response.

- **2.7 seconds.** Two orders of magnitude inside the ceiling.
- **4,669 tokens** against 2,709 for the instruct model on the same prompt, of which
  **2,159 were reasoning** — ~84% of billed output is thinking the game never sees.
- **Reasoning came back in a separate `reasoning` field**, with `content` clean. So
  `providers.py`, which reads `choices[0].message.content`, needs no stripping *for this
  provider*.

**But the hazard is real.** That reasoning field contains **all eleven `**Field**`
headings** — the model drafts the entire character before writing the answer. If any
provider inlined it, `extract_field` takes the first match from position 0 and would return
the draft instead of the real output, `character_parse_complete` would pass, the parse retry
would never fire, and nothing in the run record would show it. The router load-balances
`gpt-oss-120b` across 11 providers, so the shape can differ between consecutive calls.

**And a bug with nothing to do with reasoning models.** The parse failed on
`reason_self_told`:

```
expected:    Reason for Damnation — Self-told      (U+002D hyphen-minus)
model wrote: Reason for Damnation — Self‑told      (U+2011 NON-BREAKING HYPHEN)
```

`extract_field` used an exact `find()`, so it missed the heading entirely and cost a parse
retry. The model used U+2011 five times in one response.

## Quality signal (n=1)

> *"You seized a live 400-volt cable on the site, pulled it down to prove your strength to
> Maja Eriksson, and the electric shock killed you instantly."*

A decision, nothing had to go wrong, no intent to die — inside the corridor on the first
attempt, where the instruct model had hit a wall for three runs. Fields noticeably terser;
prose came in at 100 words, under the cap.

## What was decided

- `2026-09-26_tolerant-field-extraction` — dash/space folding plus defensive `<think>`
  stripping in `extract_field`. Verified against 6,300 historical extractions: 0 differences.
- `2026-09-26_generation-on-gpt-oss-120b` — the model swap. **Judged bad**: 1.9x tokens,
  literal sentence-template collapse across both characters, two fields structurally broken.
- `2026-09-26_generation-temperature-0-6` — temperature alone. **Also bad**: verbatim overlap
  rose from 132 to 194 chars. Reverted to the 235B.

The one-character probe was promising and the full pair was not. Treat single-character
probes as evidence to try something, never as evidence that it works.
