"""
Prompt assembly logic mirroring CharacterController.cs and CharacterGenerator.cs.

Pure functions — no I/O, no state. Given inputs, return the assembled strings.
"""

from typing import Optional
import importlib


def _reload_prompts():
    """Reload prompts module to pick up edits made during the session."""
    from game_state import prompts
    importlib.reload(prompts)
    return prompts


# ──────────────────────────────────────────────────────────────────────────────
# CHARACTER GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def assemble_name_prompts(gender: str) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the name generation call."""
    p = _reload_prompts()
    system = p.characterSetupSystemPrompt
    user = p.characterNameUserPrompt + " " + p.characterNameGenderSuffix.format(gender)
    return system, user


def assemble_life_prompts(
    name: str,
    age: int,
    gender: str,
    other_occupation: Optional[str] = None,
    other_cause_of_death: Optional[str] = None,
    other_who_loved: Optional[str] = None,
    other_who_hated: Optional[str] = None,
) -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) for the Life call.
    If other_* args are provided, appends the anti-duplication block (Character 2).
    """
    p = _reload_prompts()
    system = p.characterSetupSystemPrompt
    user = (p.characterLifeUserPrompt
            .replace("{NAME}", name)
            .replace("{AGE}", str(age))
            .replace("{GENDER}", gender))

    if other_occupation is not None and other_cause_of_death is not None \
            and other_who_loved is not None and other_who_hated is not None:
        block = (p.characterLifeAntiDuplicationBlock
                 .replace("{OTHER_OCCUPATION}", other_occupation)
                 .replace("{OTHER_CAUSE_OF_DEATH}", other_cause_of_death)
                 .replace("{OTHER_WHO_LOVED}", other_who_loved)
                 .replace("{OTHER_WHO_HATED}", other_who_hated))
        user += "\n\n" + block

    return system, user


def assemble_sin_prompts(
    name: str,
    age: int,
    gender: str,
    occupation: str,
    cause_of_death: str,
    who_loved: str,
    who_hated: str,
    prose_body: str,
    other_reason_true: Optional[str] = None,
) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the Sin call."""
    p = _reload_prompts()
    system = p.characterSetupSystemPrompt
    user = (p.characterSinUserPrompt
            .replace("{NAME}", name)
            .replace("{AGE}", str(age))
            .replace("{GENDER}", gender)
            .replace("{OCCUPATION}", occupation)
            .replace("{CAUSE_OF_DEATH}", cause_of_death)
            .replace("{WHO_LOVED}", who_loved)
            .replace("{WHO_HATED}", who_hated)
            .replace("{PROSE_BODY}", prose_body))

    if other_reason_true is not None:
        block = p.characterSinAntiDuplicationBlock.replace(
            "{OTHER_REASON_TRUE}", other_reason_true
        )
        user += "\n\n" + block

    return system, user


