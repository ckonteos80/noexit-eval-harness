"""
Main simulator. Provides functions Claude calls to:
- Set up a session
- Run character generation
- Run the narrator opening
- Run a player turn (info extraction + addressing + dialogue + info extraction)
- Manage state (restart, clear, regenerate)
- Edit prompts
- Read state for display

Designed to be called from Claude in the sandbox, one operation at a time.
"""

import ast
import csv
import dataclasses
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from _paths import GAME_STATE, OUTPUTS  # noqa: F401 -- also puts PROJECT_ROOT on sys.path
from game_state import config, providers, assembly, game


# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────

# A chained character-2 call carries the other character's whole bio and runs far longer
# than a standalone one. Shorter than config.PROXY_TIMEOUT_GENERATION on purpose: past the
# HF router's ~120s ceiling the call is lost anyway, so failing at 110s reports the problem
# instead of holding the request open for minutes. Harness-side: Unity has no equivalent,
# so this stays out of game_state/.
PROXY_TIMEOUT_ANTI_DUP = 110

# What the last sanity check concluded, so a caller can record it rather than assume
# "ok". Written by _call_with_sanity_retry, read immediately after by its caller.
_LAST_SANITY = {"why": None, "attempts": None}

OUTPUT_DIR = OUTPUTS
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRANSCRIPT_CSV = OUTPUT_DIR / "transcript.csv"
TRANSCRIPT_JSON = OUTPUT_DIR / "transcript.json"
EDITS_CSV = OUTPUT_DIR / "edits.csv"
STATE_JSON = OUTPUT_DIR / "session_state.json"


# ──────────────────────────────────────────────────────────────────────────────
# TRANSCRIPT WRITING
# ──────────────────────────────────────────────────────────────────────────────

def _utc_now_iso() -> str:
    """
    UTC timestamp in the exact format utcnow().isoformat() produced.

    utcnow() is deprecated, but the naive (offset-free) shape is kept on purpose:
    run_viewer sorts these as plain strings, and the whole run history is stored
    this way. Switching to an offset-bearing format would mix two shapes.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


_TRANSCRIPT_HEADERS = [
    "timestamp", "session_id", "turn_number", "call_type",
    "character_no", "model", "temperature", "max_tokens",
    "system_prompt", "user_prompt", "response", "notes",
    # ── metadata captured from providers.CallResult ──
    "requested_model", "served_model",
    "prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens",
    "finish_reason", "response_time_s", "retry_count", "cold_start", "endpoint",
    "proxy_timeout",
]


def _init_transcript_files():
    """Create transcript files with headers if they don't exist."""
    # A column added to _TRANSCRIPT_HEADERS makes every new row one field wider than
    # the header already written at the top of an existing file. Nothing parses this
    # CSV today, but a silently ragged file is worse than a rotated one -- and this
    # directory is scratch, so rotating costs nothing.
    if TRANSCRIPT_CSV.exists():
        with open(TRANSCRIPT_CSV, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f), None)
        if header != _TRANSCRIPT_HEADERS:
            stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            TRANSCRIPT_CSV.replace(TRANSCRIPT_CSV.with_name(f"transcript.pre-{stamp}.csv"))
    if not TRANSCRIPT_CSV.exists():
        with open(TRANSCRIPT_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(_TRANSCRIPT_HEADERS)
    if not TRANSCRIPT_JSON.exists():
        TRANSCRIPT_JSON.write_text("[]", encoding="utf-8")
    if not EDITS_CSV.exists():
        with open(EDITS_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["timestamp", "prompt_name", "old_text", "new_text"])


def log_call(
    state: game.GameState,
    call_type: str,
    character_no: int,
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str,
    user_prompt: str,
    response: str,
    notes: str = "",
    meta: "providers.CallResult" = None,
):
    """
    Append one LLM call to the transcript CSV and JSON.

    `meta` is the providers.CallResult for this call; when provided, its metadata
    (tokens, response time, retries, requested/served model, finish_reason) is
    stored alongside the prompts and response. None for calls with no CallResult.
    """
    _init_transcript_files()

    m = meta.to_dict() if meta is not None else {}
    row = [
        _utc_now_iso(),
        state.session_id,
        state.turn_count,
        call_type,
        character_no,
        model,
        temperature,
        max_tokens,
        system_prompt,
        user_prompt,
        response,
        notes,
        m.get("requested_model"),
        m.get("served_model"),
        m.get("prompt_tokens"),
        m.get("completion_tokens"),
        m.get("total_tokens"),
        m.get("cached_tokens"),
        m.get("finish_reason"),
        m.get("response_time_s"),
        m.get("retry_count"),
        m.get("cold_start"),
        m.get("endpoint"),
        m.get("proxy_timeout"),
    ]

    with open(TRANSCRIPT_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)

    # JSON append
    try:
        existing = json.loads(TRANSCRIPT_JSON.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, FileNotFoundError):
        existing = []
    existing.append(dict(zip(_TRANSCRIPT_HEADERS, row)))
    TRANSCRIPT_JSON.write_text(json.dumps(existing, indent=2, ensure_ascii=False), encoding="utf-8")


def log_edit(prompt_name: str, old_text: str, new_text: str):
    """Log a prompt edit to edits.csv."""
    _init_transcript_files()
    with open(EDITS_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            _utc_now_iso(),
            prompt_name,
            old_text,
            new_text,
        ])


