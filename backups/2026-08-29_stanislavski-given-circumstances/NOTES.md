# 2026-08-29_stanislavski-given-circumstances

**Date:** 2026-08-29
**Previous version:** 2026-08-23_relational-sin-anchors

## State

Character generation is now grounded in concepts from Stanislavski's *An Actor Prepares* (researched into `stanislavski-an-actor-prepares.md` at project root). The through-line of this version: **a generated fact earns its place by being usable in the room, not by reading well.** Dialogue prompts were deliberately left alone this round so the effect on character generation could be evaluated in isolation.

## Changes from previous version

### Character generation (the intended work of this version)

Six edits to `prompts.py`, each traceable to a named concept. See `DIFF.md` for exact before/after.

| # | Field | Change | Stanislavski concept |
|---|---|---|---|
| 1 | `characterSetupSystemPrompt` | Added two governing rules for all four generation calls: every fact must be **usable** (sayable aloud, askable about, catchable as a lie) and must be **named** (no gesturing at an unstated thing). | Action; Faith and a Sense of Truth |
| 2 | `characterLifeUserPrompt` — Cause of Death | Must follow from something the character did, chose, or avoided. Explicitly not a random accident, not something a stranger did to them. | The Unbroken Line |
| 3 | `characterLifeUserPrompt` — Who you loved / hated | Each person now gets a second clause stating what **they themselves** wanted, independent of the protagonist. | Communion |
| 4 | `characterLifeUserPrompt` — closing prose | Rewritten from "voice, mannerism, the texture of the days" to facts another person could ask about, with an explicit ban on sensory writing, atmosphere, imagery and metaphor. **Largest single change in this version.** | Given Circumstances |
| 5 | `characterSinUserPrompt` — Self-told | The distortion must be checkable: a reader must be able to point at the exact established fact it bends, or it is not a distortion. | Inner Motive Forces; The Unbroken Line |
| 6 | `characterStanceUserPrompt` — What you want | Must be a strategy for protecting what the character refuses to admit, not an unconnected wish. | The Super-Objective |

**Deliberately not adopted:** Emotion Memory (one step from re-authorising the poetic prose this version removes); the four actor-craft chapters (Concentration, Relaxation, Inner Creative State, Threshold of the Subconscious — no text analogue).

**Held for a later version:** Units and Objectives, Adaptation, Communion-in-scene, and the Magic If as a deflection test. All are real gaps, but they belong to the dialogue prompt.

### Carried in from earlier work (not part of this version's intent)

These were made after `relational-sin-anchors` was snapshotted and never versioned on their own, so they land here. They are unrelated to the Stanislavski work:

- **`config.py`** — `MODEL_GENERATION` swapped from `Qwen/Qwen3-8B` to `Qwen/Qwen3-235B-A22B-Instruct-2507`. Generation runs once per session, so cost and latency matter less; chosen to address vague character-gen content flagged in human eval. `MODEL_DIALOGUE` / `MODEL_ADDRESSING` remain `Qwen3-8B`.
- **`assembly.py`** — `assemble_dialogue_system_prompt()` gained a `name` parameter.
- **`prompts.py` — `dialogueSystemPromptTemplate`** — added "Your name is {NAME}." (characters previously did not know their own name), and split the response rules into answer-plain-facts-directly (rule 5) versus guard-the-loaded-material (rule 6).

## Runs generated under this version

- `runs/2026-08-29_8cc397da Qwen3-235B-A22B-Instruct-2507.json` — chars-only pair (Daniel Reeves / Linda Cruz). **Note:** this run was auto-tagged `2026-08-23_relational-sin-anchors` at save time because this snapshot had not been taken yet; the tag was corrected by hand, and `meta.version_tag_corrected` records that. Verified against the run's own stored prompts — all six edits above are present in its call text.

## Known issues observed in the first run under this version

Recorded here so the next version has a starting point:

1. **Name generation is the weakest link.** Character 1 was named Daniel Reeves in this run *and* in the run of the 28th. Within this run, character 2's hated man is named Daniel Poole — colliding with character 1's first name. The same class of collision was flagged by human eval on the 28th (Daniel's sister Claire / Claire Bennett's son Daniel). The anti-duplication blocks cover occupation, cause of death and relation-category, but nothing constrains names — not against the other character, not against that character's own supporting cast.
2. **The factual prose has hardened into a template.** Both paragraphs follow: where you lived → daily routine → "the week before you died, you..." → the final moment → a short flat closing line. New in this version; a side effect of change #4.
3. **Cause of death is narrowing toward omission.** Both deaths are "ignored a warning" (lockout-tagout; compression sleeves and a postponed doctor). The category filter passed them as occupational vs illness, but the underlying move is identical. Change #2 may need widening to invite acts of commission.
4. **The old poetic register survived precisely where it was not addressed** — the Life paragraph is clean, but "what you refuse to admit" still writes mood. Suggests the remaining fields need the same explicit treatment rather than a general appeal to restraint.
5. **`characterStanceUserPrompt`'s example list is being copied verbatim.** Character 1's trait came back as "Quietly furious," lifted straight from the prompt's own examples, and it does not fit the character.

## Unity files to update

- **assembly.py** ->
  - CharacterController.cs -- SendRequestForCharacter, SendRequestForAdress
  - CharacterGenerator.cs -- ExtractField
- **config.py** ->
  - CharacterController.cs -- 'temp' field (shared by TEMP_DIALOGUE/TEMP_ADDRESSING/TEMP_NARRATOR -- changing just one of these three constants has no independent Unity equivalent; verify all three still agree before treating this as a clean port)
  - CharacterController.cs -- useQween0_6, useHuggingFaceProvider toggles
  - CharacterGenerator.cs -- temperature, age Random.Range(25,65), gender assignment
  - ModelNamesController -- model strings
- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments
