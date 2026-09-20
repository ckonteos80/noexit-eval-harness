# 2026-09-20_addressing-drop-character-3

**Date:** 2026-09-20
**Previous version:** 2026-09-13_experiment-no-examples

## State

Addressing only. No character-generation prompt was touched, so this version is
directly comparable with the one before it for character-gen evaluation purposes.

## What was wrong

`adressingSystemPromptActions` offered four answers -- 0, 1, 2 and 3 -- but
`simulator._run_addressing` only accepted 0, 1 and 2. A "3" reply was therefore
treated as malformed: retried three times, then discarded in favour of the
fallback "0" (both characters reply).

This actually happened. In run `2026-08-09_f225d3f2`, turn 5:

```
attempt 1  reply='3'
attempt 2  reply='3'
attempt 3  reply='3'
all attempts invalid, falling back to 0
```

Four API calls to reach an answer the model had given correctly on the first
try. The player was addressing the valet and got both characters instead.

There was also a dead branch downstream -- `run_player_turn` carried a comment
about "3" not being mapped, but `_run_addressing` could never return it.

## The decision

Drop 3 rather than wire it up. **The valet shows the player in and leaves; the
departure is final** (see `narratorSystemPrompt`: "not returning, not going
elsewhere, simply done"). He is not present in the room and so is not
addressable. Offering him as a target contradicts the fiction.

## Changes

**`game_state/prompts.py` -- `adressingSystemPromptActions`**

- Removed: `- If the user message addresses character 3, reply with "3".`
- Added: "Reply with exactly one of those digits and nothing else", making the
  contract explicit now that the parser enforces it strictly.

**`tools/simulator.py` (not snapshotted -- outside game_state/)**

`_run_addressing` now validates instead of extracting:

```python
choice = reply.strip()
if choice in ("0", "1", "2"):
    return choice
```

The previous code scanned for any of "0"/"1"/"2" *anywhere* in the reply and
returned the lowest one present. Its comment claimed "first matching digit
wins", which is not what iterating the tuple does: a reply of `"2, not 0"`
silently became `"0"`, and `"Character 1"` became `"1"`. Under a
one-digit contract those are malformed and should be retried, not resolved.

The dead "3" comment and the stale `"0"/"1"/"2"/"3"` docstring were removed.

## Verification

Replayed all 30 addressing replies ever recorded across the run history through
both the old and new parsers: **identical results on every one**, because every
real reply has been a single digit with at most surrounding whitespace. This is
a behaviour change only for malformed replies, which have not occurred yet.

Synthetic cases confirmed: `"2"`, `"\n\n0"` and `"  1  "` parse; `"3"`, `""`,
`"2, not 0"` and `"Character 1"` are now rejected and retried.

## Note for the Unity port

The removed comment was the only record of Unity's digit-selection behaviour, and
it could not be verified against the C#. If `CharacterController.cs` really does
scan a reply for the first digit it finds, it now differs from the harness on
malformed replies. Worth checking when porting; the prompt change itself is a
straight deletion of one line.

## Unity files to update

- **prompts.py** ->
  - Assets/Scripts/PromptsController.cs -- Init() string field assignments (one field changed)
- **simulator.py** (untracked by the diff tool) ->
  - CharacterController.cs -- ParsedText, the addressing-reply parse
