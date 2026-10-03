"""
Character library: one JSON record per character, in characters/ at the project root.

A character used to exist only inside a session -- in session_state.json while it was
live, in runs/<id>.json once saved. That made it impossible to generate many, keep the
good ones, or seat the same pair again under different dialogue settings. A record here
is standalone and reusable.

Three rules the rest of the code relies on:

  * `record["character"]` is exactly game.Character's field set, so
    simulator.character_from_dict round-trips it with no mapping layer.
  * A char_id is NEVER overwritten. A reroll or a hand edit writes a new record with
    provenance.derived_from set, because runs reference char_ids and mutating one would
    silently rewrite the provenance of every run that used it.
  * The verbatim prompts in provenance are the real reproducibility guarantee, not
    game_state_version. The version says which files were supposed to be live; the
    prompt says what was actually sent, which is what differs under drift or an
    override. Keeping both makes a disagreement between them visible.

Harness-only: no Unity counterpart, nothing in game_state/, nothing to port.
"""
import ast
import io
import json
import os
import re
import secrets
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from _paths import PROJECT_ROOT

CHARACTERS_DIR = PROJECT_ROOT / "characters"
DELETED_DIR = CHARACTERS_DIR / "_deleted"
SCHEMA = 1

# Call types that are part of generating a character. 'life', 'sin' and 'stance' are
# historical -- they predate single-call generation but still appear in older runs.
GENERATION_CALL_TYPES = {"character", "name", "life", "sin", "stance"}


# ──────────────────────────────────────────────────────────────────────────────
# IDS AND PATHS
# ──────────────────────────────────────────────────────────────────────────────

def char_id_new(when: datetime | None = None) -> str:
    """
    <date>_<time>_<4 hex>. The id is the filename, so nothing has to be indexed to
    resolve one, and it sorts chronologically. No colons -- this runs on Windows.
    """
    when = when or datetime.now()
    # The suffix exists to de-collide writes inside one second. A bulk import does
    # hundreds, where 4 hex digits collide by the birthday bound, so check the disk
    # rather than trusting the entropy.
    for _ in range(1000):
        cid = f"{when:%Y-%m-%d_%H%M%S}_{secrets.token_hex(3)}"
        if not path_for(cid).exists():
            return cid
    raise RuntimeError("could not find a free char_id")


def path_for(char_id: str) -> Path:
    return CHARACTERS_DIR / f"{char_id}.json"


# ──────────────────────────────────────────────────────────────────────────────
# READ / WRITE
# ──────────────────────────────────────────────────────────────────────────────

def new_record(character: dict, provenance: dict, calls: list | None = None,
               char_id: str | None = None, created_at: str | None = None,
               tags: list | None = None, notes: str = "") -> dict:
    """Assemble a record. `character` must already be game.Character's field set."""
    return {
        "char_id": char_id or char_id_new(),
        "schema": SCHEMA,
        "created_at": created_at or datetime.now().isoformat(timespec="seconds"),
        "character": character,
        "provenance": provenance,
        "calls": calls or [],
        "tags": tags or [],
        "notes": notes,
    }


def write_character(record: dict) -> Path:
    """Write a record. Refuses to overwrite: char_ids are immutable."""
    CHARACTERS_DIR.mkdir(parents=True, exist_ok=True)
    p = path_for(record["char_id"])
    if p.exists():
        raise FileExistsError(f"{record['char_id']} already exists; char_ids are immutable")
    p.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


def read_character(char_id: str) -> dict:
    return json.loads(path_for(char_id).read_text(encoding="utf-8"))


def _summary(rec: dict) -> dict:
    """The card fields, for listing without shipping every prompt and call."""
    c, p = rec.get("character", {}), rec.get("provenance", {})
    return {
        "char_id": rec.get("char_id"),
        "name": c.get("name", ""),
        "age": c.get("age", 0),
        "gender": c.get("gender", ""),
        "description": c.get("description", ""),
        "words": p.get("words") or len((c.get("description") or "").split()),
        "created_at": rec.get("created_at"),
        "source": p.get("source"),
        "origin": p.get("origin"),
        "game_state_version": p.get("game_state_version"),
        "model": (p.get("settings") or {}).get("generation_model"),
        "tags": rec.get("tags", []),
    }


def list_characters(full: bool = False) -> list[dict]:
    """Newest first. Globs recursively so sharding into subfolders later needs no migration."""
    out = []
    if not CHARACTERS_DIR.exists():
        return out
    for p in sorted(CHARACTERS_DIR.glob("**/*.json")):
        if DELETED_DIR in p.parents:
            continue
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue                      # a half-written or hand-broken file is skipped
        out.append(rec if full else _summary(rec))
    out.sort(key=lambda r: r.get("created_at") or "", reverse=True)
    return out


