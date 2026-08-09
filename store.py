"""
Experiment store for the NoExit Agents eval loop.

Turns a completed harness run (its per-call transcript records) into two things:
  1. A per-run JSON file under runs/  — the full, readable record of one run.
  2. Rows in index.sqlite            — one row per call across ALL runs, for
                                        cross-run comparison.

Both live inside the project folder by default (root's runs/ and index.sqlite),
so run_viewer.html and Claude Code both find them at the same place without
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


class ExperimentStore:
    def __init__(self, root: str = "."):
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
        run_obj = {
            "run_id": run_id,
            "written_at": datetime.now(timezone.utc).isoformat(),
            "meta": meta or {},
            "state": state_snapshot or {},
            "calls": transcript_records,
        }
        run_path = self.runs_dir / f"{run_id}.json"
        run_path.write_text(json.dumps(run_obj, indent=2, ensure_ascii=False), encoding="utf-8")

        # ── 2. Index rows (one per call, for cross-run comparison) ──
        rows = []
        for rec in transcript_records:
            rows.append(tuple(_index_value(rec, col, run_id) for col in INDEX_COLUMNS))
        placeholders = ", ".join("?" for _ in INDEX_COLUMNS)
        col_names = ", ".join(f'"{c}"' for c in INDEX_COLUMNS)
        with sqlite3.connect(self.index_path) as conn:
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
