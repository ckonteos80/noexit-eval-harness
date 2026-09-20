# Change process

How to make a change to `game_state/` without losing the previous state or mislabelling the runs that come out of it.

This exists because of a specific failure on 2026-08-29: prompts were edited, a run was generated, and only afterwards was the version snapshotted. The run was stamped `2026-08-23_relational-sin-anchors` despite having been generated entirely under the new prompts, and the tag had to be corrected by hand. The same delay meant three earlier changes (a model swap, a signature change, and a dialogue-template edit) had gone unversioned for days and got swept into an unrelated version.

**Most of that is now enforced in code rather than left to discipline** — see *What the tools now guarantee* below. The steps still matter, but skipping one should produce an error rather than a quietly wrong record.

---

## The rule

> **`backups/` must always contain a version whose `game_state/` is byte-identical to what generated the run you are about to save.**

Everything below is in service of that one sentence.

`backups/CURRENT` is the machine-readable form of it: a small JSON file naming the version that matches live `game_state/` right now. It is written by `save_version.py` on every save and by `restore_version.py` after every restore, and it is what both savers read when tagging a run.

---

## The steps

### 1. Before you edit anything — check for drift

Live `game_state/` should match the version `CURRENT` names. If it doesn't, someone changed something and never versioned it, and you are about to bury that work inside your own change.

```bash
python -c "import sys; sys.path.insert(0,'tools'); from save_version import current_version, compute_file_diffs, ROOT; c=current_version(); d=sorted(str(k) for k in compute_file_diffs(c, ROOT)); print('CURRENT:', c.name); print('drift:', d or 'NONE - in sync')"
```

- `drift: NONE - in sync` → go to step 2.
- Anything listed → **snapshot that drift first**, on its own, before you start. Give it a slug describing what the *unversioned* work was, not what you're about to do:

```bash
python tools/save_version.py "unversioned-drift-model-swap" "Captures changes made since the last version that were never snapshotted."
```

This is the "snapshot before any changes" guarantee: you never begin editing on top of an unrecorded state, and you always have a restore point.

### 2. Make the change

Edit `game_state/`. Keep one change set to one coherent idea — the version folder is the unit of "what we tried," so a version that mixes an unrelated model swap into a prompt experiment can't be evaluated cleanly.

### 3. Snapshot — before generating a single run

```bash
python tools/save_version.py "short-kebab-slug" "One-line summary of what changed and why."
```

**This must happen before any run is generated under the new state.** Not after the run looks good, not after the eval — before. Do not make it conditional on the output being good: a bad run under a known version is useful data; a good run under an unknown version is not.

The web UI now enforces this — saving a session while `game_state/` has drifted returns an error instead of writing a mislabelled run. Your session stays open, so the fix is to snapshot and click Save again.

`save_version.py` writes the folder, `DIFF.md` (field-level before/after for `prompts.py`, unified diff for everything else), a `CHANGELOG.md` entry, the Unity-porting notes, and updates `backups/CURRENT`. It also archives the *previous* version's tagged runs into that previous folder, which is why the ordering in step 1 matters.

### 4. Fill in NOTES.md

`save_version.py` generates a NOTES.md that just repeats your one-line summary twice. Replace the "Changes from previous version" section with something a future reader can actually use:

- What each edit was, and the reasoning behind it — not just the text that changed, which `DIFF.md` already has.
- What was deliberately *not* done, and why. This is the part that stops the same rejected idea being re-proposed in three weeks.
- Anything carried in from earlier work that isn't part of this version's intent, under its own heading.

### 5. Generate and evaluate

Run sessions, then AI eval and human eval per `character-eval-guide.md`. Add the known issues back into that version's `NOTES.md` as they surface, so the next version starts from them rather than rediscovering them.

---

## What the tools now guarantee

As of 2026-08-29 these are enforced, not just documented:

- **`backups/CURRENT` is the single source of truth** for which version matches live `game_state/`. Nothing infers it from folder ordering any more, so same-day saves and restores can no longer mistag runs. `list_versions()` still sorts by name, but that is display order only and nothing depends on it for correctness.
- **A restore updates `CURRENT` to the version restored to**, not to the safety snapshot it just took. Runs generated after a restore are tagged correctly with no follow-up snapshot needed.
- **The web UI refuses to save a run while `game_state/` has drifted** from `CURRENT`, naming the changed files and telling you to snapshot. The session is kept in memory, so nothing is lost by the refusal. A forced save (`{"force": true}`) is possible but records `meta.drift_at_save` listing the files that didn't match, so the run is never silently mislabelled.
- **Prompt diffing is quote-agnostic.** `parse_prompt_fields` parses `prompts.py` with `ast`, so a single-quoted prompt is captured exactly like a triple-quoted one.
- **Every file type is diffed**, not just `*.py` — in both `save_version.py` and `restore_version.py`'s confirmation preview. Undecodable files are reported as `Binary file changed` rather than crashing the diff.

---

## When `save_version.py` itself needs updating

For ordinary work — editing prompts, models, temperatures, assembly or parsing logic — **nothing**. The script copies all of `game_state/` and auto-discovers every file inside it, including ones that didn't exist in the previous version. You never touch it.

Two cases still need hand-maintenance, because they are mappings the tool cannot infer:

| You did this | What breaks | What to do |
|---|---|---|
| Added a new file to `game_state/` | Snapshot and diff both work, but the Unity note comes out as `(no mapping recorded)` | Add an entry to `UNITY_MAPPING` (`tools/save_version.py`) |
| Added a Unity-mirroring file *outside* `game_state/` | Not snapshotted, not diffed, not flagged — like `simulator.py` today | Update `UNTRACKED_UNITY_NOTE` (`tools/save_version.py`), or move the file into `game_state/` |

Also update `UNITY_MAPPING` if an existing `game_state/` file starts corresponding to a different Unity script than it used to.

---

## Restoring

`restore_version.py` mirror-restores `game_state/` from a chosen backup — live files end up an exact copy, so anything added since is removed, not merged. It previews the changes and asks for confirmation first, and auto-saves a safety snapshot of the current state before touching anything, so a restore is never destructive on its own.

```bash
python tools/restore_version.py 2026-08-23_relational-sin-anchors
```

It accepts an unambiguous suffix, so `python tools/restore_version.py relational-sin-anchors` also works. Add `--yes` to skip the confirmation.

Afterwards, `CURRENT` points at the version you restored, and its stored `game_state/` genuinely matches what is live — so runs generated next are tagged correctly and no follow-up snapshot is needed. The safety snapshot remains in `backups/` as `<date>_pre-restore-safety` if you want the abandoned work back.
