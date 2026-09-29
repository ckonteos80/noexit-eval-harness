---
description: Version the game_state mirror and report what Unity still needs
argument-hint: [slug] [one-line summary]
---

Arguments: `$ARGUMENTS` — a kebab-case slug and a one-line summary, if given.

Read `game_state/CLAUDE.md` and `docs/CHANGE_PROCESS.md` before doing anything.

## Part 1 — version management

**1. Check for drift first.** Compare the working tree against the version named in
`backups/CURRENT`, using `save_version`'s own diffing rather than an eyeball:

```bash
python -c "import sys; sys.path.insert(0,'tools'); from save_version import current_version, compute_file_diffs, ROOT; c=current_version(); d=sorted(str(k) for k in compute_file_diffs(c, ROOT)); print('CURRENT:', c.name); print('drift:', d or 'NONE - in sync')"
```

If there is drift, **stop and report it**. Either the working tree has uncommitted changes
that were never snapshotted, or `CURRENT` is stale. Both need the user's decision; neither
should be papered over by taking a new snapshot.

**2. Show what changed** since the current version, file by file, before writing anything.

**3. Snapshot**, once the user has seen the diff:

```
python tools/save_version.py <slug> "<one-line summary>"
```

If no slug was given, propose one from the actual change and ask.

**4. Fill in the new version's `NOTES.md`** — what changed and why, what it is expected to
do, and what would show that it worked. Not a file list.

## Part 2 — Unity migration

A change to `game_state/` is not finished when it is snapshotted. It is finished when Unity
has it.

**5. Work out what Unity is missing.** `backups/UNITY_MAPPING.md` maps each file to its
counterpart — `prompts.py` to the prompt strings, `assembly.py` to
`CharacterGenerator.ExtractField`, `config.py` to the controller fields. Compare the
snapshot just taken against the known outstanding ports listed in `game_state/CLAUDE.md`.

**6. Report the port list** as work a Unity developer can act on: the file, the counterpart,
what changed, and what breaks if it is not ported. Where a change is behavioural rather than
textual — dash folding, reasoning stripping, a field count — say what the old code does with
new input, because that is the bug that will be reported.

**7. Update `game_state/CLAUDE.md`'s outstanding list** and `docs/INTEGRATION_BRIEF.md` if
the change affects integration.

Do not edit NOTES.md files inside existing backups. They are historical snapshots and were
accurate when written.