def state_snapshot_dict(state: game.GameState) -> dict:
    """
    The session snapshot, as a dict.

    Split out from save_state_snapshot so a run can be saved from the session in
    memory rather than by reading session_state.json back off disk. The disk file is
    only written by the three generation/turn functions, so a session that did not go
    through them -- one seated from the character library -- would otherwise save the
    PREVIOUS session's snapshot as its own.
    """
    return {
        "session_id": state.session_id,
        "session_started": state.session_started,
        "turn_count": state.turn_count,
        "characters_generated": state.characters_generated,
        "narrator_played": state.narrator_played,
        "characters": {
            str(cid): {
                "name": char.name,
                "description": char.description,
                "gender": char.gender,
                "age": char.age,
                "info_shared": char.info_shared,
                "occupation": char.occupation,
                "prose_body": char.prose_body,
                "people": char.people,
                "reason_true": char.reason_true,
                "reason_self_told": char.reason_self_told,
                "refuse_to_admit": char.refuse_to_admit,
                "personality_trait": char.personality_trait,
                "want": char.want,
            }
            for cid, char in state.characters.items()
        },
        "dialogue_entries": [
            {
                "character_id": e.character_id,
                "character_label": e.character_label,
                "dialogue_text": e.dialogue_text,
                "timestamp": e.timestamp,
            }
            for e in state.dialogue_entries
        ],
    }