def delete_character(char_id: str) -> Path:
    """Move to _deleted/ rather than unlink. These cost credits."""
    DELETED_DIR.mkdir(parents=True, exist_ok=True)
    dest = DELETED_DIR / f"{char_id}.json"
    shutil.move(str(path_for(char_id)), str(dest))
    return dest


def set_tags(char_id: str, tags=None, notes=None) -> dict:
    """
    Tags and notes are the one mutable part of a record: they are the user's
    annotation, not provenance, and nothing downstream reads them.
    """
    rec = read_character(char_id)
    if tags is not None:
        rec["tags"] = list(tags)
    if notes is not None:
        rec["notes"] = notes
    path_for(char_id).write_text(json.dumps(rec, indent=2, ensure_ascii=False),
                                 encoding="utf-8")
    return rec


# ──────────────────────────────────────────────────────────────────────────────
# IDEMPOTENCY
# ──────────────────────────────────────────────────────────────────────────────

def origin_key(origin: dict | None) -> str | None:
    """A stable string for an origin, so an import can be run twice safely."""
    if not origin:
        return None
    if "run_id" in origin:
        return f"run:{origin['run_id']}:{origin.get('slot')}"
    if "experiment" in origin:
        return f"exp:{origin['experiment']}:{origin.get('index')}"
    return json.dumps(origin, sort_keys=True)


def known_origins() -> set:
    return {k for k in (origin_key((r.get("provenance") or {}).get("origin"))
                        for r in list_characters(full=True)) if k}


# ──────────────────────────────────────────────────────────────────────────────
# IMPORT FROM A SAVED RUN
# ──────────────────────────────────────────────────────────────────────────────

def import_from_run(run_path, skip: set | None = None) -> list[str]:
    """
    One record per character in a saved run. Returns the char_ids written.

    Runs carry the generation calls, and those calls carry `system_prompt` and
    `user_prompt` -- so unlike experiments, a backfilled run recovers its prompts
    verbatim rather than by reconstruction.
    """
    run_path = Path(run_path)
    run = json.loads(run_path.read_text(encoding="utf-8"))
    skip = skip if skip is not None else known_origins()
    meta, state = run.get("meta") or {}, run.get("state") or {}
    calls = run.get("calls") or []
    written = []

    for cid, cdata in sorted((state.get("characters") or {}).items()):
        if cid == "0" or not (cdata or {}).get("description"):
            continue                      # the player, or a slot that never generated
        origin = {"run_id": run.get("run_id") or run_path.stem, "slot": int(cid)}
        if origin_key(origin) in skip:
            continue

        mine = [c for c in calls
                if c.get("call_type") in GENERATION_CALL_TYPES
                and str(c.get("character_no")) == str(cid)]
        char_call = next((c for c in mine if c.get("call_type") == "character"), None)
        name_call = next((c for c in mine if c.get("call_type") == "name"), None)
        last = char_call or (mine[-1] if mine else {})

        rec = new_record(
            character={k: v for k, v in cdata.items()
                       if k not in ("eval", "eval_ai")} | {"info_shared": []},
            created_at=(last.get("timestamp") or run.get("written_at")),
            provenance={
                "source": "backfilled_from_run",
                "origin": origin,
                "game_state_version": meta.get("game_state_version"),
                "drift_at_generation": meta.get("drift_at_save") or [],
                "gen_session_id": state.get("session_id"),
                "settings": {
                    "generation_model": last.get("model"),
                    "generation_temperature": last.get("temperature"),
                    "generation_max_tokens": last.get("max_tokens"),
                    "name_model": (name_call or {}).get("model"),
                    "name_temperature": (name_call or {}).get("temperature"),
                },
                "prompts": {
                    "character_system": (char_call or {}).get("system_prompt"),
                    "character_user": (char_call or {}).get("user_prompt"),
                    "name_user": (name_call or {}).get("user_prompt"),
                },
                "anti_duplication": {"used": int(cid) == 2, "other_char_id": None},
                "usable": True,
                "sanity": "not checked (predates generation_is_usable)",
                "attempts": None,
                "words": len((cdata.get("description") or "").split()),
                "derived_from": None,
                "complete": bool(char_call),
            },
            calls=mine,
        )
        write_character(rec)
        skip.add(origin_key(origin))
        written.append(rec["char_id"])
    return written


# ──────────────────────────────────────────────────────────────────────────────
# IMPORT FROM AN EXPERIMENT
# ──────────────────────────────────────────────────────────────────────────────

