# NoExit Agents

A Python harness that mirrors the NoExit Unity game's LLM call flow, so prompts and models can be iterated on outside Unity. On top of the harness sits an eval loop: every call is fully observable (tokens, timing, retries, served vs. requested model), every session can be saved and scored, and every prompt/config change can be checkpointed and — when it's good — ported back to Unity by hand.

Nothing here runs inside Unity. `game_state/` mirrors specific Unity C# behavior closely enough that changes made here are meant to be manually re-applied there; everything else is harness/tooling that only exists to support iterating and evaluating outside the game.

> **Before changing anything in `game_state/`, read [`CHANGE_PROCESS.md`](docs/CHANGE_PROCESS.md).** Snapshot ordering is not optional — runs are tagged with whatever version is newest in `backups/` at save time, so a change made without a snapshot produces runs labelled with the wrong version.

---

## Folders

### `game_state/`
Every file that mirrors real Unity C# behavior — the prompts, model/temperature config, and the structural code tightly coupled to them. This is what `backups/` versions and what eventually needs porting back to Unity when a change is worth keeping. See `backups/UNITY_MAPPING.md` for exactly which file maps to which Unity script.

### `backups/`
Version history of `game_state/`. Each save (`tools/save_version.py`) creates one dated folder containing a full copy of `game_state/` at that point, `NOTES.md` (state summary + which Unity files to check), `DIFF.md` (exact before/after), and a `runs/` subfolder of every session that was generated under that version. `CHANGELOG.md` is the running index across all versions; `UNITY_MAPPING.md` is the static file → Unity-script reference table.

### `runs/`
Every saved session, one JSON file per run (bios, full per-call transcript, metadata, eval scores). This is the live, ever-growing "current" set — `ui/run_viewer.html` reads from here, and `tools/save_version.py` archives a copy into the relevant `backups/` version once that version is superseded.

### `noexit_outputs/`
The raw scratch log `tools/simulator.py` writes to *during* a session — `transcript.csv`/`transcript.json` (every call, unscoped, keeps growing across every process you run), `session_state.json` (latest session snapshot, used to resume state across separate calls), `edits.csv` (live prompt edits made mid-session). Disposable — `runs/` is where you keep a session on purpose; this is just where it's logged as it happens.

---

## `tools/`

**`_paths.py`** — Single source of truth for project paths. Every other script here imports `PROJECT_ROOT`, `BACKUPS`, `GAME_STATE`, `RUNS`, `OUTPUTS` and `UI` from it rather than deriving them from its own `__file__`, and importing it also puts the project root on `sys.path` so `game_state` stays importable from inside `tools/`. Change paths here, nowhere else.

**`simulator.py`** — The orchestrator. Session setup, the character-generation chain, the narrator call, player turns (info extraction → addressing → dialogue → info extraction), transcript logging, and live in-session prompt editing. Its call-flow/decision logic (who replies, when addressing triggers) mirrors Unity's `CharacterGenerator.GenerateCharacter`/`CharacterController.ParsedText`, while the logging/observability code around it has no Unity equivalent at all.

**`store.py`** — Experiment store. Turns a finished session into a JSON file under `runs/` and indexed rows in `index.sqlite`.

**`run_session.py`** — CLI driver for one full interactive session: generate both characters → narrator → type your own turns → save. Tags the saved run with whichever `game_state` version is currently active.

**`webapp.py`** — Local browser UI for playing a session (stdlib only, no dependencies; serves `ui/webapp.html` on `127.0.0.1:8765`). Start a full session, or use **Generate Characters Only** to produce a character pair without the narrator or any dialogue — the fast path for iterating on character-generation prompts. Saves through the same `store.write_run` path as everything else, so chars-only runs open in the viewer normally.

**`export.py`** — Bundles a session's outputs (transcripts, edits log, current `game_state/`) into a zip; writes human-readable session notes and a Unity migration brief documenting exactly which prompt fields changed.

**`save_version.py`** — Snapshots `game_state/` into `backups/<date>_<slug>/`, diffs it against the previous version, writes the Unity-porting notes, and archives that now-superseded version's tagged runs.

**`restore_version.py`** — Mirror-restores `game_state/` from a chosen backup version (live files end up an exact copy — nothing added since is left behind). Always auto-saves a safety snapshot of the current state first.

---

## Files (project root)

**`index.sqlite`** — SQLite index of every call across every run (written by `store.py`), for cross-run queries like per-run token totals.

**`requirements.txt`** — Python dependencies (just `requests`).

---

## `docs/`

**`CHANGE_PROCESS.md`** — The SOP for changing `game_state/`: check for unversioned drift before editing, snapshot before generating any runs, and what to put in `NOTES.md`. Read this first.

**`eval-loop-scoring-design.md`** — Design doc for the two scoring rubrics (character generation, dialogue) that both human and future AI evals are built from.

**`character-eval-guide.md`** — How to judge generated characters (per-character, pair-level, overall design). Written as a director's first impression rather than a checklist; the good/neutral/bad rating follows from the note, not the other way round.

**`stanislavski-an-actor-prepares.md`** — Reference notes on Stanislavski's system, each concept tied to a problem seen in eval. Source for the 2026-08-29 prompt changes.

**`aristotle-poetics.md`** — Reference notes on Aristotle's *Poetics* (plot before character, necessity and probability, peripeteia, the unity/removability test). Source for the 2026-09-12 prompt changes.

**`INTEGRATION_BRIEF.md`** — Historical record of the original harness integration into this project folder.

---

## `ui/`

**`webapp.html`** — The UI `webapp.py` serves. Chat view, character sidebar, and the characters-only review screen.

**`run_viewer.html`** — Self-contained browser viewer (no server, no dependencies). Two views: **Character Gen** (bios plus editable human and AI eval columns, three independently-scrolling panes) and **Table** (every call across loaded runs, sortable/filterable by column group and row category, with inline-editable scoring). Saves edits back to the run JSON directly via the File System Access API. Open it by double-clicking; it needs nothing else.

## `game_state/`

**`prompts.py`** — Every prompt string. Mirrors `PromptsController.cs`.

**`config.py`** — Endpoints, model strings, temperatures, token limits, age range, dialogue-history window. Mirrors values set in the Unity Inspector across `CharacterController`, `CharacterGenerator`, and `ModelNamesController`.

**`assembly.py`** — Pure functions: assemble prompts from `prompts.py` templates + inputs, and parse model responses back into structured fields. Mirrors the assembly/parsing logic in `CharacterController.cs` and `CharacterGenerator.cs`.

**`game.py`** — Session state, person-number mapping (who's "other_1" vs "other_2" from each character's perspective), dialogue-history formatting. Mirrors the state Unity's `CharacterController.cs` holds.

**`providers.py`** — HTTP wrappers for the chat proxy and info-extractor endpoints, with retry/cold-start handling. Mirrors `APIRequestHandler.cs`/`InfoExtractorHandler.cs`.
