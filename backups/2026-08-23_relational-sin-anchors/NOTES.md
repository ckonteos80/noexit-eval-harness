# 2026-08-23_relational-sin-anchors

**Date:** 2026-08-23
**Previous version:** 2026-08-09_baseline

## State

Add explicit relational fields to character generation: each character now generates a named 'Who you loved' and 'Who you hated' during the Life call, required to be from different relation-categories between the two characters (anti-duplication). The Sin call is rewired to anchor the True reason for damnation on one of these two people instead of an abstract professional/systemic failing -- direct response to today's human eval feedback (both character-level, pair-level, and session-level evals flagged 'too much emphasis on line of work'). Also swapped MODEL_* from Qwen2.5-7B-Instruct to Qwen3-8B since the old model's only working HF provider (Together) stopped serving it.

## Changes from previous version

- Add explicit relational fields to character generation: each character now generates a named 'Who you loved' and 'Who you hated' during the Life call, required to be from different relation-categories between the two characters (anti-duplication). The Sin call is rewired to anchor the True reason for damnation on one of these two people instead of an abstract professional/systemic failing -- direct response to today's human eval feedback (both character-level, pair-level, and session-level evals flagged 'too much emphasis on line of work'). Also swapped MODEL_* from Qwen2.5-7B-Instruct to Qwen3-8B since the old model's only working HF provider (Together) stopped serving it.

(Edit this section with more detail if useful see DIFF.md for the exact diff.)

## Unity files to update

- **assembly.py** ->
  - CharacterController.cs -- SendRequestForCharacter, SendRequestForAdress
  - CharacterGenerator.cs -- ExtractField
- **config.py** ->
  - CharacterController.cs -- 'temp' field (shared by TEMP_DIALOGUE/TEMP_ADDRESSING/TEMP_NARRATOR -- changing just one of these three constants has no independent Unity equivalent; verify all three still agree before treating this as a clean port)
  - CharacterController.cs -- useQween0_6, useHuggingFaceProvider toggles
  - CharacterGenerator.cs -- temperature, age Random.Range(25,65), gender assignment
  - ModelNamesController -- model strings
- **game.py** ->
  - CharacterController.cs -- PersonController/CharacterEntry, DialogueEntry, GetPersonMapping, GetPersonNumberFor, FormatDialogueForCharacter, UpdateLatestDialoguesContext, LogDialogueEntry
- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments
