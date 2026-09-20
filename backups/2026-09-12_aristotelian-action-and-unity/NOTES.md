# 2026-09-12_aristotelian-action-and-unity

**Date:** 2026-09-12
**Previous version:** 2026-08-29_stanislavski-given-circumstances

## State

Character generation, second pass. Adds concepts from Aristotle's *Poetics* (researched into `aristotle-poetics.md`) alongside two further Stanislavski ideas, and fixes all five defects observed in the previous version's single run.

The through-line of the previous version was *a fact earns its place by being usable rather than by reading well*. This version extends that in two directions: **a fact must also be load-bearing** (Aristotle's unity — anything removable without consequence is superfluous), and **a trait must be demonstrated by an action** (Aristotle's plot-before-character — a quality nothing shows is a label, not a person).

Dialogue prompts were again deliberately left untouched, so the effect on character generation stays attributable. Dialogue is the next version.

## Changes from previous version

### The nine edits

| # | Field | Change | Source concept |
|---|---|---|---|
| 1a | `characterSetupSystemPrompt` | Third governing rule: a fact must be **load-bearing** — if deleting it would change nothing else, it doesn't belong. | Aristotle, unity of action |
| 1b | `characterSetupSystemPrompt` | Fourth rule: **everyone must be plausible**, not just the lead. Any person mentioned acts from their own situation, not from what the story needs. Placed in the shared setup prompt so it also governs the sin call's invented supporting cast. | Aristotle, necessity & probability; Stanislavski, the Magic If |
| 2 | Life → Cause of Death | Widened to include acts of **commission**, with a stated preference for the active kind. | — (defect fix) |
| 3 | Life → Who you loved / hated | The other person's want must be plausible for them: "a want that exists only to explain how you felt about them is not a want." | Aristotle, necessity & probability |
| 4 | Life → prose paragraph | Removed the ordered topic menu; added "choose the facts that matter for *this* life," "two different lives should not produce two paragraphs built the same way," and **end on a fact, not a resonant closing line**. Word limit hardened from "around 80–100" to "no longer than 110." | Aristotle, magnitude |
| 5 | `characterLifeAntiDuplicationBlock` | Added `{OTHER_NAME}`; death must differ in **kind of causation** (act vs omission), not only category; **no name reuse** across the pair or their supporting casts, with an explicit exception for genuine family. | — (defect fix) |
| 6 | `characterNameAntiDuplicationBlock` | **New prompt string.** Character 2's name call now sees character 1's name and must differ in first name, surname, near-variants, and naming register. | — (defect fix) |
| 7 | Sin → True reason | The act was aimed at something; write it so the aim is visible and **the result ran against it**. | Aristotle, peripeteia |
| 8 | Sin → What you refuse to admit | State it flatly, no imagery or cadence; and it must be **reasoned** — someone holding only the facts above could work their way to it. | Stanislavski, Inner Motive Forces (the field was producing feeling without mind) |
| 9 | Stance → Defining personality trait | Removed the three worked examples entirely (the model was copying them verbatim). Trait must be **demonstrated** by the life, death or sin. Contradiction allowed only if **reliable**. | Aristotle, plot before character; "consistently inconsistent" |

### Plumbing

- **`assembly.py`** — `assemble_name_prompts(gender, other_name=None)` now appends the name anti-duplication block, matching the conditional-block pattern already used by `assemble_life_prompts`. `assemble_life_prompts` accepts `other_name` and interpolates `{OTHER_NAME}`; its anti-dup guard now requires all five `other_*` args.
- **`simulator.py`** — two lines in `generate_character()` passing `other_char.name` into both calls for character 2. **Not captured in `DIFF.md`**: `simulator.py` lives outside `game_state/` and is not tracked by `save_version.py` (see `UNTRACKED_UNITY_NOTE`). Recorded here by hand.

No new character fields, so the parse contract, `Character` dataclass, run JSON schema and `run_viewer.html` are all untouched.

### Deliberately not adopted

- **Hamartia.** Aristotle's tragic figure errs rather than sins — a misjudgement, not a vice — and he wants a protagonist neither virtuous nor villainous. **Rejected by decision:** the setup prompt explicitly invokes Sartre, whose damned are genuinely culpable, and the sin category list is vice-based throughout. Sins stay Sartrean. Do not re-propose without revisiting that decision directly.
- **Catharsis as a design target, and any requirement for resolution.** NoExit's premise is that nothing resolves; importing Aristotle's demand for an end would break it.
- **Emotion Memory** (carried over from last version's rejection) — one step from re-authorising the poetic prose two versions have now worked to remove.

### Held for the dialogue version

Aristotle's *character revealed through choice* and Stanislavski's *Units and Objectives* converge on the same change: every reply should enact a decision rather than report a state. Plus Communion, and the conditions under which the guard on the sin can break (anagnorisis). None of these belong in the generation chain.

## Still open

- **Cross-run name repetition.** Character 1 was named Daniel Reeves in two consecutive runs. Edit 6 prevents collisions *within* a pair but the name call has no memory across runs, so this is unfixed. The fix — feeding recent runs' names in as exclusions — is a larger change touching `simulator.py` and the run store.
- **The prose template** is addressed by edit 4 alone. If two paragraphs still come back the same shape, the next lever is feeding character 1's prose body into the anti-duplication block, which was deliberately not done this round (token cost, and risk of the model copying details rather than avoiding them).

## What to look for in the first run

In priority order: do the two prose paragraphs still share a shape; are both deaths still "ignored a warning"; is the trait actually evidenced by the life; is the refusal written plainly; is any name reused across the pair.

## Unity files to update

- **assembly.py** ->
  - CharacterController.cs -- SendRequestForCharacter, SendRequestForAdress
  - CharacterGenerator.cs -- ExtractField
- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments (note: **one new field**, `characterNameAntiDuplicationBlock`)
- **simulator.py** (untracked by the diff tool) ->
  - CharacterGenerator.cs -- GenerateCharacter, where Character 2's generation receives Character 1's data
