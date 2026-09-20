# 2026-09-13_experiment-no-examples

**Date:** 2026-09-13
**Previous version:** 2026-09-13_pronoun-rule-scoped-to-life-characters

## State

**This is an experiment, not a considered improvement.** Every concrete example — positive and negative — has been stripped from the three character-generation prompts. All rules survive, stated abstractly. If the next run is worse, restore the previous version:

```bash
python restore_version.py pronoun-rule-scoped-to-life-characters
```

## The hypothesis

Examples were suspected of narrowing the output rather than widening it. Two were caught doing it outright:

| Example text | Where it lived | Leaked into |
|---|---|---|
| *"You told **Sanne** it was impossible"* | the pronoun rule | 3 of the last 4 runs — as Jasper's sister, Klaus's partner, Jasper's partner |
| *"If they **needed to be needed**…"* | anti-duplication, "different kind of hold" | Marloes's true reason, verbatim: *"your need to be needed"* |

The Sanne loop was self-inflicted: the name appeared organically in one run, was then adopted **as the worked example**, and has appeared in both runs since.

The Cause of Death field showed the same effect structurally rather than verbatim — 4 of its 7 examples were medical, and four consecutive characters died medically. The anti-duplication block reused the same vocabulary, so character 2 was picking a different item off an identical menu rather than choosing from a space, which is why the deaths landed adjacent (took the pills / refused the pills).

## What was removed

**Positive (19):** the truth-would-come-out demonstration; the Sanne pronoun example; "Insurance claims adjuster" / "Keeper of the Ledger"; the relation list on Who you loved; the seven-item death list; the "condition you let run because admitting to it meant asking someone for help" example; the lived-alone/house-full contrast; the aims list on the True reason; the distortion-types list on Self-told; the generous-in-public trait example; the eight-option want list; the two banned want phrasings quoted in full; and in the anti-duplication block — the driver/healthcare demonstration, the seven-item death list, the drank-themselves-to-death example, the relation-category list, the needed-to-be-needed example, and the fourteen sin categories.

**Negative (4):** "no fantasy, no mysticism, no atmospheric worldbuilding"; "Hell is not a place of fire or devils"; the accident instances ("another vehicle, water on the road, equipment that failed, a stranger who happened to be there"); and the banned death categories ("No crashes or collisions of any kind. No falls, no fires, no machinery, no weather, no violence done to you by someone else").

**2,479 characters removed.** All 24 rules verified present afterwards, along with field order, the format block, and all eight anti-duplication bullets.

## Scope

Only the three character-generation prompts. The narrator, dialogue, addressing and info-extraction prompts keep their examples — a chars-only run never invokes them, so stripping those would add no signal to this test while risking unrelated regressions. They can be done separately if this succeeds.

## What is genuinely at risk

**The negative examples were the ones that worked.** The accident ban took deaths from five-in-six traffic accidents to zero in a single version, and it did so with a concrete list: *no crashes, no falls, no fires, no machinery, no weather.* That list is now gone, and only the abstract test remains ("if something outside your control had to go a particular way at a particular moment"). **If accidents return, that is the finding, and the fix is to restore the ban list while leaving the positive examples deleted** — a middle position this experiment deliberately skips in order to get a clean reading.

We also have prior evidence that removal alone does not create variety: the trait field's three worked examples were deleted in v3 because "Quietly furious" was being copied, and the model then produced *quietly controlling*, *quietly insistent* and *quietly stubborn* across the next four characters. The vacuum was filled by the prior, not by invention.

## What to look for in the first run

1. **Do accidents come back?** The single most likely regression.
2. **Does the medical monoculture break?** Four consecutive characters have died of deliberate health self-neglect used as leverage.
3. **Do the leaked tokens disappear** — no Sanne, no "need to be needed"?
4. **Does anything get vaguer?** The examples may have been carrying meaning the abstract rules do not, particularly on Occupation (which had the tightest positive/negative pair) and on the want field.
5. **Does the pair improve at all?** Unlikely from this change alone, but the anti-duplication block lost the most specificity of the three prompts.

## Files changed

`game_state/prompts.py` only — all three character-generation fields. No code, schema, or structural change.

## Unity files to update

- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments (three fields changed). **Do not port until the experiment is judged** — this may be reverted.