def save_state_snapshot(state: game.GameState):
    """Write current state to session_state.json for resumption / export."""
    snap = state_snapshot_dict(state)
    STATE_JSON.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# CHARACTER GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def generate_character_core(state, *, gender, age=None, other=None, slot=1,
                            anti_dup=False, settings=None) -> dict:
    """
    One character, generated and returned. Writes NOTHING to state or to disk.

    Split out of generate_character so the library can generate without touching the
    live session: the old function assigns into state.characters and calls
    save_state_snapshot, so a batch of ten would have overwritten the snapshot that a
    running session depends on, ten times.

    `state` is still needed, but only as a logging vehicle -- log_call reads its
    session_id and turn_count. Pass a throwaway session for library work.

    Returns everything the caller needs to build either a game.Character or a library
    record: the name, the bio, and the prompts verbatim.
    """
    st = settings or {}
    age = int(st.get("age") or age or random.randint(*config.AGE_RANGE))
    name = _generate_name(state, slot, age, gender, settings=st)

    char_kwargs = dict(name=name, age=age, gender=gender)
    if anti_dup and other:
        char_kwargs["other_name"], char_kwargs["other_bio"] = other

    sys_p, user_p = assembly.assemble_character_prompts(**char_kwargs)

    # Prompt overrides from the UI. Editing prompts.py would work too -- it is
    # hot-reloaded -- but that file is game_state/, so every edit creates drift and
    # then blocks saving behind the version guard. An override is recorded verbatim in
    # the character record instead, which is what makes it attributable without a
    # snapshot.
    if st.get("system_prompt"):
        sys_p = st["system_prompt"]
    if st.get("user_prompt"):
        user_p = (st["user_prompt"].replace("{NAME}", name)
                                   .replace("{AGE}", str(age))
                                   .replace("{GENDER}", gender))
        if anti_dup and other:
            p = assembly._reload_prompts()
            user_p += "\n\n" + (p.characterFullAntiDuplicationBlock
                                 .replace("{OTHER_NAME}", other[0])
                                 .replace("{OTHER_BIO}", other[1]))

    # A chained call is the slow one, so give it a shorter leash: it fails visibly
    # rather than holding the request open for several minutes.
    bio = _call_with_sanity_retry(
        sys_p, user_p, slot, state,
        proxy_timeout=PROXY_TIMEOUT_ANTI_DUP if (anti_dup and other) else None,
        settings=st,
    )
    return {
        "name": name, "age": age, "gender": gender, "bio": bio,
        "words": len(bio.split()),
        "system_prompt": sys_p, "user_prompt": user_p,
        "anti_dup": bool(anti_dup and other),
        "prompts_overridden": bool(st.get("system_prompt") or st.get("user_prompt")
                                   or st.get("name_prompt")),
        "sanity": _LAST_SANITY["why"],
        "attempts": _LAST_SANITY["attempts"],
    }


def generate_character(state: game.GameState, char_no: int, anti_dup: bool = False,
                       settings: Optional[dict] = None) -> dict:
    """
    Generate one character into a session, as the game does.

    A thin wrapper over generate_character_core: this one owns the 1/2 slot rules, the
    gender map, the character-2 precondition, and the writes to state and disk.
    Mirrors CharacterGenerator.GenerateCharacter.
    """
    if char_no not in (1, 2):
        raise ValueError(f"char_no must be 1 or 2, got {char_no}")

    # settings is a plain dict of per-request overrides from the UI; every key is
    # optional and absent means "use config". A dict rather than a dataclass because it
    # crosses a JSON boundary either way.
    st = settings or {}
    gender = st.get("gender") or config.CHARACTER_GENDERS[char_no]

    # Character 2 sees character 1's finished story. Gated on the bio rather than on an
    # occupation field: there are no fields now.
    other_char = state.characters.get(1) if char_no == 2 else None
    if char_no == 2 and (other_char is None or not other_char.description):
        raise RuntimeError("Cannot generate Character 2 before Character 1 is fully generated.")

    made = generate_character_core(
        state, gender=gender, slot=char_no, settings=st, anti_dup=anti_dup,
        other=((other_char.name, other_char.description) if other_char else None),
    )

    # The story is the bio. Nothing parses it into fields; the per-field columns on
    # Character stay empty from this version on.
    state.characters[char_no] = game.Character(
        name=made["name"], description=made["bio"],
        gender=made["gender"], age=made["age"],
    )

    if 1 in state.characters and 2 in state.characters \
       and state.characters[1].description and state.characters[2].description:
        state.characters_generated = True

    save_state_snapshot(state)
    return {"char_no": char_no, "gender": made["gender"], "age": made["age"],
            "name": made["name"], "words": made["words"]}


def _generate_name(state: game.GameState, char_no: int, age: int, gender: str,
                   settings: Optional[dict] = None) -> str:
    """
    The name call. A story adopts a supplied name about half the time wherever the
    name sits in the prompt (experiments 18, 19), so the supplied value is what
    {NAME} uses downstream whether or not the prose repeats it.

    Known limitation: this call is the source of the name collisions -- ten names in
    experiment 19 gave nine beginning with E. It is reliable, not varied. Swapping it
    for a random draw in code is a one-function change.
    """
    st_name = (settings or {}).get("name_prompt")
    template = st_name or assembly._reload_prompts().characterNamePrompt
    user = template.replace("{AGE}", str(age)).replace("{GENDER}", gender)
    st = settings or {}
    model = st.get("name_model") or config.MODEL_NAME
    temp = st.get("name_temperature")
    temp = config.TEMP_NAME if temp is None else float(temp)
    res = providers.call_proxy("", user, model=model, temperature=temp, max_tokens=0)
    name = assembly.strip_reasoning(res.content or "").strip().strip('."\u201c\u201d')
    # log_call's model/temperature are positional: pass the values actually used, or the
    # transcript will disagree with CallResult.requested_model about what was called.
    log_call(state, "name", char_no, model, temp, 0, "", user, name, meta=res)
    if not name:
        raise RuntimeError("Name call returned nothing.")
    return name


