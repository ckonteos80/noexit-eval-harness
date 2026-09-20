# Integration Brief — Experiment Store + Run Viewer

**For:** Claude Code, integrating into `D:\Dropbox\_Projects\HuggingFace Projects\NoExit Agents\`
**Produced by:** a sandbox prototype session (Path A) — every change below was written and verified live against the real Hugging Face endpoints before packaging.
**Scope of this package:** the *plumbing* for the eval loop — capture per-call metadata, store each run (JSON + SQLite), and view it. It does **not** include the simulated player, the judge, the batch runner, or any prompt/model changes. Those are the next stage.

---

## Context

The NoExit harness mirrors the Unity game's call flow so prompts and models can be iterated outside Unity. We are building a human-in-the-loop evaluation loop on top of it. The first requirement was to make every LLM call **fully observable**: which model was requested and which was actually served, tokens used, response time, retries/cold-starts, the exact prompts sent, the response — and a slot for eval scores to be filled in later by a judge that does not exist yet.

This package delivers that observability plus a portable file-based store and a viewer. It was proven end-to-end: a real character pair was generated through the modified pipeline, written to the store, and rendered in the viewer (both card and table views) successfully.

**Environment note:** this package was built in a temporary sandbox. The `NoExit Agents` folder on disk is the permanent home. The one consequence that needs action is a hardcoded sandbox path — see **Step 1** below. It is the single most important integration task; nothing writes correctly until it is fixed.

---

## Files affected

**Changed (behavioural):**
- `providers.py` — **CHANGED.** `call_proxy` and `call_info_extractor` now return a `CallResult` object instead of a bare `str`. `CallResult.content` holds the reply text (as before); new fields carry the metadata.
- `simulator.py` — **CHANGED.** `_TRANSCRIPT_HEADERS` gained 11 metadata columns; `log_call` gained an optional `meta` parameter; all 7 provider call sites updated to capture the `CallResult`, use `.content`, and pass `meta=`.

**New:**
- `store.py` — **NEW.** `ExperimentStore`: writes one per-run JSON file under `runs/` and appends one row per call to `index.sqlite`. Includes an empty eval slot (NULL columns) for the future judge.
- `run_viewer.html` — **NEW.** Self-contained viewer (no build step, no dependencies). Drag-drop one or more run JSON files; card view (full round trip per call) and sortable table view (cross-run comparison). Inherits the design language of the existing `session_viewer.html`.
- `runs/2026-08-09_834a3e1e.json` — **SAMPLE.** A real generated run, so the viewer works on first open. Safe to delete once you have your own runs.

**Unchanged (included for a complete, runnable set — identical to project knowledge, safe to overwrite):**
- `config.py`, `prompts.py`, `assembly.py`, `game.py`, `export.py`, `requirements.txt`

**No new dependencies.** `store.py` uses only the standard library (`sqlite3`, `json`, `pathlib`, `datetime`). `run_viewer.html` needs no server or packages. `requirements.txt` is unchanged (`requests` only).

---

## Step-by-step integration

### Step 1 — Fix the hardcoded sandbox output path (REQUIRED FIRST)

`simulator.py` writes transcripts to an absolute sandbox path that does not exist on this machine:

```python
OUTPUT_DIR = Path("/home/claude/noexit_outputs")
```

Change it to a path inside the project. Recommended: make it relative to the project folder, e.g.

```python
OUTPUT_DIR = Path(__file__).parent / "noexit_outputs"
```

`export.py` has the same issue — it writes zips to `Path("/home/claude")`. Change that base directory to the project folder (or a chosen outputs location) as well.

Do not change any other paths. `PROMPTS_FILE = Path(__file__).parent / "prompts.py"` is already relative and correct.

### Step 2 — Place the files

Copy all files from this package into the `NoExit Agents` folder, preserving the `runs/` subfolder. The unchanged `.py` files are byte-identical to project knowledge; overwriting is safe. Keep the existing `eval-loop-scoring-design.md` and `session_viewer.html` if present — this package does not replace them (`run_viewer.html` is a new, separate viewer for the new run format).

### Step 3 — Confirm imports and connectivity

From the project folder:
```
pip install -r requirements.txt
python -c "import config, prompts, providers, assembly, game, simulator, export, store; print('imports OK')"
```
Then make one live proxy call and one extractor call to confirm the machine can reach `*.hf.space` (egress allowlist). Cold starts on the extractor can take 10–30s; `providers.py` retries automatically.

### Step 4 — Run one generation and write it to the store

Minimal wiring (this is the pattern the future batch runner will formalise — it is **not** yet a bundled script):

```python
import json
from datetime import datetime, timezone
import simulator, store

state = simulator.new_session()
simulator.generate_character(state, 1)
simulator.generate_character(state, 2)

records  = json.load(open(simulator.TRANSCRIPT_JSON))
snapshot = json.load(open(simulator.STATE_JSON))

