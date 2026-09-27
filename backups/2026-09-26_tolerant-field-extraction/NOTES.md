# 2026-09-26_tolerant-field-extraction

**Date:** 2026-09-26
**Previous version:** 2026-09-26_per-request-proxy-timeout

## State

extract_field folds dash/space variants and strips <think> blocks; replayed 6,300 historical extractions unchanged.

## Changes from previous version

Parser robustness only. **No prompt changed, and no model changed**, so output
quality is not expected to move. This exists to make a reasoning model safe to
adopt in the *next* version.

### Why: two separate hazards, one found by accident

**1. Unicode heading variance — an observed failure, not a hypothetical.**
A probe of `openai/gpt-oss-120b` with the real generation prompt wrote the heading
`Reason for Damnation — Self‑told` using U+2011 NON-BREAKING HYPHEN where the prompt
uses an ASCII hyphen. `extract_field` used an exact `find()`, so it missed the
heading entirely: the field came back empty, `character_parse_complete` returned
False, and the whole generation would have been retried at full cost. The model used
U+2011 five times in one response. This has nothing to do with reasoning models —
any model with typographic habits could trip it, and the em dashes already in our
own headings make the surface wide.

**2. Reasoning blocks would have been parsed as the answer.**
The same probe returned its reasoning in a separate `reasoning` field with `content`
left clean, so nothing was broken in practice. But that reasoning field **contained
all eleven `**Field**` headings** — the model drafts the entire character before
writing the real one. Whether reasoning is inlined as `<think></think>` or returned
separately is a per-provider behaviour, and the HF router load-balances across
several providers per model (eleven for gpt-oss-120b), so the same model can answer
either way between two consecutive calls. Because `extract_field` takes the FIRST
match from position 0, an inlined draft sits earlier in the string than the real
answer and wins. `character_parse_complete` would pass, the parse retry would never
fire, and the run record would show nothing wrong. The verification below
demonstrates this on a constructed response: the old code returns `DRAFT NAME`.

### What changed — `assembly.py` only

- **`_MATCH_EQUIV`** — maps 8 dash variants to `-` and 4 space variants to a space.
  Every entry is one character to exactly one character, so `str.translate` is
  **length-preserving**. That is the crux of the design: matching happens against a
  folded copy, but the value is sliced out of the *original*, so offsets carry over
  and the returned text keeps its real characters. A bio containing an em dash still
  contains an em dash.
- **`strip_reasoning()`** — removes `<think></think>` pairs. An unclosed `<think>`
  means the reasoning was truncated before an answer existed, so everything from it
  onward is dropped too. Short-circuits on responses with no `<think>`, which is
  every response on record.
- **`extract_field()`** — calls `strip_reasoning`, then searches the folded copy and
  slices the original.

### Verification

Replayed **6,300 extractions across 572 responses from 40 run files** (all of
`runs/` plus every archived `backups/*/runs/`), comparing the old implementation
against the new for every heading that actually appears in each response plus all
eleven canonical labels: **0 differences**. Plus:

- U+2011 heading: old `None` → new extracts correctly
- a value containing em dash, non-breaking hyphen and NBSP round-trips byte-identical
- constructed `<think>` draft: old returns `DRAFT NAME`, new returns `Real Name`
- unclosed `<think>`: real answer still returned
- the actual gpt-oss-120b probe response: old missing `reason_self_told`, new parses
  all eleven fields complete

### Deliberately not done

- **Case-insensitive heading matching.** A model writing `Reason For Damnation`
  would still miss. Not observed, and case folding is a wider change than dash
  folding, so it is left until something actually fails on it.
- **No model change.** `MODEL_GENERATION` is still
  `Qwen/Qwen3-235B-A22B-Instruct-2507`. The gpt-oss-120b swap is deliberately a
  separate version so parser and model changes stay separable.
- **Reasoning is not captured or stored.** Decided explicitly: we do not need to see
  it. `providers.py` reads `choices[0].message.content` and ignores the separate
  `reasoning` field, which is the desired behaviour, not an oversight.
- **`reasoning_effort` is not sent** — it is undeclared in the proxy's `ChatRequest`
  and would be silently dropped. Running at provider default by choice for now.

### Carried in from earlier work, still open

- **`Qwen/Qwen3-235B-A22B-Thinking-2507` is unreachable.** Measured: the HF router
  returns `504 Gateway Time-out` at roughly 120s, well inside our 300s proxy clamp,
  so the clamp raised in the previous version sits above a ceiling we do not
  control. Reaching that model needs streaming, which the proxy does not support.
  `gpt-oss-120b` answered the same prompt in **2.7s**, so it is unaffected.
- **The proxy masks every upstream status as HTTP 500.** `raise HTTPException(...)`
  inside the `try` is caught by the generic `except Exception` and re-raised as 500.
  Consequence: `call_proxy` only retries on 503/504 and therefore **never retries** —
  `cold_start` is `false` on all 288 calls in `index.sqlite` and has never once been
  true. Fixing this is a proxy change, outside version control here.
- **`max_tokens` is still dropped by the proxy**, for the same pydantic reason. See
  the previous version's notes for why fixing it is not a one-liner.

## Unity files to update

- **assembly.py** ->
  - CharacterController.cs -- prompt assembly / dialogue formatting
  - CharacterGenerator.cs -- ExtractField, bio assembly

**Porting note:** `ExtractField` in `CharacterGenerator.cs` needs both changes if
Unity is ever pointed at a reasoning model, and needs the dash folding regardless,
since the Unicode hazard is model-wide rather than reasoning-specific. In C#, fold
the haystack and the marker with the same one-to-one character map before
`IndexOf`, then substring the original — the length-preserving property is what
makes that safe. This is on top of the line-anchored end marker from
`2026-09-20_housekeeping-extract-field-and-deprecations`, which is still unported.