def _script_literals(folder: Path) -> dict:
    """
    Module-level string-literal assignments from an experiment's script.

    Only literals: SYSTEM is built as `prompts.characterSetupSystemPrompt + CRAFT` and
    cannot be read without executing the module, so it stays unknown rather than being
    guessed at. A wrong prompt in a provenance record is worse than an absent one.
    """
    out = {}
    for p in sorted(folder.glob("*.py")):
        if p.name.startswith("_"):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                v = node.value.value
                if isinstance(v, (str, int, float)):   # MODEL is a str, TEMP is a float
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            out[t.id] = v
        out.setdefault("__script__", p.name)
    return out


def _user_template(lits: dict, row: dict) -> tuple[str | None, str | None]:
    """
    (template, how). Picks the arm's template when the row names an arm, else the only
    USER-ish literal if there is exactly one. Ambiguity returns None -- see above.
    """
    # NAME_PROMPT also substitutes {AGE} and {GENDER}, so it must be excluded by name or
    # it competes with the story template and makes every experiment look ambiguous.
    cands = {k: v for k, v in lits.items()
             if k not in ("__script__", "NAME_PROMPT") and isinstance(v, str)
             and ("{AGE}" in v or "{GENDER}" in v)}
    arm = (row.get("arm") or "").upper()
    if arm and arm in cands:
        return cands[arm], f"script arm {arm}"
    if len(cands) == 1:
        k, v = next(iter(cands.items()))
        return v, f"script {k}"
    return None, None


