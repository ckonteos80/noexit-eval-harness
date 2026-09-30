---
description: Take a change into game_state, from an experiment or stated directly, and summarise it for confirmation before editing
argument-hint: <experiment NN> | <the change you want>
---

Arguments: `$ARGUMENTS`

The single way a change enters `game_state/`. The source is either an experiment or the
user's own instruction; everything after step 2 is the same either way.

**The user decides whether a change qualifies.** Your job is to establish exactly what it
involves, what it will break, and what it needs — then summarise and wait. Do not edit
`game_state/` before the confirmation in step 5.

Read `game_state/CLAUDE.md` and `docs/CHANGE_PROCESS.md` first.

## 1. Drift check

```bash
python -c "import sys; sys.path.insert(0,'tools'); from save_version import current_version, compute_file_diffs, ROOT; c=current_version(); d=sorted(str(k) for k in compute_file_diffs(c, ROOT)); print('CURRENT:', c.name); print('drift:', d or 'NONE - in sync')"
```

Drift means someone changed `game_state/` and never versioned it. **Stop and report it.**
Snapshot that work on its own first, under a slug describing what it was — not what you are
about to do.

## 2. Establish the source

**From an experiment** — the argument names one, or the user does:

- read its `NOTES.md`, its script and its `results.json`
- **if it has more than one arm, ask which is being taken.** Never assume the winner
- state what the script pinned: model, temperature, the exact prompt text, and anything else
  that differs from `config.py`
- note how it was run. An experiment may have bypassed the harness — calling the router
  directly, or sending a field the proxy drops — and that difference is a prerequisite, not
  a detail

**Stated directly** — the user describes the change:

- restate it precisely: which file, which value or which lines, from what to what
- if any part is ambiguous, ask before summarising. A guess here becomes a wrong version

## 3. Work out what the change requires

Three buckets. Only the first is a text diff.

- **Prompt text** — what changes in `prompts.py`, shown old against new
- **Model and config** — `config.py` values, and whether the harness can send what the
  change needs
- **What breaks downstream** — the one that gets missed. Trace the consumers before
  proposing anything:
  - `dialogueSystemPromptTemplate` requires `{NAME}` and `{CHARACTER_DESCRIPTION}`
  - `{CHARACTER_DESCRIPTION}` comes from `assemble_bio`, built from `CHARACTER_FIELDS`
  - those come from `parse_character` → `extract_field`, which looks for `**heading**`
    markers. Prose with no headings extracts nothing
  - character 2 is generated with `characterFullAntiDuplicationBlock` inserted — check the
    change still reads correctly in that form
  - `game.py`, the addressing call and the info extractor also read character data

State what the old code does with the new input. That is the bug that gets reported.

## 4. Prerequisites

What must be true before this can work at all. Check, do not assume:

- is the model reachable through the proxy with the settings it needs? The proxy drops
  `max_tokens`, `top_p` and `reasoning_effort`, and masks every upstream status as 500
- does it finish inside the HF router's ~120s ceiling?
- does anything need deploying — a proxy change committed but not live?
- token cost per generation, and per pair

## 5. Summarise, and stop

Put in front of the user, in one place:

- **what changes**, file by file, old against new
- **what it will break**, and what handling it requires
- **prerequisites**, and which are not yet met
- **the restore point** — the current version name, restorable with `restore_version.py`
- **what Unity will need** afterwards, from `backups/UNITY_MAPPING.md`
- **how it will be verified** — a generated **pair**, not a single character. Every
  experiment since 05 tested characters in isolation; the game makes two, and that step has
  never been tested

Then wait. The user decides.

## 6. After confirmation

Make the edit, keeping to one coherent idea. Then show what actually changed, file by file,
so the user sees the edit rather than a claim about it.

**Then ask whether to snapshot now**, and say why it is being asked: `game_state/` has
changed and is not yet versioned, and a run generated before the snapshot is tagged with the
*previous* version's name — wrong, permanently, and silently. Do not generate anything until
this is settled.

Propose a slug and a one-line summary with the question, so the answer can be a yes.

- **yes** → follow `/snapshot` from step 3: `python tools/save_version.py <slug> "<summary>"`,
  fill in the new version's `NOTES.md`, then produce the Unity port list
- **no** → say plainly that `game_state/` is now unversioned drift, and that the next
  `/update-game` or `/snapshot` will stop on it until it is resolved

Once versioned:

- **`/eval`** — verify it on a generated **pair**, not a single character
- if the source was an experiment, add a line to that experiment's `NOTES.md` recording that
  it was promoted, and to which version
