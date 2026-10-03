"""
The generation pipeline for experiments, identical to the one the game runs.

Two problems this exists to fix.

**Experiments and the game produced different artefacts.** Experiments 15 and 17 made no
name call, so those characters have no name at all; 18-20 did. None of them applied
`assembly.generation_is_usable`, so the one-in-ten first-person story that the harness
now rejects and retries would sit in an experiment's results looking like a result.

**An experiment folder did not record what it sent.** `results.json` held the text and
the measurements; the prompts lived in the script -- and only half of them, because
`SYSTEM` is `prompts.characterSetupSystemPrompt + CRAFT`, assembled at run time from a
file that has changed many times since. Roughly 200 of the ~290 words actually sent were
in no file the experiment owns. Now every generation writes a character record carrying
both prompts verbatim, and the folder gets a `prompts.json` manifest.

Settings are still **pinned by the experiment**, exactly as `CLAUDE.md` requires: every
one is an argument here and nothing is read from `config` except `PROXY_URL`, which is
an endpoint rather than a setting.
"""
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from game_state import config, assembly          # noqa: E402
import library                                   # noqa: E402


def _post(body, timeout):
    return requests.post(config.PROXY_URL, timeout=timeout, json=body)


def make_name(*, name_prompt, model, temperature, age, gender,
              attempts=4, timeout=150, proxy_timeout=120):
    """The name call. Returns (name, raw) or (None, reason)."""
    user = (name_prompt.replace("{AGE}", str(age)).replace("{GENDER}", gender))
    body = {"model": model, "temperature": temperature, "provider": "hf",
            "timeout": proxy_timeout, "messages": [{"role": "user", "content": user}]}
    last = "no attempt"
    for _ in range(attempts):
        try:
            r = _post(body, timeout)
            if r.status_code == 200:
                raw = r.json()["choices"][0]["message"]["content"]
                name = assembly.strip_reasoning(raw).strip().strip('."“”')
                if name:
                    return name, user
            else:
                last = f"HTTP {r.status_code}"
        except Exception as e:
            last = type(e).__name__
        time.sleep(5)
    return None, last


def generate(*, system, user_template, model, temperature,
             age, gender,
             experiment, index, arm=None,
             name_prompt=None, name_model=None, name_temperature=None,
             supplied_name=None,
             reasoning_effort=None, max_tokens=0, proxy_timeout=300,
             other_name=None, other_bio=None,
             attempts=3, timeout=330, write_record=True, extra=None):
    """
    One character, the way the harness makes one: name call, story call,
    strip_reasoning, generation_is_usable with retry.

    Returns the row to append to results.json -- the measurements plus `char_id`, with
    the full text kept alongside so the experiment folder stays readable on its own and
    `_view.py` / `_doc.py` keep working unchanged. The canonical record, with both
    prompts verbatim and every setting, is written to characters/.
    """
    name, name_user = supplied_name, None
    if name_prompt and not supplied_name:
        name, name_user = make_name(name_prompt=name_prompt, model=name_model,
                                    temperature=name_temperature, age=age, gender=gender)
        if not name:
            return {"error": f"name call failed: {name_user}", "index": index, "arm": arm}

    user = (user_template.replace("{NAME}", name or "")
                         .replace("{AGE}", str(age))
                         .replace("{GENDER}", gender))
    if other_name and other_bio:
        from game_state import prompts as p_mod
        block = (assembly._reload_prompts().characterFullAntiDuplicationBlock
                 .replace("{OTHER_NAME}", other_name).replace("{OTHER_BIO}", other_bio))
        user += "\n\n" + block

    body = {"model": model, "temperature": temperature, "provider": "hf",
            "timeout": proxy_timeout,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort

    text, usage, seconds, why, tries = "", {}, None, "not called", 0
    for tries in range(1, attempts + 1):
        try:
            t0 = time.time()
            r = _post(body, timeout)
            seconds = round(time.time() - t0, 1)
            if r.status_code != 200:
                why = f"HTTP {r.status_code}"
                time.sleep(5)
                continue
            d = r.json()
            usage = d.get("usage") or {}
            text = assembly.strip_reasoning(d["choices"][0]["message"]["content"]).strip()
            ok, why = assembly.generation_is_usable(text)
            if ok:
                break
        except Exception as e:
            why = type(e).__name__
            time.sleep(5)
    else:
        if not text:
            return {"error": why, "index": index, "arm": arm}

    settings = {
        "generation_model": model, "generation_temperature": temperature,
        "generation_max_tokens": max_tokens, "reasoning_effort": reasoning_effort,
        "proxy_timeout": proxy_timeout, "provider": "hf",
        "name_model": name_model, "name_temperature": name_temperature,
    }
    char_id = None
    if write_record:
        origin = {"experiment": experiment, "index": index}
        if arm:
            origin["arm"] = arm
        rec = library.new_record(
            character={"name": name or "", "description": text,
                       "gender": gender, "age": int(age), "info_shared": []},
            provenance={
                "source": "experiment",
                "origin": origin,
                "game_state_version": _current_version_name(),
                "drift_at_generation": [],
                "gen_session_id": None,
                "settings": settings,
                # Both verbatim, including the anti-duplication block if one was used.
                "prompts": {"character_system": system, "character_user": user,
                            "name_user": name_user},
                "prompts_source": "recorded at generation",
                "anti_duplication": {"used": bool(other_name), "other_char_id": None},
                "usable": True, "sanity": why, "attempts": tries,
                "words": len(text.split()), "derived_from": None, "complete": True,
            },
            calls=[],
            tags=[experiment.split("_")[0]],
        )
        library.write_character(rec)
        char_id = rec["char_id"]

    row = {"char_id": char_id, "index": index, "arm": arm,
           "age": age, "gender": gender, "supplied_name": name,
           "seconds": seconds, "tokens": usage.get("total_tokens"),
           "completion_tokens": usage.get("completion_tokens"),
           "words": len(text.split()), "attempts": tries, "sanity": why,
           "text": text}
    row.update(extra or {})
    return row


def _current_version_name():
    try:
        from save_version import current_version
        c = current_version()
        return c.name if c else None
    except Exception:
        return None


def write_manifest(folder, arms: dict, inputs=None, notes=""):
    """
    `prompts.json` in the experiment folder: every prompt and setting, once per arm.

    The character records each carry their own verbatim copy because they are
    standalone; this is so the experiment folder alone answers "what was sent", which
    it could not before.
    """
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "prompts.json").write_text(json.dumps({
        "experiment": folder.name,
        "game_state_version": _current_version_name(),
        "written_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "inputs": inputs or [],
        "notes": notes,
        "arms": arms,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    return folder / "prompts.json"