def _call_with_sanity_retry(sys_p, user_p, char_no, state, proxy_timeout=None,
                            settings=None) -> str:
    """
    Call the proxy for the story and return it whole, after strip_reasoning.

    Retries while the response fails assembly.generation_is_usable -- the response is
    used without parsing, so this is the only thing standing between a bad generation
    and the dialogue system prompt.
    """
    st = settings or {}
    custom_prompts = bool(st.get("system_prompt") or st.get("user_prompt"))
    model = st.get("generation_model") or config.MODEL_GENERATION
    temp = st.get("generation_temperature")
    temp = config.TEMP_GENERATION if temp is None else float(temp)
    effort = st.get("reasoning_effort") or config.REASONING_EFFORT_GENERATION
    max_tokens = config.MAX_TOKENS_GENERATION

    response, res, why = "", None, "not called"
    for attempt in range(config.PARSE_RETRY_ATTEMPTS):
        res = providers.call_proxy(
            sys_p, user_p,
            model=model, temperature=temp, max_tokens=max_tokens,
            proxy_timeout=proxy_timeout or config.PROXY_TIMEOUT_GENERATION,
            reasoning_effort=effort,
        )
        response = assembly.strip_reasoning(res.content or "").strip()
        ok, why = assembly.generation_is_usable(response)
        # The word range in generation_is_usable is calibrated to the 300-word prompt.
        # A custom prompt may legitimately ask for 120 words or 500, so a length-only
        # failure is not a failure when the caller wrote the prompt. The second-person
        # and <think> checks still apply: those are about the harness, not the brief.
        if not ok and custom_prompts and "words, outside" in why:
            ok, why = True, why + " (allowed: custom prompt)"
        log_call(state, "character", char_no, model, temp, max_tokens,
                 sys_p, user_p, response,
                 notes=f"attempt {attempt + 1}: {why}", meta=res)
        if ok:
            _LAST_SANITY["why"], _LAST_SANITY["attempts"] = why, attempt + 1
            return response
    log_call(state, "character", char_no, model, temp, max_tokens, sys_p, user_p, response,
             notes=f"UNUSABLE after {config.PARSE_RETRY_ATTEMPTS} attempts: {why}", meta=res)
    _LAST_SANITY["why"] = f"UNUSABLE: {why}"
    _LAST_SANITY["attempts"] = config.PARSE_RETRY_ATTEMPTS
    return response


def _call_with_parse_retry(
    sys_p, user_p, char_no, call_label,
    model, temperature, max_tokens,
    state, parse_fn, complete_check_fn,
    proxy_timeout=None,
):
    """
    Call the proxy and parse the response. Retry once on incomplete parse.
    Returns (response_text, parsed_dict).
    """
    parsed = {}
    response = ""
    res = None
    for attempt in range(config.PARSE_RETRY_ATTEMPTS):
        res = providers.call_proxy(
            sys_p, user_p, model=model, temperature=temperature, max_tokens=max_tokens,
            proxy_timeout=proxy_timeout,
        )
        response = res.content
        log_call(state, call_label, char_no, model, temperature, max_tokens, sys_p, user_p, response,
                 notes=f"attempt {attempt + 1}", meta=res)
        parsed = parse_fn(response)
        if complete_check_fn(parsed):
            return response, parsed
    # Final failure
    log_call(state, call_label, char_no, model, temperature, max_tokens, sys_p, user_p, response,
             notes=f"PARSE FAILED after {config.PARSE_RETRY_ATTEMPTS} attempts", meta=res)
    return response, parsed


