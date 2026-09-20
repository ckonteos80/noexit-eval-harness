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

def assemble_character_prompts(
    name_origin: str,
    age: int,
    gender: str,
    other_name: Optional[str] = None,
    other_bio: Optional[str] = None,
) -> tuple[str, str]:
    """
    Returns (system_prompt, user_prompt) for the single character-generation call.

    Replaces the former four-call chain (name -> life -> sin -> stance). The order of
    the format block inside characterFullUserPrompt carries the conditioning those
    separate calls used to provide -- generation is autoregressive, so each field is
    written knowing the ones above it. Do not reorder that block casually.

    If other_name and other_bio are given, appends the anti-duplication block (Character 2).
    """
    p = _reload_prompts()
    system = p.characterSetupSystemPrompt
    user = (p.characterFullUserPrompt
            .replace("{NAME_ORIGIN}", name_origin)
            .replace("{AGE}", str(age))
            .replace("{GENDER}", gender))

    if other_name is not None and other_bio is not None:
        block = (p.characterFullAntiDuplicationBlock
                 .replace("{OTHER_NAME}", other_name)
                 .replace("{OTHER_BIO}", other_bio))
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


# Field key -> the **heading** it is written under in the generation response.
# Order matches the format block in prompts.characterFullUserPrompt.
CHARACTER_FIELDS = {
    "name": "Name",
    "occupation": "Occupation",
    # The relationship precedes the death deliberately: generation is autoregressive,
    # so a death written before these fields cannot be caused by the person in them.
    # That ordering is what made every death read as disconnected through v4.
    "who_loved": "Who you loved",
    "who_hated": "Who you hated",
    "cause_of_death": "Cause of Death",
    "prose_body": "Life",
    "reason_true": "Reason for Damnation — True",
    "reason_self_told": "Reason for Damnation — Self-told",
    "refuse_to_admit": "What you refuse to admit about yourself",
    "personality_trait": "Defining personality trait",
    "want": "What you want from the others in the room",
}


def parse_character_response(response: str) -> dict:
    """All eleven character fields from one generation response. Values may be None."""
    return {key: extract_field(response, label) for key, label in CHARACTER_FIELDS.items()}


def character_parse_complete(parsed: dict) -> bool:
    """True only when every field came back non-empty; drives the parse retry."""
    return all((parsed.get(key) or "").strip() for key in CHARACTER_FIELDS)


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
    """
    Assembles the final bio string in the display order (matches CharacterGenerator).

    Section order follows CHARACTER_FIELDS -- the relationship before the death --
    so the bio reads in the order the model wrote it.
    """
    sections = [
        f"**Occupation**\n{occupation}",
        f"**Who you loved**\n{who_loved}",
        f"**Who you hated**\n{who_hated}",
        f"**Cause of Death**\n{cause_of_death}",
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

def assemble_dialogue_system_prompt(name: str, character_description: str) -> str:
    """Substitutes {NAME} and {CHARACTER_DESCRIPTION} into the dialogue template."""
    p = _reload_prompts()
    return (p.dialogueSystemPromptTemplate
            .replace("{NAME}", name)
            .replace("{CHARACTER_DESCRIPTION}", character_description))


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