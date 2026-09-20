# Unity file mapping

Which `game_state/` file corresponds to which Unity C# file(s).

## prompts.py
- Assets/Scripts/PromptsController.cs -- Init() string field assignments

## config.py
- CharacterController.cs -- 'temp' field (shared by TEMP_DIALOGUE/TEMP_ADDRESSING/TEMP_NARRATOR -- changing just one of these three constants has no independent Unity equivalent; verify all three still agree before treating this as a clean port)
- CharacterController.cs -- useQween0_6, useHuggingFaceProvider toggles
- CharacterGenerator.cs -- temperature, age Random.Range(25,65), gender assignment
- ModelNamesController -- model strings

## assembly.py
- CharacterController.cs -- SendRequestForCharacter, SendRequestForAdress
- CharacterGenerator.cs -- ExtractField

## game.py
- CharacterController.cs -- PersonController/CharacterEntry, DialogueEntry, GetPersonMapping, GetPersonNumberFor, FormatDialogueForCharacter, UpdateLatestDialoguesContext, LogDialogueEntry

## providers.py
- APIRequestHandler.cs -- SendOpenAIRequest
- InfoExtractorHandler.cs -- ExtractInfo

## Not tracked in game_state/, but also Unity-relevant

tools/simulator.py is outside game_state/ and so is not snapshotted, but its call-flow mirrors Unity: CharacterGenerator.cs (GenerateCharacter) and CharacterController.cs (ParsedText) -- the sequencing of generation calls and reply/addressing routing. If you change *when* addressing triggers, reply routing, or the generation sequence, check those Unity methods too, even though this tool won't flag it automatically.
