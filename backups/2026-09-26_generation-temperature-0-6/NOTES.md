# 2026-09-26_generation-temperature-0-6

**Date:** 2026-09-26
**Previous version:** 2026-09-26_generation-on-gpt-oss-120b

## State

TEMP_GENERATION lowered 0.95 to 0.6 on gpt-oss-120b; model and prompts unchanged.

## Changes from previous version

`TEMP_GENERATION`: **0.95 -> 0.6**. That is the whole change. The model stays
`openai/gpt-oss-120b`, no prompt moved, and `TEMP_DIALOGUE` / `TEMP_ADDRESSING` /
`TEMP_NARRATOR` stay at 0.5.

Temperature had been constant at 0.95 across every version on record, so this is the
first time it has moved. It moves alone, deliberately, for the same reason the model
moved alone in the previous version.

### The prediction, recorded before the run

This is a discriminating test, not an expected fix, and the two effects in play pull
in opposite directions:

- **High temperature degrades long reasoning chains.** A bad token early in a
  2,000-token trace does not produce one odd phrase, it sends the rest of the
  reasoning down a path that then gets rationalised. Lowering temperature should
  therefore improve **rule-following and coherence** — the death corridor, the
  dangling "the baby" reference, the 24-year gap between grievance and revenge.
- **Low temperature increases determinism.** A model sampling closer to the mode
  reaches for the same high-probability sentence frames more often. Lowering
  temperature should therefore make **duplication worse**, and duplication was the
  headline failure of the previous version — six sentence frames appeared verbatim
  in both characters, and both committed the identical sin of forging a document to
  destroy the person they loved.

**Predicted outcome: deaths get more rule-abiding, duplication gets worse.**

If both improve instead, 0.95 was simply wrong for a reasoning model and the
previous version's verdict should be re-read as a sampling artefact rather than a
judgement on gpt-oss-120b. If both get worse, temperature is not the lever and the
model should be reverted.

An honest caveat about the number: 0.6 comes from Qwen's published guidance for
*their* Thinking variants, not from anything gpt-oss-specific. The direction is the
hypothesis; the exact value is a reasonable guess.

### What this version cannot tell us

`top_p` and `top_k` still cannot be forwarded by the proxy, so this is a
temperature-only intervention. Reasoning-model guidance normally pairs a lower
temperature with `top_p` around 0.95, so even the Qwen recipe is only half applied.

### Deliberately not done

- **No prompt change.** The death corridor is still described only by its two walls.
  The previous eval concluded the escalation toward homicide is driven by the prompt
  rather than the model, since two unrelated models walked the same road — but
  fixing that is a prompt change and would confound this test.
- **The anti-duplication block is untouched.** The previous eval raised the
  possibility that a reasoning model reads character 1's bio as a *specification*
  rather than a warning, which would make the block actively harmful. That is the
  next thing to test and it is deliberately not bundled here.

### Rollback

- `python tools/restore_version.py generation-on-gpt-oss-120b` — back to 0.95.
- `python tools/restore_version.py tolerant-field-extraction` — back to the
  Qwen 235B with every parser fix intact. The parser work is model-agnostic.

### Carried in, still open

- The HF router 504s at roughly 120s, which is why `Qwen3-235B-A22B-Thinking-2507`
  is unreachable without streaming.
- The proxy masks every upstream status as HTTP 500, so `call_proxy`'s 503/504 retry
  has never fired — `cold_start` is false on all 288 calls on record.
- `max_tokens` is still dropped by the proxy.
- The 110-word prose cap has never been a real constraint.

## Unity files to update

- **config.py** ->
  - CharacterController.cs -- 'temp' field (shared by TEMP_DIALOGUE/TEMP_ADDRESSING/TEMP_NARRATOR -- changing just one of these three constants has no independent Unity equivalent; verify all three still agree before treating this as a clean port)
  - CharacterController.cs -- useQween0_6, useHuggingFaceProvider toggles
  - CharacterGenerator.cs -- temperature, age Random.Range(25,65), gender assignment
  - ModelNamesController -- model strings

**Porting note:** only `CharacterGenerator.cs`'s `temperature` field is affected —
generation temperature is separate from the shared `CharacterController.temp` that
drives dialogue, addressing and the narrator, and none of those moved. Do not port
until a run has been judged good.
