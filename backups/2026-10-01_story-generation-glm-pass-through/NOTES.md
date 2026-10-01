# 2026-10-01_story-generation-glm-pass-through

**Date:** 2026-10-01
**Previous version:** 2026-09-27_death-need-not-belong

## State

Story-form generation on GLM-5.3 at high effort; name from its own call; response used whole, with a sanity check replacing field parsing.

## Changes from previous version

Promoted from experiments 15-20. The design and the decisions behind it are in
`docs/PROMOTION_PLAN.md`; the evidence is in `experiments/` 14-20.

**Generation is now two calls and the response is not parsed.**

1. **A name call first.** `Qwen3-8B` @ 1.2 invents a full name from age and gender, and it is
   handed to the story prompt as a given. A story adopts a supplied name only 4-5 times in 10
   wherever the name sits in the prompt (experiments 18, 19), so the supplied value - not the
   prose - is what `{NAME}` uses downstream.
2. **The story call** on `zai-org/GLM-5.3` @ 1.1 with `reasoning_effort="high"`, replacing
   `Qwen3-235B` @ 0.95. The prompt asks for a 300-word life story answering five questions,
   replacing the nine labelled fields.
3. **The response is used whole.** No `ExtractField`, no header parsing, no assembled bio.
   `char.description` is the stripped response.

**What the evidence says this buys.** The secret arrives as a findable object in 10 of 10
(experiment 17) - a voicemail listened to seventeen times, a diary in the basement freezer
under the frozen peas, an unsent email - usually physically present at the moment of death.
Qwen gave 2 objects in 5 on the same inputs. That is the first output in the series that hands
the play a prop two characters can ask each other about.

**What it costs.** Nothing downstream can query a structured fact about a character; the run
record's nine per-character fields are empty from this version on. Deaths are narrow -
experiment 20 gave 4 of 10 suicides and 6 of 10 cardiovascular - and the name call collides
badly, nine of ten names beginning with E in experiment 19.

**The safety net changed.** `character_parse_complete` was the only test that a generation had
succeeded, and it is gone with the fields. `assembly.generation_is_usable` replaces it:
non-empty, 150-450 words, no surviving `<think>`, and at least 5 second-person markers. The
last threshold is set from data - one experiment 20 story came back entirely in the first
person with 19 "I" and zero "you", while every sound story scored 19-26. Checked before
shipping: it accepts 39 of the 40 stories from experiments 15, 17, 19 and 20, and rejects
exactly the broken one.

**Also removed:** `{NAME_ORIGIN}` and the `random.choice(NAME_ORIGINS)` draw. `game_state` had
been passing a naming tradition since before the standing rule of 2026-09-27; it no longer
does.

## What would show it worked

- A generated **pair** that reads as two different people. Untested since experiment 05 -
  every experiment since generates characters independently, and the anti-duplication block
  has never run against a story-shaped bio.
- **A dialogue session.** Everything measured so far is generation quality; the bio exists to
  feed the dialogue model and has never been tested in that role.
- Retries staying rare. More than about one in ten means the sanity check is catching a real
  regression rather than the known 1-in-10 first-person break.

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
- **providers.py** ->
  - APIRequestHandler.cs -- SendOpenAIRequest
  - InfoExtractorHandler.cs -- ExtractInfo