def assemble_stance_prompts(
    name: str,
    age: int,
    gender: str,
    occupation: str,
    cause_of_death: str,
    reason_true: str,
    reason_self_told: str,
    refuse_to_admit: str,
    prose_body: str,
    other_want: Optional[str] = None,
) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the Stance call."""
    p = _reload_prompts()
    system = p.characterSetupSystemPrompt
    user = (p.characterStanceUserPrompt
            .replace("{NAME}", name)
            .replace("{AGE}", str(age))
            .replace("{GENDER}", gender)
            .replace("{OCCUPATION}", occupation)
            .replace("{CAUSE_OF_DEATH}", cause_of_death)
            .replace("{REASON_TRUE}", reason_true)
            .replace("{REASON_SELF_TOLD}", reason_self_told)
            .replace("{REFUSE_TO_ADMIT}", refuse_to_admit)
            .replace("{PROSE_BODY}", prose_body))

    if other_want is not None:
        block = p.characterStanceAntiDuplicationBlock.replace("{OTHER_WANT}", other_want)
        user += "\n\n" + block

    return system, user


# ──────────────────────────────────────────────────────────────────────────────
# FIELD EXTRACTION (mirrors CharacterGenerator.ExtractField)
# ──────────────────────────────────────────────────────────────────────────────

def extract_field(response: str, field_name: str) -> Optional[str]:
    """
    Find **field_name** in response and return the content up to the next **
    marker (or end of string). Trimmed. Returns None if marker not found.
    """
    if not response:
        return None
    marker = f"**{field_name}**"
    start = response.find(marker)
    if start < 0:
        return None
    start += len(marker)
    # Skip leading newlines/CR
    while start < len(response) and response[start] in ("\n", "\r"):
        start += 1
    end = response.find("**", start)
    content = response[start:] if end < 0 else response[start:end]
    return content.strip()


def parse_life_response(response: str) -> dict:
    """Returns {'occupation', 'cause_of_death', 'who_loved', 'who_hated', 'prose_body'}. Values may be None."""
    return {
        "occupation": extract_field(response, "Occupation"),
        "cause_of_death": extract_field(response, "Cause of Death"),
        "who_loved": extract_field(response, "Who you loved"),
        "who_hated": extract_field(response, "Who you hated"),
        "prose_body": extract_field(response, "Life"),
    }


def parse_sin_response(response: str) -> dict:
    """Returns {'reason_true', 'reason_self_told', 'refuse_to_admit'}."""
    return {
        "reason_true": extract_field(response, "Reason for Damnation — True"),
        "reason_self_told": extract_field(response, "Reason for Damnation — Self-told"),
        "refuse_to_admit": extract_field(response, "What you refuse to admit about yourself"),
    }


def parse_stance_response(response: str) -> dict:
    """Returns {'personality_trait', 'want'}."""
    return {
        "personality_trait": extract_field(response, "Defining personality trait"),
        "want": extract_field(response, "What you want from the others in the room"),
    }


def life_parse_complete(parsed: dict) -> bool:
    return all(v and v.strip() for v in [
        parsed["occupation"], parsed["cause_of_death"],
        parsed["who_loved"], parsed["who_hated"], parsed["prose_body"],
    ])


def sin_parse_complete(parsed: dict) -> bool:
    return all(v and v.strip() for v in [parsed["reason_true"], parsed["reason_self_told"], parsed["refuse_to_admit"]])


def stance_parse_complete(parsed: dict) -> bool:
    return all(v and v.strip() for v in [parsed["personality_trait"], parsed["want"]])


def assemble_bio(
    occupation: str,
    cause_of_death: str,
    who_loved: str,
    who_hated: str,
    reason_true: str,
    reason_self_told: str,
    personality_trait: str,
    refuse_to_admit: str,
    want: str,
    prose_body: str,
) -> str:
    """Assembles the final bio string in the display order (matches CharacterGenerator)."""
    sections = [
        f"**Occupation**\n{occupation}",
        f"**Cause of Death**\n{cause_of_death}",
        f"**Who you loved**\n{who_loved}",
        f"**Who you hated**\n{who_hated}",
        f"**Reason for Damnation — True**\n{reason_true}",
        f"**Reason for Damnation — Self-told**\n{reason_self_told}",
        f"**Defining personality trait**\n{personality_trait}",
        f"**What you refuse to admit about yourself**\n{refuse_to_admit}",
        f"**What you want from the others in the room**\n{want}",
        "---",
        prose_body,
    ]
    return "\n\n".join(sections)


# ──────────────────────────────────────────────────────────────────────────────
# DIALOGUE
# ──────────────────────────────────────────────────────────────────────────────

def assemble_dialogue_system_prompt(character_description: str) -> str:
    """Substitutes {CHARACTER_DESCRIPTION} into the dialogue template."""
    p = _reload_prompts()
    return p.dialogueSystemPromptTemplate.replace("{CHARACTER_DESCRIPTION}", character_description)


def assemble_dialogue_user_message(
    info_other_1: list[str],
    info_other_2: list[str],
    recent_dialogue_formatted: str,
    speaker_person_no: int,
    player_message: str,
) -> str:
    """
    Builds the per-turn dialogue user message.
    Mirrors SendRequestForCharacter assembly.
    """
    def info_block(infos: list[str]) -> str:
        filtered = [i for i in infos if i and i.strip()]
        if not filtered:
            return "Nothing has been revealed yet."
        return "\n".join(filtered)

    return (
        "## What you know about the others in the room\n\n"
        f"<other_1>:\n{info_block(info_other_1)}\n\n"
        f"<other_2>:\n{info_block(info_other_2)}\n\n"
        f"## Recent dialogue in the room\n{recent_dialogue_formatted}\n\n"
        "---\n\n"
        f"[<other_{speaker_person_no}> is speaking to you]\n"
        f"{player_message}"
    )


# ──────────────────────────────────────────────────────────────────────────────
# ADDRESSING
# ──────────────────────────────────────────────────────────────────────────────

def assemble_addressing_system_prompt(
    char1_info: list[str],
    char2_info: list[str],
    latest_dialogues_context: str,
) -> str:
    """
    Mirrors SendRequestForAdress assembly.
    Note: uses Unity's "Character 1/2" format (the addressing path doesn't use <other_N>).
    """
    p = _reload_prompts()

    def char_info_section(char_no: int, infos: list[str]) -> str:
        filtered = [i for i in infos if i and i.strip()]
        if not filtered:
            return f"Nothing known for Character {char_no}"
        body = "\n".join(f'"{i}"' for i in filtered)
        return f"Character {char_no} information known: \n{body}\n "

    char1_section = char_info_section(1, char1_info)
    char2_section = char_info_section(2, char2_info)

    return (
        p.adressingSystemPromptIntro + "\n "
        + char1_section + "\n "
        + char2_section + "\n "
        + p.adressingSystemPromptContext + "\n "
        + latest_dialogues_context + "\n "
        + p.adressingSystemPromptActions
    )


# ──────────────────────────────────────────────────────────────────────────────
# INFO EXTRACTION
# ──────────────────────────────────────────────────────────────────────────────

def get_info_extraction_system_prompt() -> str:
    p = _reload_prompts()
    return p.infoExtractionSystemPrompt


# ──────────────────────────────────────────────────────────────────────────────
# NARRATOR
# ──────────────────────────────────────────────────────────────────────────────

def get_narrator_prompts() -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) for the narrator call."""
    p = _reload_prompts()
    return p.narratorSystemPrompt, p.narratorUserPrompt