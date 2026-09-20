# 2026-09-12_deaths-by-decision-and-no-pronouns

**Date:** 2026-09-12
**Previous version:** 2026-09-12_one-relationship-and-a-death-that-belongs-to-it

## State

Two fixes, both straight from human eval on `2026-09-12_788601a3`. Prompt-only; no code, schema or structural change.

## Fix 1 — accidental deaths banned

**Human eval:** *"Again the cause of death is accidental, we want to avoid these, need to be from concious desisions."*

Five of the last six generated deaths were traffic accidents. The previous version's wording caused it, in three separate places:

| Old wording | What it invited |
|---|---|
| "a thing you took, **drove**, started" | vehicle deaths, named in the example list |
| "or **on the way to or from them**" | dying while driving to the person — both characters did exactly this |
| "It can still be **ordinary, avoidable and stupid**" | accidents, explicitly licensed |

All three are removed. In their place, a test that is actually decidable:

> "The test is whether chance had to cooperate: if something else had to be in the wrong place at the wrong moment — another vehicle, water on the road, equipment that failed, a stranger who happened to be there — then it is an accident, and it is wrong no matter how recklessly you were behaving when it happened. **No crashes or collisions of any kind. No falls, no fires, no machinery, no weather, no violence done to you by someone else.**"

And a positive space, so the model is not left guessing: what you swallowed or drank, treatment refused, a diagnosis not acted on, pills you kept taking, a person you provoked knowing what they were capable of, a place you would not leave, a condition you let run because admitting it meant asking for help.

Guarded against the obvious over-correction with: *"You did not intend to die. You did intend to do the thing that killed you, and you knew enough to know better."* Without that line, banning accidents pushes everything toward suicide.

The connection rule from the previous version survives but no longer offers travel as a route: the death now happens "because of them, in front of them, as a direct result of something you decided to do about them, or in the hours after something passed between you."

## Fix 2 — no third-person pronouns anywhere

**Human eval:** *"In this sentence: 'You drove to her apartment' we need to avoid the 'her' or any pronouns might cause confusion later."*

The bio is fed into the dialogue system prompt and the character speaks from it in a room containing two other people. Any "her" or "him" in the bio is ambiguous at exactly the moment it matters — it reads as pointing at somebody present.

Added to the voice section, so it governs every field:

> "Name every other person every time you mention them, in every field. Never write he, she, him, her, they or them about anybody — write the name instead, even where it repeats and even where it reads a little stiffly. […] The only pronoun in these fields is 'you,' meaning the character."

## Consistency repair

The anti-duplication block still listed "vehicle, violence, illness, accident…" as the death categories and used two car crashes as its worked example — both now forbidden. Rewritten around the decision-death space, with a new worked example that still applies: *"two people who both drank themselves to death died the same death, whatever they were drinking."*

## Files changed

`game_state/prompts.py` only — `characterFullUserPrompt` and `characterFullAntiDuplicationBlock`. No code, no schema, no Unity structural change.

## Risk being carried

Banning accidents **narrows the death space**, and narrowing the space is what has driven every duplication failure so far. The previous version narrowed it once (the death must belong to the relationship) and both characters landed on the same death. This narrows it again.

The anti-duplication bullet was updated to police the new space, but that is the same instruction-based lever that has now failed three runs running. If both deaths collide again, it is further evidence for the conclusion already recorded in the previous version's notes: instruction-based anti-duplication has reached its limit, and the pair needs composing in one call rather than sequentially.

That change was scoped in discussion — separator-based splitting (`=== CHARACTER 2 ===`), then the existing per-character parser run on each half, with `extract_field` untouched — and deliberately not implemented yet.

## What to look for in the first run

Are both deaths genuinely decisions rather than accidents; are they *different* decisions; has anything drifted toward suicide; do any third-person pronouns survive in any field; and does the prose still read acceptably now that names repeat instead of pronouns.

## Unity files to update

- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments (two fields changed, none added or removed)
