"""
Reading and scoring saved runs.

The counterpart to library.py: library.py owns the character records, this owns the
run files in runs/. Both exist so the web UI never parses or rewrites a stored file
itself, and so a verdict is written by one function with one set of rules.

A run file is written by store.ExperimentStore.write_run and is immutable apart from
its eval slots -- the same split the character records use, where `character` and
`provenance` are fixed and `eval` is not.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from _paths import PROJECT_ROOT

RUNS_DIR = Path(PROJECT_ROOT) / "runs"
RATINGS = ("good", "neutral", "bad")

# Where a verdict may be written. `session_eval` judges the dialogue as a whole;
# `pair_eval` and `character_design_eval` are the older run-level slots the standalone
# viewer wrote, kept so nothing already scored becomes unreadable.
RUN_EVAL_FIELDS = ("session_eval", "pair_eval", "character_design_eval")


def path_for(run_id: str) -> Path:
    # A run_id reaches this from a URL, so it must not be able to name a file outside
    # runs/ -- "../../game_state/prompts" would otherwise resolve and be written to.
    p = (RUNS_DIR / f"{run_id}.json").resolve()
    if p.parent != RUNS_DIR.resolve():
        raise ValueError(f"not a run id: {run_id!r}")
    return p


def read_run(run_id: str) -> dict:
    return json.loads(path_for(run_id).read_text(encoding="utf-8"))


def _write(run_id: str, obj: dict) -> Path:
    p = path_for(run_id)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def _eval_brief(ev) -> dict:
    ev = ev or {}
    note = (ev.get("judge_notes") or "").strip()
    return {"rating": ev.get("rating"), "judge_model": ev.get("judge_model"),
            "has_notes": bool(note), "note": note[:240]}


def summarise(run: dict, run_id: str) -> dict:
    """The card fields, without the calls -- a run averages 68 KB, mostly prompts."""
    st = run.get("state") or {}
    meta = run.get("meta") or {}
    chars = [c for cid, c in sorted((st.get("characters") or {}).items()) if cid != "0"]
    calls = run.get("calls") or []
    by_type: dict[str, int] = {}
    for c in calls:
        t = c.get("call_type") or "?"
        by_type[t] = by_type.get(t, 0) + 1
    scored_calls = sum(1 for c in calls if (c.get("eval_scores_json") or {}).get("rating"))
    return {
        "run_id": run.get("run_id") or run_id,
        "written_at": run.get("written_at"),
        "turns": st.get("turn_count"),
        "session_id": st.get("session_id"),
        "characters": [{"name": c.get("name"), "age": c.get("age"),
                        "gender": c.get("gender")} for c in chars],
        "dialogue_lines": len(st.get("dialogue_entries") or []),
        "calls": len(calls),
        "call_types": by_type,
        "scored_calls": scored_calls,
        "phase": meta.get("phase"),
        "game_state_version": meta.get("game_state_version"),
        "drift_at_save": meta.get("drift_at_save"),
        # Set by a run seated from the library; absent on every run before that existed.
        "seated_char_ids": [c.get("char_id") for c in (meta.get("characters") or [])],
        "session_eval": _eval_brief(run.get("session_eval")),
    }


def list_runs() -> list[dict]:
    """Every run, newest first. Unreadable files are skipped, not fatal."""
    out = []
    for p in sorted(RUNS_DIR.glob("*.json"), reverse=True):
        try:
            out.append(summarise(json.loads(p.read_text(encoding="utf-8")), p.stem))
        except (OSError, json.JSONDecodeError, ValueError):
            continue
    return out


def set_run_eval(run_id: str, field: str = "session_eval", rating=None, notes=None,
                 judge_model: str | None = "human") -> dict:
    """
    One verdict and one note on a whole run. `rating` of None clears it.

    Same rule as library.set_eval: a judge already on the record is never replaced,
    so a verdict from a named model stays attributed to it after a human opens the
    form to read the note.
    """
    if field not in RUN_EVAL_FIELDS:
        raise ValueError(f"field must be one of {RUN_EVAL_FIELDS}")
    if rating is not None and rating not in RATINGS:
        raise ValueError(f"rating must be one of {RATINGS} or None")
    run = read_run(run_id)
    ev = dict(run.get(field) or {})
    ev["rating"] = rating
    if notes is not None:
        ev["judge_notes"] = notes
    if judge_model and not ev.get("judge_model"):
        ev["judge_model"] = judge_model
    ev["scored_at"] = datetime.now().isoformat(timespec="seconds")
    run[field] = ev
    _write(run_id, run)
    return run[field]


def set_call_eval(run_id: str, call_index: int, rating=None, notes=None,
                  judge_model: str | None = "human") -> dict:
    """
    A verdict on one call inside a run -- which is where a fault usually is. An
    extraction that invents a fact is one bad call in an otherwise ordinary session,
    and scoring the session cannot say that.

    Stored in `eval_scores_json` on the call, which is the slot the standalone viewer
    already wrote and store.write_run already carries forward across a re-save.
    """
    if rating is not None and rating not in RATINGS:
        raise ValueError(f"rating must be one of {RATINGS} or None")
    run = read_run(run_id)
    calls = run.get("calls") or []
    if not 0 <= call_index < len(calls):
        raise IndexError(f"call {call_index} out of range (run has {len(calls)})")
    ev = dict(calls[call_index].get("eval_scores_json") or {})
    ev["rating"] = rating
    if notes is not None:
        ev["judge_notes"] = notes
    if judge_model and not ev.get("judge_model"):
        ev["judge_model"] = judge_model
    ev["scored_at"] = datetime.now().isoformat(timespec="seconds")
    calls[call_index]["eval_scores_json"] = ev
    _write(run_id, run)
    return ev
