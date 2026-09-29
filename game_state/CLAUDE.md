# game_state — the Unity mirror

Every file here has a counterpart in the Unity project. A change here is a change to the
game, and is only finished when it has been ported. `backups/UNITY_MAPPING.md` holds the
file-by-file mapping; `save_version.py` regenerates it.

| file | Unity counterpart |
|---|---|
| `prompts.py` | the prompt strings |
| `config.py` | `CharacterController` / `CharacterGenerator` fields |
| `assembly.py` | `CharacterGenerator.ExtractField` and the bio assembly |
| `game.py` | the turn loop |
| `providers.py` | the HTTP layer |

## Before you edit

**`docs/CHANGE_PROCESS.md` is the process, not a suggestion.** In order:

1. **Check for drift** against `backups/CURRENT` — the working tree may differ from the
   version that is supposedly live, and if it does, that must be resolved first.
2. Make the change.
3. **Snapshot before generating a single run.** `python tools/save_version.py <slug>
   "<one-line summary>"`. A run generated from an unsnapshotted state cannot be attributed.
4. Fill in the version's `NOTES.md`.
5. Generate and evaluate.

`backups/CURRENT` names the live version. It is the single source of truth for what
`game_state/` currently is — not the working tree, not the last commit.

## Reloading

**Only `prompts.py` is hot-reloaded**, via `assembly._reload_prompts()`. Editing `config.py`,
`assembly.py`, `providers.py` or `game.py` requires restarting whatever is running
(`tools/webapp.py`, `tools/simulator.py`, `tools/run_session.py`). A change that appears to
have no effect is almost always this.

## Known outstanding ports to Unity

Verify against `backups/UNITY_MAPPING.md` and the Unity project before relying on this list —
it is accurate as of 2026-09-29 and nothing here updates itself:

- **line-anchored `ExtractField` end marker** — the Python side ends a field at the next
  heading rather than the next blank line
- **dash folding and `<think>` stripping** — `assembly._MATCH_EQUIV` folds U+2010–2015,
  U+2212, U+00AD to `-` and the narrow spaces to a space, so a heading typed with a
  non-breaking hyphen still matches; `strip_reasoning` removes inline reasoning blocks. Both
  were replayed against every historical extraction before landing
- **the nine-field character rewrite** — `CHARACTER_FIELDS` went from eleven fields to nine
  (`who_loved`, `who_hated` and `cause_of_death` dropped, `people` added) and `assemble_bio`
  from ten arguments to eight

## Experiments do not live here

Prompt A/B work happens in `experiments/`, which imports this package read-only and pins its
own model and temperature. Nothing from an experiment is promoted into `game_state/` without
going through the change process above.

Standing: **no naming tradition** is passed to character generation, since 2026-09-27.
