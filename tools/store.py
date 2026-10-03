"""
Experiment store for the NoExit Agents eval loop.

Turns a completed harness run (its per-call transcript records) into two things:
  1. A per-run JSON file under runs/  — the full, readable record of one run.
  2. Rows in index.sqlite            — one row per call across ALL runs, for
                                        cross-run comparison.

Both live inside the project folder by default (root's runs/ and index.sqlite),
so ui/run_viewer.html and Claude Code both find them at the same place without
extra configuration. Pass root= to point elsewhere if needed.

Nothing here makes network calls. It only reads the transcript records the
simulator already produced and writes files. The SQLite file is created
automatically on first write; every later run appends.

Eval scores are part of the schema but stay empty until the judge exists — the
`evals` columns are present and NULL for now.
"""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from _paths import PROJECT_ROOT


# Columns stored per call in the index. Mirrors the transcript record + an
# empty slot for eval scores (added when the judge lands).
INDEX_COLUMNS = [
    "run_id", "session_id", "timestamp", "turn_number", "call_type",
    "character_no", "requested_model", "served_model",
    "temperature", "max_tokens",
    "prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens",
    "finish_reason", "response_time_s", "retry_count", "cold_start", "endpoint",
    "notes",
    # ── eval slot (NULL until the judge scores this call) ──
    "eval_scores_json", "judge_model", "judge_notes",
]


def _carry_character_evals(old: dict, new: dict) -> None:
    """
    Re-attach per-character evals to the rebuilt state.

    state comes from simulator.state_snapshot_dict, which builds each character field by
    field and never emits eval/eval_ai -- so without this a re-save silently drops a
    human verdict on a character.
    """
    old_chars = ((old.get("state") or {}).get("characters") or {})
    new_chars = ((new.get("state") or {}).get("characters") or {})
    for cid, old_c in old_chars.items():
        if not isinstance(old_c, dict) or cid not in new_chars:
            continue
        for key in ("eval", "eval_ai"):
            if old_c.get(key) and not new_chars[cid].get(key):
                new_chars[cid][key] = old_c[key]


def _carry_call_evals(old: dict, new: dict) -> None:
    """
    Re-attach per-call evals, matched on (timestamp, call_type, character_no).

    The new calls come straight from the transcript and carry no eval slot. Matching on
    the triple rather than on list position means a re-save that added or reordered
    calls still lands each score on the call it was written about.
    """
    def key(rec):
        return (rec.get("timestamp"), rec.get("call_type"), rec.get("character_no"))

    scored = {key(c): c["eval_scores_json"] for c in (old.get("calls") or [])
              if isinstance(c, dict) and c.get("eval_scores_json")}
    if not scored:
        return
    for rec in new.get("calls") or []:
        hit = scored.get(key(rec))
        if hit and not rec.get("eval_scores_json"):
            rec["eval_scores_json"] = hit


class ExperimentStore:
    def __init__(self, root=None):
        root = PROJECT_ROOT if root is None else root
        self.root = Path(root)
        self.runs_dir = self.root / "runs"
        self.index_path = self.root / "index.sqlite"
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self._init_index()

    def _init_index(self):
        """Create the index table if the SQLite file/table doesn't exist yet."""
        cols_sql = ", ".join(f'"{c}" TEXT' for c in INDEX_COLUMNS)
        with sqlite3.connect(self.index_path) as conn:
            conn.execute(f"CREATE TABLE IF NOT EXISTS calls ({cols_sql})")
            conn.commit()

    def write_run(
        self,
        run_id: str,
        transcript_records: list[dict],
        state_snapshot: Optional[dict] = None,
        meta: Optional[dict] = None,
    ) -> Path:
        """
        Persist one run.

        run_id             : unique label for this run (e.g. '2026-08-09_54ec654e')
        transcript_records : the list of per-call dicts (from transcript.json)
        state_snapshot     : optional final game state (bios, dialogue, infoShared)
        meta               : optional free-form run metadata (config used, notes)

        Returns the path to the per-run JSON file.
        """
        # ── 1. Per-run JSON file (the full readable record) ──
        #
        # Merge rather than clobber. This function owns five keys; everything else in
        # the file was put there by something else and must survive a re-save. In
        # practice that means the evals: ui/run_viewer.html writes pair_eval,
        # character_design_eval, session_eval and their _ai twins at the top level,
        # per-character eval/eval_ai inside state.characters, and eval_scores_json on
        # individual calls. Rebuilding the object from five keys dropped all of them --
        # 173 populated eval objects across 18 of the 25 runs on disk, with notes
        # averaging well over a thousand characters, and nothing anywhere reads them
        # back to notice they had gone.
        run_path = self.runs_dir / f"{run_id}.json"
        existing = {}
        if run_path.exists():
            try:
                existing = json.loads(run_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                existing = {}        # unreadable: treat as absent rather than refuse to save

        run_obj = dict(existing)
        run_obj.update({
            "run_id": run_id,
            "written_at": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
            "state": state_snapshot or {},
            "calls": transcript_records,
        })
        _carry_character_evals(existing, run_obj)
        _carry_call_evals(existing, run_obj)
        run_path.write_text(json.dumps(run_obj, indent=2, ensure_ascii=False), encoding="utf-8")

        # ── 2. Index rows (one per call, for cross-run comparison) ──
        rows = []
        for rec in transcript_records:
            rows.append(tuple(_index_value(rec, col, run_id) for col in INDEX_COLUMNS))
        placeholders = ", ".join("?" for _ in INDEX_COLUMNS)
        col_names = ", ".join(f'"{c}"' for c in INDEX_COLUMNS)
        with sqlite3.connect(self.index_path) as conn:
            # Writing the same run_id twice overwrites its JSON file, so the index
            # has to match: clear this run's rows first or a re-save silently
            # double-counts every call in cross-run token queries.
            conn.execute("DELETE FROM calls WHERE run_id = ?", (run_id,))
            conn.executemany(
                f"INSERT INTO calls ({col_names}) VALUES ({placeholders})", rows
            )
            conn.commit()

        return run_path

    def run_count(self) -> int:
        return len(list(self.runs_dir.glob("*.json")))

    def call_count(self) -> int:
        with sqlite3.connect(self.index_path) as conn:
            return conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0]


def _index_value(rec: dict, col: str, run_id: str):
    """Pull one index column's value from a transcript record."""
    if col == "run_id":
        return run_id
    # eval columns don't exist in the transcript yet — store NULL
    if col in ("eval_scores_json", "judge_model", "judge_notes"):
        return None
    val = rec.get(col)
    # store booleans/ints as-is-ish (SQLite is forgiving); JSON-encode nothing here
    if isinstance(val, bool):
        return "true" if val else "false"
    return val