# ──────────────────────────────────────────────────────────────────────────────
# NARRATOR
# ──────────────────────────────────────────────────────────────────────────────

def run_narrator(state: game.GameState) -> str:
    """Run the narrator opening call. Returns the narrator's line."""
    sys_p, user_p = assembly.get_narrator_prompts()
    res = providers.call_proxy(
        sys_p, user_p,
        model=config.MODEL_NARRATOR,
        temperature=config.TEMP_NARRATOR,
        max_tokens=config.MAX_TOKENS_NARRATOR,
    )
    reply = res.content
    log_call(state, "narrator", 3, config.MODEL_NARRATOR, config.TEMP_NARRATOR,
             config.MAX_TOKENS_NARRATOR, sys_p, user_p, reply, meta=res)
    game.log_dialogue(state, character_id=3, text=reply)
    state.narrator_played = True
    save_state_snapshot(state)
    return reply


# ──────────────────────────────────────────────────────────────────────────────
# PLAYER TURN
# ──────────────────────────────────────────────────────────────────────────────

def run_player_turn(state: game.GameState, player_message: str) -> dict:
    """
    Process one player turn. Mirrors CharacterController.ParsedText.

    Returns a dict with everything that happened, for chat display:
    {
      "player_message": str,
      "extracted_from_player": str,  # "none" or extracted info
      "addressing_called": bool,
      "addressing_decision": Optional[str],  # "0"/"1"/"2" or None
      "replies": [
          {"char_no": 1, "text": "...", "extracted": "name: Alex" | "none"},
          ...
      ],
    }
    """
    state.turn_count += 1
    result = {
        "player_message": player_message,
        "extracted_from_player": "none",
        "addressing_called": False,
        "addressing_decision": None,
        "replies": [],
    }

    # Log player dialogue
    game.log_dialogue(state, character_id=0, text=player_message)

    # ── Info extraction on player message ──
    info_sys = assembly.get_info_extraction_system_prompt()
    extract_res = providers.call_info_extractor(player_message, info_sys)
    extracted = extract_res.content
    log_call(state, "info_extraction", 0, "info-extractor", 0.0, 0,
             info_sys, player_message, extracted, notes="on player message", meta=extract_res)
    result["extracted_from_player"] = extracted
    if extracted.lower() != "none":
        game.add_info(state, 0, extracted)

    # ── Decide who replies (mirrors ParsedText logic) ──
    char1 = state.characters.get(1)
    char2 = state.characters.get(2)
    has_info_1 = bool(char1 and char1.info_shared)
    has_info_2 = bool(char2 and char2.info_shared)

    replying_char_ids = []
    if not has_info_1 and not has_info_2:
        # No info yet → both characters respond
        replying_char_ids = [1]
        if char2:  # Mirrors `Characters[2].gameObject.activeSelf`
            replying_char_ids.append(2)
    else:
        # Run addressing call
        result["addressing_called"] = True
        addressing_decision = _run_addressing(state, player_message)
        result["addressing_decision"] = addressing_decision
        if addressing_decision == "0":
            replying_char_ids = [1, 2]
        elif addressing_decision == "1":
            replying_char_ids = [1]
        elif addressing_decision == "2":
            replying_char_ids = [2]
        # Nothing else is reachable: _run_addressing only ever returns "0"/"1"/"2".

    # ── Run each replying character ──
    for char_id in replying_char_ids:
        reply_result = _run_character_reply(state, char_id, player_message)
        result["replies"].append(reply_result)

    save_state_snapshot(state)
    return result