st = store.ExperimentStore(root=".")   # project root -- runs/ and index.sqlite live here
run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d_") + state.session_id
st.write_run(run_id, records, snapshot, meta={"phase": "baseline"})
```

`store.ExperimentStore(root=...)` creates `root/runs/` and `root/index.sqlite` automatically on first use. Point `root` wherever you want the experiment history to live inside the project.

### Step 5 — View a run

Open `run_viewer.html` in a browser. Drag the run JSON from `runs/` onto it (or use "Choose files"). Drop several run files to compare them in the table view. The viewer reads the JSON files directly — it does **not** read `index.sqlite` (browsers can't open SQLite without extra libraries; the SQLite index is for programmatic/Claude Code querying).

---

## What changed, in detail (for verification / re-application)

### `providers.py`
- Added `@dataclass CallResult` with fields: `content`, `requested_model`, `served_model`, `prompt_tokens`, `completion_tokens`, `total_tokens`, `cached_tokens`, `finish_reason`, `response_time_s`, `retry_count`, `cold_start`, `provider`, `temperature`, `max_tokens`, `endpoint`; plus `to_dict()`.
- `call_proxy(...) -> CallResult`: times the call; on success reads `content` from `choices[0].message.content`, `served_model` from `data["model"]`, `finish_reason` from `choices[0].finish_reason`, and token counts from `data["usage"]`; tracks `retry_count` and sets `cold_start=True` when a 503/504 triggers a retry. Behaviour is otherwise identical to before (same payload, same retry/backoff, still does NOT strip newlines).
- `call_info_extractor(...) -> CallResult`: `content` is the extracted string (or `"none"`); token fields are `None` (the extractor endpoint reports no usage); captures `response_time_s`, `retry_count`, `cold_start`.

### `simulator.py`
- `_TRANSCRIPT_HEADERS`: appended `requested_model, served_model, prompt_tokens, completion_tokens, total_tokens, cached_tokens, finish_reason, response_time_s, retry_count, cold_start, endpoint`.
- `log_call(...)`: new optional `meta: providers.CallResult = None`; when provided, its `to_dict()` values populate the new columns (CSV and JSON both).
- Call sites updated (7): name generation; `_call_with_parse_retry` (life/sin/stance); `run_narrator`; player-message info extraction in `run_player_turn`; the addressing loop in `_run_addressing`; and dialogue + reply-extraction in `_run_character_reply`. Each now captures the `CallResult`, uses `.content` for logic/logging, and passes `meta=` to `log_call`. The `_call_with_parse_retry` return signature is unchanged (still returns the response text via `.content`).

### `store.py`
- `INDEX_COLUMNS` mirrors the transcript record plus three eval columns (`eval_scores_json`, `judge_model`, `judge_notes`) stored NULL until a judge exists.
- `write_run(run_id, transcript_records, state_snapshot=None, meta=None)` writes `runs/<run_id>.json` (full readable record) and appends index rows. `run_count()` / `call_count()` for quick checks.

### `run_viewer.html`
- Accepts the run format `{run_id, meta, state, calls:[...]}` and, as a fallback, a raw `transcript.json` array. Card view: per-call round trip (system/user/response/metadata/eval slot) with metadata badges (served model highlighted when it differs from requested; cold-start and cut-off badges). Table view: one sortable row per call across all loaded runs.

---

## Don't touch

- **Prompt content** (`prompts.py`) — unchanged here by design. Prompt iteration is a later, separate stage driven by eval results.
- **Model/temperature config** (`config.py`) — unchanged. Model sweeps are a later stage.
- **The eval/judge** — does not exist yet. Leave the eval columns NULL. Do not invent a scoring implementation as part of this integration.
- **The info-extractor behaviour** — its failures are a training-data matter, out of scope. This package only *measures* it.
- **The `.content` contract** — anything that consumed a provider return as a string must now use `.content`. Do not "unwrap" `CallResult` back into a bare string return; the metadata is the whole point.
- **Newline handling** — the harness intentionally does NOT strip newlines (Unity has that bug separately). Keep it that way.

---

## Acceptance criteria

1. `import ... store` succeeds; all modules import with no errors.
2. A generation run completes and `simulator.TRANSCRIPT_JSON` contains, for every proxy call, non-null `served_model`, `total_tokens`, `response_time_s`, and `finish_reason`. (Info-extraction calls correctly have null token fields.)
3. `store.write_run(...)` produces `runs/<run_id>.json` and appends N rows to `index.sqlite`, where N == number of calls in the run.
4. `index.sqlite` is queryable, e.g. `SELECT run_id, SUM(CAST(total_tokens AS INT)) FROM calls GROUP BY run_id;` returns a per-run token total.
5. The eval columns (`eval_scores_json`, `judge_model`, `judge_notes`) exist and are NULL.
6. `run_viewer.html` opens the sample run and shows: run-summary strip, both character bios, per-call cards with metadata, and the "Not yet scored" eval slot; the table view sorts by clicking headers.
7. The OUTPUT_DIR / export paths from Step 1 point inside the project — no `/home/claude/...` paths remain.

## Verification

```
# 1. imports
python -c "import config, prompts, providers, assembly, game, simulator, export, store; print('OK')"

# 2. one run + store (see Step 4 snippet), then:
python -c "import sqlite3; c=sqlite3.connect('index.sqlite'); \
print(c.execute('SELECT COUNT(*) FROM calls').fetchone()); \
print(c.execute('SELECT run_id, SUM(CAST(total_tokens AS INT)) FROM calls GROUP BY run_id').fetchall())"

# 3. open run_viewer.html, drag in runs/<run_id>.json, check both views.
```

---

## What comes next (NOT in this package)

The plumbing is done. The next build stage — to be briefed separately — is the loop itself:
1. **Simulated player** — a capable model playing the human, with its own persona guidance (2–3 personas to start).
2. **Batch runner** — run N full sessions unattended, calling `store.write_run` after each.
3. **Judge** — scores each result against the rubric in `eval-loop-scoring-design.md` (hybrid: practical pass/flag, mood 1–3 anchored), writing into the eval columns this package left NULL.
4. **Addressing accuracy** — scored separately against hand-labelled messages.

The record schema, storage, and viewer built here are designed so that the judge's scores drop into the existing eval slot without any restructuring.
