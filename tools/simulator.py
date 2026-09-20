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
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Optional

from _paths import GAME_STATE, OUTPUTS  # noqa: F401 -- also puts PROJECT_ROOT on sys.path
from game_state import config, providers, assembly, game


# ──────────────────────────────────────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────────────────────────────────────

OUTPUT_DIR = OUTPUTS
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TRANSCRIPT_CSV = OUTPUT_DIR / "transcript.csv"
TRANSCRIPT_JSON = OUTPUT_DIR / "transcript.json"
EDITS_CSV = OUTPUT_DIR / "edits.csv"
STATE_JSON = OUTPUT_DIR / "session_state.json"


# ──────────────────────────────────────────────────────────────────────────────
# TRANSCRIPT WRITING
# ──────────────────────────────────────────────────────────────────────────────

_TRANSCRIPT_HEADERS = [
    "timestamp", "session_id", "turn_number", "call_type",
    "character_no", "model", "temperature", "max_tokens",
    "system_prompt", "user_prompt", "response", "notes",
    # ── metadata captured from providers.CallResult ──
    "requested_model", "served_model",
    "prompt_tokens", "completion_tokens", "total_tokens", "cached_tokens",
    "finish_reason", "response_time_s", "retry_count", "cold_start", "endpoint",
]


def _init_transcript_files():
    """Create transcript files with headers if they don't exist."""
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
        datetime.utcnow().isoformat(),
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
            datetime.utcnow().isoformat(),
            prompt_name,
            old_text,
            new_text,
        ])


def save_state_snapshot(state: game.GameState):
    """Write current state to session_state.json for resumption / export."""
    snap = {
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
                "cause_of_death": char.cause_of_death,
                "who_loved": char.who_loved,
                "who_hated": char.who_hated,
                "prose_body": char.prose_body,
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
    STATE_JSON.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")


# ──────────────────────────────────────────────────────────────────────────────
# CHARACTER GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def generate_character(state: game.GameState, char_no: int) -> dict:
    """
    Generate one character in a single call.

    Replaces the former four-call chain (name -> life -> sin -> stance): every field
    now comes back in one response, ordered so that each is written knowing the ones
    above it. Character 2 still runs after Character 1 and sees its finished bio.
    Mirrors CharacterGenerator.GenerateCharacter.
    """
    if char_no not in (1, 2):
        raise ValueError(f"char_no must be 1 or 2, got {char_no}")

    gender = config.CHARACTER_GENDERS[char_no]
    age = random.randint(*config.AGE_RANGE)
    # Randomising the naming tradition is what breaks the model's strong name prior --
    # instructing it to vary names failed across three versions. Same pattern as AGE_RANGE.
    name_origin = random.choice(config.NAME_ORIGINS)

    # Determine anti-duplication inputs (Char 2 sees Char 1's finished character)
    other_char = state.characters.get(1) if char_no == 2 else None
    if char_no == 2 and (other_char is None or not other_char.occupation):
        raise RuntimeError("Cannot generate Character 2 before Character 1 is fully generated.")

    summary = {"char_no": char_no, "gender": gender, "age": age, "name_origin": name_origin}

    # ── Single generation call ──
    char_kwargs = dict(name_origin=name_origin, age=age, gender=gender)
    if char_no == 2:
        char_kwargs["other_name"] = other_char.name
        char_kwargs["other_bio"] = other_char.description

    sys_p, user_p = assembly.assemble_character_prompts(**char_kwargs)
    _response, parsed = _call_with_parse_retry(
        sys_p, user_p, char_no, "character",
        config.MODEL_GENERATION, config.TEMP_GENERATION, 0,
        state, assembly.parse_character_response, assembly.character_parse_complete,
    )

    def field(key):
        return parsed.get(key) or "[generation failed]"

    name = field("name")
    occupation = field("occupation")
    cause_of_death = field("cause_of_death")
    who_loved = field("who_loved")
    who_hated = field("who_hated")
    prose_body = field("prose_body")
    reason_true = field("reason_true")
    reason_self_told = field("reason_self_told")
    refuse_to_admit = field("refuse_to_admit")
    personality_trait = field("personality_trait")
    want = field("want")

    summary.update(name=name, occupation=occupation, cause_of_death=cause_of_death,
                   personality_trait=personality_trait, want=want)

    # ── Assemble bio & store ──
    bio = assembly.assemble_bio(
        occupation=occupation,
        cause_of_death=cause_of_death,
        who_loved=who_loved,
        who_hated=who_hated,
        reason_true=reason_true,
        reason_self_told=reason_self_told,
        personality_trait=personality_trait,
        refuse_to_admit=refuse_to_admit,
        want=want,
        prose_body=prose_body,
    )

    state.characters[char_no] = game.Character(
        name=name,
        description=bio,
        gender=gender,
        age=age,
        occupation=occupation,
        cause_of_death=cause_of_death,
        who_loved=who_loved,
        who_hated=who_hated,
        prose_body=prose_body,
        reason_true=reason_true,
        reason_self_told=reason_self_told,
        refuse_to_admit=refuse_to_admit,
        personality_trait=personality_trait,
        want=want,
    )

    if 1 in state.characters and 2 in state.characters \
       and state.characters[1].description and state.characters[2].description:
        state.characters_generated = True

    save_state_snapshot(state)
    return summary


def _call_with_parse_retry(
    sys_p, user_p, char_no, call_label,
    model, temperature, max_tokens,
    state, parse_fn, complete_check_fn,
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
      "addressing_decision": Optional[str],  # "0"/"1"/"2"/"3" or None
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
        # "3" not currently mapped (would be narrator); ignore for now

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
        if any(c in reply for c in ("0", "1", "2")):
            # Match Unity behavior: first matching digit wins
            for c in ("0", "1", "2"):
                if c in reply:
                    return c
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

    # Always re-emit as a triple-quoted literal; refuse rather than produce a file
    # that will not parse.
    if '"""' in new_text or new_text.endswith('"') or new_text.endswith("\\"):
        return False, "New text contains a triple quote, or ends in a quote or backslash -- cannot be written safely."
    literal = f'"""{new_text}"""'.encode("utf-8")

    PROMPTS_FILE.write_bytes(raw[:start] + literal + raw[end:])
    log_edit(prompt_name, old_text, new_text)
    return True, f"Prompt '{prompt_name}' updated. Next call will use the new content."


# ──────────────────────────────────────────────────────────────────────────────
# SESSION SETUP HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def new_session() -> game.GameState:
    """Create a fresh GameState and reset transcript files for the new session."""
    # Don't clobber prior transcripts — append session_id to filename if exists
    return game.GameState()


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
        state.characters[cid] = game.Character(**cdata)
    state.dialogue_entries = [
        game.DialogueEntry(**e) for e in snap.get("dialogue_entries", [])
    ]
    return state