def _run_addressing(state: game.GameState, player_message: str) -> str:
    """Run the addressing call with up to 3 retries on invalid output."""
    char1 = state.characters.get(1)
    char2 = state.characters.get(2)
    char1_info = char1.info_shared if char1 else []
    char2_info = char2.info_shared if char2 else []
    latest_context = game.get_latest_dialogues_context(state)

    sys_p = assembly.assemble_addressing_system_prompt(char1_info, char2_info, latest_context)

    for attempt in range(3):
        res = providers.call_proxy(
            sys_p, player_message,
            model=config.MODEL_ADDRESSING,
            temperature=config.TEMP_ADDRESSING,
            max_tokens=config.MAX_TOKENS_ADDRESSING,
        )
        reply = res.content
        log_call(state, "addressing", 0, config.MODEL_ADDRESSING, config.TEMP_ADDRESSING,
                 config.MAX_TOKENS_ADDRESSING, sys_p, player_message, reply,
                 notes=f"attempt {attempt + 1}", meta=res)
        # The prompt asks for exactly one digit, so validate rather than extract.
        # The previous version scanned for any of "0"/"1"/"2" anywhere in the reply
        # and returned the lowest one present, so a malformed reply like "2, not 0"
        # silently became "0" instead of being retried.
        choice = reply.strip()
        if choice in ("0", "1", "2"):
            return choice
    # Fallback: "0" (both respond)
    log_call(state, "addressing", 0, config.MODEL_ADDRESSING, config.TEMP_ADDRESSING,
             config.MAX_TOKENS_ADDRESSING, sys_p, player_message, "",
             notes="all attempts invalid, falling back to 0")
    return "0"


def _run_character_reply(state: game.GameState, char_id: int, player_message: str) -> dict:
    """Run one character's reply call + info extraction on the reply."""
    char = state.characters[char_id]

    # Build dialogue user message
    p1_idx, p2_idx = game.get_person_mapping(char_id)
    info_p1 = state.characters[p1_idx].info_shared if p1_idx in state.characters else []
    info_p2 = state.characters[p2_idx].info_shared if p2_idx in state.characters else []
    recent_dialogue = game.format_dialogue_for_character(state, char_id)
    speaker_person_no = game.get_person_number_for(char_id, 0)  # player is speaking

    user_msg = assembly.assemble_dialogue_user_message(
        info_other_1=info_p1,
        info_other_2=info_p2,
        recent_dialogue_formatted=recent_dialogue,
        speaker_person_no=speaker_person_no,
        player_message=player_message,
    )

    sys_p = assembly.assemble_dialogue_system_prompt(char.name, char.description)

    res = providers.call_proxy(
        sys_p, user_msg,
        model=config.MODEL_DIALOGUE,
        temperature=config.TEMP_DIALOGUE,
        max_tokens=config.MAX_TOKENS_DIALOGUE,
    )
    reply = res.content
    log_call(state, "dialogue", char_id, config.MODEL_DIALOGUE, config.TEMP_DIALOGUE,
             config.MAX_TOKENS_DIALOGUE, sys_p, user_msg, reply, meta=res)

    game.log_dialogue(state, character_id=char_id, text=reply)

    # Info extraction on the reply
    info_sys = assembly.get_info_extraction_system_prompt()
    extract_res = providers.call_info_extractor(reply, info_sys)
    extracted = extract_res.content
    log_call(state, "info_extraction", char_id, "info-extractor", 0.0, 0,
             info_sys, reply, extracted, notes=f"on Char {char_id} reply", meta=extract_res)
    if extracted.lower() != "none":
        game.add_info(state, char_id, extracted)

    return {"char_no": char_id, "text": reply, "extracted": extracted}


# ──────────────────────────────────────────────────────────────────────────────
# PROMPT EDITING
# ──────────────────────────────────────────────────────────────────────────────

PROMPTS_FILE = GAME_STATE / "prompts.py"


def get_prompt_value(prompt_name: str) -> Optional[str]:
    """Read a prompt's current value by reloading the module."""
    import importlib
    from game_state import prompts as p_mod
    importlib.reload(p_mod)
    return getattr(p_mod, prompt_name, None)


