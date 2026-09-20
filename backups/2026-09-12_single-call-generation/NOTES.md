# 2026-09-12_single-call-generation

**Date:** 2026-09-12
**Previous version:** 2026-09-12_aristotelian-action-and-unity

## State

A structural change rather than a content one. Character generation ran **four calls per character, eight per session** (name → life → sin → stance) since the project began. It now runs **one call per character, two per session**.

Almost no prompt *guidance* changed: all nine rules from the previous version carry over close to verbatim. What changed is the shape of the request. Dialogue prompts remain untouched, as in the previous two versions.

## Why

Measured on `2026-09-12_a5e36b0f`, the last run under the old chain: **9,737 tokens, 22.1s, of which 8,384 (86%) were prompt** — because every call re-sent the setup system prompt plus everything generated so far.

Three defects traced directly to the four-call shape:

1. **The name call saw nothing about the person.** 879 prompt tokens across both characters to produce 7 completion tokens, with gender as its only input. With no character to anchor to, the model fell back on its prior: *Daniel Reeves* was character 1 in **three consecutive runs**, and the supporting names *Mark* and *Poole* both recurred from the previous run.
2. **The stance call never received who you loved or hated.** The trait and the want — the two fields that actually drive behaviour in the room — were written blind to the character's relationships.
3. **Anti-duplication was four separate blocks**, each comparing a single dimension. Pair-level failures fell between them: both characters in the last run died in car crashes, and that passed every individual check.

## The design decision that makes this work

Merging does **not** mean the model writes the fields simultaneously. Generation is autoregressive, so **the order of the format block reproduces the conditioning the separate calls used to provide**. The Self-told field still sees the life facts because they are already written above it in the same response; the trait still sees the sin.

The format block preserves the old chain's order exactly:

```
Name → Occupation → Cause of Death → Who you loved → Who you hated → Life →
Reason for Damnation (True) → Reason for Damnation (Self-told) →
What you refuse to admit → Defining personality trait → What you want
```

`assembly.CHARACTER_FIELDS` is the single source of truth for these headings and their order, and a test asserts it matches the prompt's format block. **Do not reorder either without the other.**

What is genuinely lost is the hard boundary between calls — but that boundary was not preventing much: Maya's prose contradicted her own Cause of Death, and both came from the *same* call. It is replaced with explicit cross-field constraints rather than assumed.

## Changes

### `config.py`
- **`NAME_ORIGINS`** — 30 naming traditions, one drawn at random per character and interpolated into the prompt. This is the real fix for cross-run name repetition: instructing the model to vary names failed for three versions. Randomising the *input* breaks the prior deterministically. Uses the same pattern as `AGE_RANGE` (`random.randint`), so it ports to Unity's existing `Random.Range` usage.

### `prompts.py` — 18 prompt fields down to 11
- **Added** `characterFullUserPrompt` (all eleven field instructions plus one format block) and `characterFullAntiDuplicationBlock` (the four old blocks merged, showing character 1's *complete* bio rather than one dimension at a time).
- **Deleted nine**: `characterNameUserPrompt`, `characterNameGenderSuffix`, `characterNameAntiDuplicationBlock`, and the `Life`/`Sin`/`Stance` user prompts and anti-duplication blocks.
- `characterSetupSystemPrompt` unchanged, still the system prompt for the single call.

**Four new rules**, each targeting a specific observed failure:

| New rule | Fixes |
|---|---|
| The Life paragraph must end at *the death already written in Cause of Death* — same death, same means, same place | Maya's prose invented a second, incompatible death |
| Nothing in Who you loved / hated may describe events after the death | Maya's hated person "called you the next day" when Maya had died that night |
| The trait must be written as words only — no asterisks, quotes or emphasis | The trait stored as `*In control calm*`, markdown leaking into the field value |
| The refusal must go underneath the act, not restate it — "if it could be swapped with the True reason without anyone noticing, it is not the refusal" | Maya's refusal was her sin again at greater length |

The death-category anti-duplication rule was also made emphatic — *"two car crashes are two vehicle deaths even if one ran a red light and the other hydroplaned"* — and the causation bullet separated from it. The previous version added causation directly beneath category and the model appears to have satisfied the newer rule while dropping the older one.

### `assembly.py`
Ten functions replaced by three: `assemble_character_prompts()`, `parse_character_response()`, `character_parse_complete()`, driven by the `CHARACTER_FIELDS` map. `extract_field()` needed **no change** — the field labels are identical, and it already reads to the next `**` marker. `assemble_bio()` and everything on the dialogue side are untouched.

### `simulator.py` — **not captured in DIFF.md**
`generate_character()` goes from four call sites to one. Picks `name_origin` via `random.choice`, assembles, one `_call_with_parse_retry`, unpacks eleven fields. Character 2 passes `other_char.description` (the finished bio) instead of four separate fields. Logged as `call_type="character"`.

`simulator.py` sits outside `game_state/` and is not tracked by `save_version.py` (see `UNTRACKED_UNITY_NOTE`), so this is recorded here by hand.

### `run_viewer.html`
`'character'` added to `ROW_CATS`, the char-level label list, and the pill CSS. **The old four types are retained** so runs recorded before this version still render correctly.

## Not changed

`game.py` — the `Character` dataclass keeps exactly the same fields, so the run JSON schema, `store.py`, `assemble_bio()`'s output and the viewer's Character Gen view are all unaffected. No dialogue, addressing, narrator or info-extraction prompt was touched.

## Expected effect

~3,500 tokens per session against 9,737, and 2 calls against 8. Verified statically only — no run has been generated under this version yet.

## Risks being carried

- **Late-field quality.** Trait and want are now written last in a single ~700-token response, and they were already the weakest fields. This is the first thing to check.
- **The self-told mechanism.** Autoregressive ordering should preserve it, but the model can now in principle author convenient life facts knowing where it is heading. Watch whether the distortion still bends a fact that stands on its own.
- **Parse failure is now all-or-nothing.** One missing field retries the whole response. Mitigating evidence: zero parse retries across all 24 calls of every type in every run ever recorded, and `MAX_TOKENS_GENERATION = 0` with `finish_reason: "stop"` throughout, so truncation is not a concern.
- **Unity port.** This is the largest parity break the project has made — `CharacterGenerator.GenerateCharacter` goes from four calls to one, and `PromptsController` loses nine fields and gains two.

## What to look for in the first run

In priority order: are the names finally different from previous runs; does the prose still contradict the Cause of Death; is the self-told still bending a real fact; have trait and want degraded now that they come last; do the two deaths still share a category.

## Still open

- **Dialogue** is the next substantive version — character-revealed-through-choice (Aristotle) and Units and Objectives (Stanislavski) converge on the same change, plus Communion and the conditions under which the guard on the sin can break.
- **`character-eval-guide.md`** still needs the removability test, "consistently inconsistent", and the three calibration fixes from the human/AI comparison of the 28th.
- If names still repeat despite `NAME_ORIGINS`, the next lever is a short discarded preamble field letting the model sketch the person before naming them.

## Unity files to update

- **config.py** ->
  - CharacterGenerator.cs -- add the NAME_ORIGINS list and a Random.Range pick alongside the existing age randomisation
  - ModelNamesController -- model strings (unchanged this version)
- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments. **Nine fields removed, two added.**
- **assembly.py** ->
  - CharacterGenerator.cs -- ExtractField (unchanged), and the parse/assemble helpers, which collapse to one each
- **simulator.py** (untracked by the diff tool) ->
  - CharacterGenerator.cs -- GenerateCharacter: four sequential requests become one; Character 2 passes Character 1's assembled bio rather than individual fields
