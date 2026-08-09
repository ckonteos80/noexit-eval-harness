# NoExit Agents

A Python harness that mirrors the NoExit Unity game's LLM call flow, so prompts and models can be iterated on outside Unity. On top of the harness sits an eval loop: every call is fully observable (tokens, timing, retries, served vs. requested model), every session can be saved and scored, and every prompt/config change can be checkpointed and — when it's good — ported back to Unity by hand.

Nothing here runs inside Unity. `game_state/` mirrors specific Unity C# behavior closely enough that changes made here are meant to be manually re-applied there; everything else is harness/tooling that only exists to support iterating and evaluating outside the game.

---

## Folders

### `game_state/`
Every file that mirrors real Unity C# behavior — the prompts, model/temperature config, and the structural code tightly coupled to them. This is what `backups/` versions and what eventually needs porting back to Unity when a change is worth keeping. See `backups/UNITY_MAPPING.md` for exactly which file maps to which Unity script.

### `backups/`
Version history of `game_state/`. Each save (`save_version.py`) creates one dated folder containing a full copy of `game_state/` at that point, `NOTES.md` (state summary + which Unity files to check), `DIFF.md` (exact before/after), and a `runs/` subfolder of every session that was generated under that version. `CHANGELOG.md` is the running index across all versions; `UNITY_MAPPING.md` is the static file → Unity-script reference table.

### `runs/`
Every saved session, one JSON file per run (bios, full per-call transcript, metadata, eval scores). This is the live, ever-growing "current" set — `run_viewer.html` reads from here, and `save_version.py` archives a copy into the relevant `backups/` version once that version is superseded.

### `noexit_outputs/`
The raw scratch log `simulator.py` writes to *during* a session — `transcript.csv`/`transcript.json` (every call, unscoped, keeps growing across every process you run), `session_state.json` (latest session snapshot, used to resume state across separate calls), `edits.csv` (live prompt edits made mid-session). Disposable — `runs/` is where you keep a session on purpose; this is just where it's logged as it happens.

---

## Files (project root)

**`simulator.py`** — The orchestrator. Session setup, the character-generation chain, the narrator call, player turns (info extraction → addressing → dialogue → info extraction), transcript logging, and live in-session prompt editing. Its call-flow/decision logic (who replies, when addressing triggers) mirrors Unity's `CharacterGenerator.GenerateCharacter`/`CharacterController.ParsedText`, while the logging/observability code around it has no Unity equivalent at all.

**`store.py`** — Experiment store. Turns a finished session into a JSON file under `runs/` and indexed rows in `index.sqlite`.

**`run_session.py`** — CLI driver for one full interactive session: generate both characters → narrator → type your own turns → save. Tags the saved run with whichever `game_state` version is currently active.

**`run_viewer.html`** — Self-contained browser viewer (no server, no dependencies). Two views: **Character Gen** (bios + editable human-eval scoring, two independently-scrolling panes) and **Table** (every call across loaded runs, sortable/filterable by column group and row category, with inline-editable dialogue scoring). Saves edits back to the run JSON file directly via the File System Access API.

**`export.py`** — Bundles a session's outputs (transcripts, edits log, current `game_state/`) into a zip; writes human-readable session notes and a Unity migration brief documenting exactly which prompt fields changed.

**`save_version.py`** — Snapshots `game_state/` into `backups/<date>_<slug>/`, diffs it against the previous version, writes the Unity-porting notes, and archives that now-superseded version's tagged runs.

**`restore_version.py`** — Mirror-restores `game_state/` from a chosen backup version (live files end up an exact copy — nothing added since is left behind). Always auto-saves a safety snapshot of the current state first.

**`index.sqlite`** — SQLite index of every call across every run (written by `store.py`), for cross-run queries like per-run token totals.

**`requirements.txt`** — Python dependencies (just `requests`).

**`INTEGRATION_BRIEF.md`** — Historical record of the original harness integration into this project folder.

**`eval-loop-scoring-design.md`** — Design doc for the two scoring rubrics (character generation, dialogue) that both human and future AI evals are built from.

---

## Files (`game_state/`)

**`prompts.py`** — Every prompt string. Mirrors `PromptsController.cs`.

**`config.py`** — Endpoints, model strings, temperatures, token limits, age range, dialogue-history window. Mirrors values set in the Unity Inspector across `CharacterController`, `CharacterGenerator`, and `ModelNamesController`.

**`assembly.py`** — Pure functions: assemble prompts from `prompts.py` templates + inputs, and parse model responses back into structured fields. Mirrors the assembly/parsing logic in `CharacterController.cs` and `CharacterGenerator.cs`.

**`game.py`** — Session state, person-number mapping (who's "other_1" vs "other_2" from each character's perspective), dialogue-history formatting. Mirrors the state Unity's `CharacterController.cs` holds.

**`providers.py`** — HTTP wrappers for the chat proxy and info-extractor endpoints, with retry/cold-start handling. Mirrors `APIRequestHandler.cs`/`InfoExtractorHandler.cs`.
