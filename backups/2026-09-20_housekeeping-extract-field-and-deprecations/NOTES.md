# 2026-09-20_housekeeping-extract-field-and-deprecations

**Date:** 2026-09-20
**Previous version:** 2026-09-20_addressing-drop-character-3

## State

Housekeeping. **No prompt was touched and no behaviour changed**, so this version is
directly comparable with the previous one for character-generation evaluation.
Raised by a line-by-line audit of every file, not by anything seen in a run.

## Changes

### `assembly.py` — `extract_field` ends at a heading, not at any `**`

It returned everything up to the next `**` *anywhere*, so a value containing inline
bold was silently truncated: `"teacher **and** coach"` came back as `"teacher"`.
Headings are always written on their own line, so the end marker is now the next
`**` that **starts a line**:

```python
_HEADING_START = re.compile(r"^\*\*", re.M)
```

**Verified against the whole run history**: 3,091 extractions replayed across every
recorded generation response through both the old and new implementations —
identical on all of them. No response on record contains mid-line `**`, so this is
defensive; nothing about how existing runs parse changes.

### `assembly.py` — `assemble_bio` docstring corrected

It claimed "Section order follows CHARACTER_FIELDS". It does not: the relationship
precedes the death as it does there, but the **trait is shown before the refusal**,
the reverse of generation order. The claim was wrong in a file whose own comments
say ordering is load-bearing, which is the dangerous kind of wrong. The docstring
now describes the real order and notes that changing it changes the dialogue system
prompt, since the bio is what gets substituted in.

### `game.py` — `datetime.utcnow()` replaced

Deprecated. Both call sites go through a helper that deliberately keeps the
**naive, offset-free** shape:

```python
datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
```

The obvious swap to `datetime.now(timezone.utc).isoformat()` would append `+00:00`
and mix two timestamp shapes in one column — `run_viewer` sorts these as plain
strings via `localeCompare`, and all 17 stored runs use the naive form.

### `providers.py` — unused `field` import dropped

### `config.py` — trailing newline added

## Related change outside `game_state/`

`tools/simulator.py` now passes `config.MAX_TOKENS_GENERATION` instead of a
hardcoded `0`. The constant existed but nothing read it, so it looked like a knob
and was not one. Same value, so no behavioural change — the knob is simply live now.

## Found during the audit, deliberately not fixed

**Mojibake in one historical run.** `2026-08-09_142230ec` contains `â€"` — the
UTF-8 bytes of an em-dash (`E2 80 94`) decoded as cp1252 — in four generation
responses and in both saved bios. Where it lands on a `Reason for Damnation — True`
heading, `extract_field` cannot match and returns `None`, which would have driven a
parse retry.

Confined to that one run, the oldest in the history, served by
`Qwen/Qwen2.5-7B-Instruct-Turbo` — the model whose provider was dropped on
2026-08-23. **All 16 later runs are clean.** A defensive
`response.encoding = "utf-8"` in `providers.py` would guard against a recurrence,
but the cause cannot be reproduced with the current provider and `providers.py`
mirrors `APIRequestHandler.cs`, so speculative changes there are not free. Recorded
rather than patched.

## Unity files to update

- **assembly.py** ->
  - CharacterGenerator.cs -- `ExtractField`. **Port the line-anchored end marker**:
    stop at the next `**` that begins a line, not the next `**` found. Without it the
    harness and Unity parse differently for any value containing inline bold.
- **game.py**, **providers.py**, **config.py** -> no Unity-visible change
  (timestamp helper, an unused import, a trailing newline).
