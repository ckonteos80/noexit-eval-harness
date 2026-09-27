# 2026-09-26_generation-on-gpt-oss-120b

**Date:** 2026-09-26
**Previous version:** 2026-09-26_tolerant-field-extraction

## State

MODEL_GENERATION swapped to openai/gpt-oss-120b, a reasoning model; temperature and all other models unchanged.

## Changes from previous version

One line of substance: `MODEL_GENERATION` moves from
`Qwen/Qwen3-235B-A22B-Instruct-2507` to `openai/gpt-oss-120b`.

**Nothing else moved, on purpose.** No prompt changed. `TEMP_GENERATION` stays at
0.95. `MODEL_DIALOGUE`, `MODEL_ADDRESSING` and `MODEL_NARRATOR` stay on
`Qwen/Qwen3-8B`. The parser changes that make this safe landed in the previous
version precisely so that model and parser would not move together.

### Why a reasoning model at all

Three consecutive runs failed the death rules structurally rather than randomly.
The prompt defines a corridor with two walls — "your death must come out of a
decision you made" and "you did not intend to die" — and describes neither from the
inside. Characters kept leaving through one wall or the other, and in the last two
runs they did so by position: character 1 through intent, character 2 through
accident, both times.

That is the kind of constraint a model might satisfy by checking its own draft
against the rules before answering, which is what reasoning models do. It is a
hypothesis, not a fix — the corridor is still undescribed, and if the sameness and
the wall-breaking persist here, that is strong evidence the problem is the prompt's
geometry rather than the model's care.

### Why gpt-oss-120b specifically

`Qwen/Qwen3-235B-A22B-Thinking-2507` is the stronger model and was the first choice.
It is unreachable through this path: the HF router returns **504 Gateway Time-out at
roughly 120s**, and the 11-field generation prompt needs longer. That ceiling sits
below the 300s clamp raised in `2026-09-26_per-request-proxy-timeout`, so the clamp
cannot help — reaching that model requires streaming, which the proxy does not
support. `gpt-oss-120b` answered the same prompt in **2.7s** and has 11 live
providers, the widest routing of any candidate.

### Measured on the probe (n=1, single character, not a full run)

- 2.7s, 4,669 total tokens against 2,709 for the instruct model on the same prompt
  — roughly 1.7x. Of 2,559 completion tokens, **2,159 were reasoning**, so ~84% of
  what is billed as output is thinking the game never sees.
- Reasoning came back in a separate `reasoning` field with `content` clean.
- Its death: *"You seized a live 400-volt cable on the site, pulled it down to prove
  your strength to Maja Eriksson, and the electric shock killed you instantly."*
  A decision, nothing had to go wrong for it to kill him, and he did not intend to
  die — **inside the corridor on the first attempt**. Its sin connected too (forged
  negative references to block her job applications, keeping her dependent).
- Fields read noticeably terser than the 235B's. Prose came in at 100 words, under
  the 110 cap, which almost never happens.

Treat all of that as one sample. It is the reason to try, not evidence that it works.

### What to watch for in the first real runs

- **Does the corridor hold for both characters?** Character 2 is the one to watch,
  since it is the only one shown the other bio and told to differ.
- **Terseness.** Shorter fields may read as cleaner or as thinner. The 235B's
  failure mode was inflation — a 171-word cause of death in the last run — so terser
  is not automatically worse.
- **Cost.** ~1.7x per character, and reasoning tokens scale with prompt difficulty,
  so a harder prompt costs more than a linear estimate suggests.
- **Parse retries.** The previous version fixed the U+2011 heading that cost a retry
  on the probe. If `retry_count` is above 0 on generation calls, there is another
  formatting variance the parser has not been taught yet.

### Deliberately not done

- **Temperature unchanged at 0.95.** Qwen publishes ~0.6 for its Thinking variants
  and high temperature is known to hurt reasoning chains, so 0.95 is very likely
  wrong for this model. It stays anyway: temperature has been constant across every
  version on record, and moving it in the same version as the model would make a
  quality difference unattributable. Change it next, alone, if this version
  underperforms.
- **`reasoning_effort` not sent.** Undeclared in the proxy's `ChatRequest`, so it
  would be silently dropped. Running at provider default by explicit decision.
- **Reasoning not captured.** Decided explicitly: we do not need to see it.
- **`top_p` / `top_k` still unforwardable**, same pydantic cause as `max_tokens`.

### Rollback

`python tools/restore_version.py tolerant-field-extraction` returns generation to
the 235B with every parser fix intact. The parser changes are model-agnostic and
worth keeping regardless of which model wins.

### Carried in, still open

- The proxy masks every upstream status as HTTP 500, so `call_proxy`'s 503/504 retry
  has never fired — `cold_start` is false on all 288 calls on record.
- `max_tokens` is still dropped by the proxy.
- The anti-duplication hypothesis from the 09-26 eval is untested: character 2 may
  be driven into accident deaths *because* it must differ from character 1's
  decision death. Worth testing by generating character 2 once with the
  anti-duplication block removed — independent of which model is in use.

## Unity files to update

- **config.py** ->
  - ModelNamesController -- model strings

**Porting note:** this is a single Inspector string change in `ModelNamesController`
(the generation model field). Do not port it until a run has actually been judged
good — the point of this version is to find out.