def apply_prompt_edit(prompt_name: str, new_text: str) -> tuple[bool, str]:
    """
    Replace a prompt's value in prompts.py.

    Locates the assignment with ast rather than a regex, so quote style does not
    matter -- the old regex matched triple-quoted strings only and silently failed
    on adressingSystemPromptContext and narratorUserPrompt, the two single-quoted
    prompts. (Same class of bug that hid those fields from every DIFF.md until
    save_version.parse_prompt_fields moved to ast.)

    Offsets are computed against the UTF-8 bytes because ast.col_offset is a byte
    offset, and these prompts contain em-dashes.

    Side effect: the value is always re-emitted triple-quoted, so editing one of
    the single-quoted prompts converts it. The value is unchanged, so DIFF.md
    reports the file as changed with no field-level difference.

    Returns (success, message). On success the new text is live for the next call.
    """
    old_text = get_prompt_value(prompt_name)
    if old_text is None:
        return False, f"No prompt named '{prompt_name}' found in prompts.py."

    raw = PROMPTS_FILE.read_bytes()
    try:
        tree = ast.parse(raw.decode("utf-8"))
    except SyntaxError as e:
        return False, f"prompts.py does not parse: {e}"

    target = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            continue
        if any(isinstance(t, ast.Name) and t.id == prompt_name for t in node.targets):
            target = node.value

    if target is None:
        return False, f"Could not locate assignment for '{prompt_name}' in prompts.py."

    lines = raw.splitlines(keepends=True)
    start = sum(len(l) for l in lines[:target.lineno - 1]) + target.col_offset
    end = sum(len(l) for l in lines[:target.end_lineno - 1]) + target.end_col_offset

    # Re-emit as a triple-quoted literal. Backslashes must be escaped or Python
    # interprets them on reload -- writing a windows path would silently turn
    # \t into a tab. Only a literal triple quote or a trailing quote remain
    # unwritable, and those are refused rather than guessed at.
    if '"""' in new_text or new_text.endswith('"'):
        return False, ("New text contains a triple quote, or ends in a quote "
                       "-- cannot be written safely.")
    literal = f'"""{new_text.replace(chr(92), chr(92) * 2)}"""'.encode("utf-8")

    updated = raw[:start] + literal + raw[end:]
    PROMPTS_FILE.write_bytes(updated)

    # Verify the file still parses and the value round-tripped; roll back if not.
    # This file is imported on every call, so a bad write breaks the whole session.
    if get_prompt_value(prompt_name) != new_text:
        PROMPTS_FILE.write_bytes(raw)
        get_prompt_value(prompt_name)  # reload the restored module
        return False, f"Write did not round-trip for '{prompt_name}' -- prompts.py restored unchanged."

    log_edit(prompt_name, old_text, new_text)
    return True, f"Prompt '{prompt_name}' updated. Next call will use the new content."


# ──────────────────────────────────────────────────────────────────────────────
# SESSION SETUP HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def new_session() -> game.GameState:
    """Create a fresh GameState and reset transcript files for the new session."""
    # Don't clobber prior transcripts — append session_id to filename if exists
    return game.GameState()


def character_from_dict(d: dict) -> game.Character:
    """
    A game.Character from any dict carrying at least some of its fields, ignoring
    everything else.

    game.Character(**d) cannot load a run JSON, for two reasons that are easy to miss:
    ui/run_viewer.html writes `eval` and `eval_ai` back into each character, and runs
    from before 2026-09-27 carry cause_of_death / who_loved / who_hated, fields the
    nine-field rewrite removed. Either raises TypeError.
    """
    names = {f.name for f in dataclasses.fields(game.Character)}
    kw = {k: v for k, v in d.items() if k in names}
    kw["age"] = int(kw.get("age") or 0)
    kw["info_shared"] = list(kw.get("info_shared") or [])
    return game.Character(**kw)


def load_state_from_snapshot(snap: dict) -> game.GameState:
    """Rehydrate GameState from a session_state.json dict."""
    state = game.GameState(
        session_id=snap["session_id"],
        session_started=snap["session_started"],
        turn_count=snap.get("turn_count", 0),
        characters_generated=snap.get("characters_generated", False),
        narrator_played=snap.get("narrator_played", False),
    )
    state.characters = {}
    for cid_str, cdata in snap["characters"].items():
        cid = int(cid_str)
        state.characters[cid] = character_from_dict(cdata)
    state.dialogue_entries = [
        game.DialogueEntry(**e) for e in snap.get("dialogue_entries", [])
    ]
    return state