def import_from_experiment(folder, skip: set | None = None) -> list[str]:
    """
    One record per generated story in an experiment's results.json. Returns char_ids.

    Experiments pin their own model, temperature and prompts inline and never touch
    game_state/, so these records carry no game_state_version -- the settings and the
    reconstructed prompt are all the provenance there is, which is why the prompt is
    left null when it cannot be read exactly.
    """
    folder = Path(folder)
    results = folder / "results.json"
    if not results.exists():
        return []
    data = json.loads(results.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else \
        [r for v in data.values() if isinstance(v, list) for r in v]
    skip = skip if skip is not None else known_origins()
    lits = _script_literals(folder)
    name_tpl = lits.get("NAME_PROMPT")
    written = []

    for i, row in enumerate(rows):
        text = (row or {}).get("text")
        if not text:
            continue
        origin = {"experiment": folder.name, "index": i}
        if row.get("arm"):
            origin["arm"] = row["arm"]
        if origin_key(origin) in skip:
            continue

        tpl, how = _user_template(lits, row)
        user = None
        if tpl:
            user = (tpl.replace("{AGE}", str(row.get("age", "")))
                       .replace("{GENDER}", str(row.get("gender", "")))
                       .replace("{NAME}", str(row.get("supplied_name", ""))))

        rec = new_record(
            character={
                "name": row.get("supplied_name") or "",
                "description": text,
                "gender": row.get("gender", ""),
                "age": int(row.get("age") or 0),
                "info_shared": [],
            },
            provenance={
                "source": "imported_from_experiment",
                "origin": origin,
                "game_state_version": None,
                "drift_at_generation": [],
                "gen_session_id": None,
                "settings": {
                    # the row first, then the script's pinned constants: experiments
                    # 18-20 record neither model nor temperature per row but pin both
                    # at module level
                    "generation_model": row.get("model") or lits.get("MODEL"),
                    "generation_temperature": row.get("temp", lits.get("TEMP")),
                    "reasoning_effort": row.get("effort") or lits.get("EFFORT"),
                    "name_model": lits.get("NAME_MODEL"),
                    "name_temperature": lits.get("NAME_TEMP"),
                    "script": lits.get("__script__"),
                },
                "prompts": {
                    # SYSTEM is prompts.characterSetupSystemPrompt + CRAFT, assembled at
                    # runtime, so it is not a literal and stays unknown. CRAFT is the part
                    # that varied between experiments and IS a literal, so it is recorded
                    # on its own rather than folded into a guess at the whole.
                    "character_system": None,
                    "character_user": user,
                    "name_user": name_tpl if isinstance(name_tpl, str) else None,
                    "craft_suffix": lits.get("CRAFT"),
                },
                "prompts_source": how,
                "anti_duplication": {"used": False, "other_char_id": None},
                "usable": True,
                "sanity": "not checked (experiment predates generation_is_usable)",
                "attempts": None,
                "words": row.get("words") or len(text.split()),
                "derived_from": None,
                "complete": bool(user),
            },
            calls=[],
            tags=[folder.name.split("_")[0]],
        )
        write_character(rec)
        skip.add(origin_key(origin))
        written.append(rec["char_id"])
    return written


def backfill_all(runs=True, experiments=True) -> dict:
    """Idempotent: anything already imported is recognised by its origin and skipped."""
    skip = known_origins()
    done = {"runs": 0, "experiments": 0, "char_ids": []}
    if runs:
        for p in sorted((PROJECT_ROOT / "runs").glob("*.json")):
            ids = import_from_run(p, skip=skip)
            done["runs"] += len(ids)
            done["char_ids"] += ids
    if experiments:
        for d in sorted((PROJECT_ROOT / "experiments").iterdir()):
            if d.is_dir() and not d.name.startswith("_"):
                ids = import_from_experiment(d, skip=skip)
                done["experiments"] += len(ids)
                done["char_ids"] += ids
    return done


# ──────────────────────────────────────────────────────────────────────────────
# RECOVERING THE SYSTEM PROMPT FOR PAST EXPERIMENTS
# ──────────────────────────────────────────────────────────────────────────────

def _git(*args) -> str:
    out = subprocess.run(["git", "-C", str(PROJECT_ROOT), *args],
                         capture_output=True, text=True, encoding="utf-8")
    return out.stdout.strip() if out.returncode == 0 else ""


def _current_at(when: str) -> str | None:
    """The version named by backups/CURRENT as of a commit timestamp."""
    sha = _git("log", "-1", "--format=%H", f"--until={when}", "--", "backups/CURRENT")
    if not sha:
        return None
    blob = _git("show", f"{sha}:backups/CURRENT")
    try:
        return json.loads(blob).get("version")
    except Exception:
        return None


def _version_for_experiment(folder_name: str):
    """
    The game_state version an experiment actually ran under, from git history, or None.

    Dates alone cannot answer this: five dates in backups/ carry more than one version,
    and 2026-09-27 carries three, so picking the latest one dated <= the experiment is
    arbitrary. backups/CURRENT is committed every time a version is taken, so its value
    at the moment the experiment folder landed is the real answer.

    Returns None rather than a guess when CURRENT changed between the day the experiment
    is dated and the day it was committed -- the run could have been under either.
    """
    m = re.search(r"(\d{4}-\d{2}-\d{2})", folder_name)
    if not m:
        return None, []
    added = _git("log", "--diff-filter=A", "--format=%cI", "-1", "--",
                 f"experiments/{folder_name}")
    if not added:
        return None, []
    at_commit = _current_at(added)
    at_run_start = _current_at(f"{m.group(1)}T00:00:00")
    cands = [v for v in dict.fromkeys([at_run_start, at_commit]) if v]
    if len(cands) != 1:
        return None, cands              # ambiguous: a snapshot happened in between
    d = PROJECT_ROOT / "backups" / cands[0]
    return (d if d.exists() else None), cands


def _system_prompt_at(version_dir) -> str | None:
    """characterSetupSystemPrompt as it stood in a snapshot."""
    p = version_dir / "game_state" / "prompts.py"
    if not p.exists():
        return None
    try:
        tree = ast.parse(p.read_text(encoding="utf-8"))
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "characterSetupSystemPrompt":
                    return node.value.value
    return None


def enrich_inferred_system_prompts() -> int:
    """
    Fill `character_system_inferred` on experiment records.

    An experiment's script builds SYSTEM as `prompts.characterSetupSystemPrompt + CRAFT`,
    read from game_state/ on the day it ran -- so the folder never held it and the file
    has changed many times since. It IS recoverable: pick the backups/ version that was
    current on the experiment's date and read characterSetupSystemPrompt out of it.

    That is an inference, not a record, so it goes in its own field. `character_system`
    stays null, because a prompt that merely probably matches is worse than an absent
    one when the whole point of provenance is knowing what was sent.
    """
    n = 0
    for rec in list_characters(full=True):
        p = rec.get("provenance") or {}
        origin = p.get("origin") or {}
        exp = origin.get("experiment")
        if not exp:
            continue
        ver, cands = _version_for_experiment(exp)
        sysmsg = _system_prompt_at(ver) if ver else None
        craft = p["prompts"].get("craft_suffix") or ""
        if sysmsg:
            p["prompts"]["character_system_inferred"] = sysmsg.rstrip() + craft
            p["prompts_inferred_from"] = ver.name
            p.pop("prompts_inferred_candidates", None)
        else:
            # Cannot be attributed to one version -- record the candidates and leave the
            # prompt null. Clearing matters: an earlier, weaker guess must not survive.
            p["prompts"].pop("character_system_inferred", None)
            p.pop("prompts_inferred_from", None)
            p["prompts_inferred_candidates"] = cands
        path_for(rec["char_id"]).write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
        n += 1
    return n
