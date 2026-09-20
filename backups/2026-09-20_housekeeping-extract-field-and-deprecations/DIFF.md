## assembly.py

```diff
--- assembly.py (previous)
+++ assembly.py (this version)
@@ -1,234 +1,248 @@
-"""
-Prompt assembly logic mirroring CharacterController.cs and CharacterGenerator.cs.
-
-Pure functions — no I/O, no state. Given inputs, return the assembled strings.
-"""
-
-from typing import Optional
-import importlib
-
-
-def _reload_prompts():
-    """Reload prompts module to pick up edits made during the session."""
-    from game_state import prompts
-    importlib.reload(prompts)
-    return prompts
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# CHARACTER GENERATION
-# ──────────────────────────────────────────────────────────────────────────────
-
-def assemble_character_prompts(
-    name_origin: str,
-    age: int,
-    gender: str,
-    other_name: Optional[str] = None,
-    other_bio: Optional[str] = None,
-) -> tuple[str, str]:
-    """
-    Returns (system_prompt, user_prompt) for the single character-generation call.
-
-    Replaces the former four-call chain (name -> life -> sin -> stance). The order of
-    the format block inside characterFullUserPrompt carries the conditioning those
-    separate calls used to provide -- generation is autoregressive, so each field is
-    written knowing the ones above it. Do not reorder that block casually.
-
-    If other_name and other_bio are given, appends the anti-duplication block (Character 2).
-    """
-    p = _reload_prompts()
-    system = p.characterSetupSystemPrompt
-    user = (p.characterFullUserPrompt
-            .replace("{NAME_ORIGIN}", name_origin)
-            .replace("{AGE}", str(age))
-            .replace("{GENDER}", gender))
-
-    if other_name is not None and other_bio is not None:
-        block = (p.characterFullAntiDuplicationBlock
-                 .replace("{OTHER_NAME}", other_name)
-                 .replace("{OTHER_BIO}", other_bio))
-        user += "\n\n" + block
-
-    return system, user
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# FIELD EXTRACTION (mirrors CharacterGenerator.ExtractField)
-# ──────────────────────────────────────────────────────────────────────────────
-
-def extract_field(response: str, field_name: str) -> Optional[str]:
-    """
-    Find **field_name** in response and return the content up to the next **
-    marker (or end of string). Trimmed. Returns None if marker not found.
-    """
-    if not response:
-        return None
-    marker = f"**{field_name}**"
-    start = response.find(marker)
-    if start < 0:
-        return None
-    start += len(marker)
-    # Skip leading newlines/CR
-    while start < len(response) and response[start] in ("\n", "\r"):
-        start += 1
-    end = response.find("**", start)
-    content = response[start:] if end < 0 else response[start:end]
-    return content.strip()
-
-
-# Field key -> the **heading** it is written under in the generation response.
-# Order matches the format block in prompts.characterFullUserPrompt.
-CHARACTER_FIELDS = {
-    "name": "Name",
-    "occupation": "Occupation",
-    # The relationship precedes the death deliberately: generation is autoregressive,
-    # so a death written before these fields cannot be caused by the person in them.
-    # That ordering is what made every death read as disconnected through v4.
-    "who_loved": "Who you loved",
-    "who_hated": "Who you hated",
-    "cause_of_death": "Cause of Death",
-    "prose_body": "Life",
-    "reason_true": "Reason for Damnation — True",
-    "reason_self_told": "Reason for Damnation — Self-told",
-    "refuse_to_admit": "What you refuse to admit about yourself",
-    "personality_trait": "Defining personality trait",
-    "want": "What you want from the others in the room",
-}
-
-
-def parse_character_response(response: str) -> dict:
-    """All eleven character fields from one generation response. Values may be None."""
-    return {key: extract_field(response, label) for key, label in CHARACTER_FIELDS.items()}
-
-
-def character_parse_complete(parsed: dict) -> bool:
-    """True only when every field came back non-empty; drives the parse retry."""
-    return all((parsed.get(key) or "").strip() for key in CHARACTER_FIELDS)
-
-
-def assemble_bio(
-    occupation: str,
-    cause_of_death: str,
-    who_loved: str,
-    who_hated: str,
-    reason_true: str,
-    reason_self_told: str,
-    personality_trait: str,
-    refuse_to_admit: str,
-    want: str,
-    prose_body: str,
-) -> str:
-    """
-    Assembles the final bio string in the display order (matches CharacterGenerator).
-
-    Section order follows CHARACTER_FIELDS -- the relationship before the death --
-    so the bio reads in the order the model wrote it.
-    """
-    sections = [
-        f"**Occupation**\n{occupation}",
-        f"**Who you loved**\n{who_loved}",
-        f"**Who you hated**\n{who_hated}",
-        f"**Cause of Death**\n{cause_of_death}",
-        f"**Reason for Damnation — True**\n{reason_true}",
-        f"**Reason for Damnation — Self-told**\n{reason_self_told}",
-        f"**Defining personality trait**\n{personality_trait}",
-        f"**What you refuse to admit about yourself**\n{refuse_to_admit}",
-        f"**What you want from the others in the room**\n{want}",
-        "---",
-        prose_body,
-    ]
-    return "\n\n".join(sections)
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# DIALOGUE
-# ──────────────────────────────────────────────────────────────────────────────
-
-def assemble_dialogue_system_prompt(name: str, character_description: str) -> str:
-    """Substitutes {NAME} and {CHARACTER_DESCRIPTION} into the dialogue template."""
-    p = _reload_prompts()
-    return (p.dialogueSystemPromptTemplate
-            .replace("{NAME}", name)
-            .replace("{CHARACTER_DESCRIPTION}", character_description))
-
-
-def assemble_dialogue_user_message(
-    info_other_1: list[str],
-    info_other_2: list[str],
-    recent_dialogue_formatted: str,
-    speaker_person_no: int,
-    player_message: str,
-) -> str:
-    """
-    Builds the per-turn dialogue user message.
-    Mirrors SendRequestForCharacter assembly.
-    """
-    def info_block(infos: list[str]) -> str:
-        filtered = [i for i in infos if i and i.strip()]
-        if not filtered:
-            return "Nothing has been revealed yet."
-        return "\n".join(filtered)
-
-    return (
-        "## What you know about the others in the room\n\n"
-        f"<other_1>:\n{info_block(info_other_1)}\n\n"
-        f"<other_2>:\n{info_block(info_other_2)}\n\n"
-        f"## Recent dialogue in the room\n{recent_dialogue_formatted}\n\n"
-        "---\n\n"
-        f"[<other_{speaker_person_no}> is speaking to you]\n"
-        f"{player_message}"
-    )
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# ADDRESSING
-# ──────────────────────────────────────────────────────────────────────────────
-
-def assemble_addressing_system_prompt(
-    char1_info: list[str],
-    char2_info: list[str],
-    latest_dialogues_context: str,
-) -> str:
-    """
-    Mirrors SendRequestForAdress assembly.
-    Note: uses Unity's "Character 1/2" format (the addressing path doesn't use <other_N>).
-    """
-    p = _reload_prompts()
-
-    def char_info_section(char_no: int, infos: list[str]) -> str:
-        filtered = [i for i in infos if i and i.strip()]
-        if not filtered:
-            return f"Nothing known for Character {char_no}"
-        body = "\n".join(f'"{i}"' for i in filtered)
-        return f"Character {char_no} information known: \n{body}\n "
-
-    char1_section = char_info_section(1, char1_info)
-    char2_section = char_info_section(2, char2_info)
-
-    return (
-        p.adressingSystemPromptIntro + "\n "
-        + char1_section + "\n "
-        + char2_section + "\n "
-        + p.adressingSystemPromptContext + "\n "
-        + latest_dialogues_context + "\n "
-        + p.adressingSystemPromptActions
-    )
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# INFO EXTRACTION
-# ──────────────────────────────────────────────────────────────────────────────
-
-def get_info_extraction_system_prompt() -> str:
-    p = _reload_prompts()
-    return p.infoExtractionSystemPrompt
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# NARRATOR
-# ──────────────────────────────────────────────────────────────────────────────
-
-def get_narrator_prompts() -> tuple[str, str]:
-    """Returns (system_prompt, user_prompt) for the narrator call."""
-    p = _reload_prompts()
+"""
+Prompt assembly logic mirroring CharacterController.cs and CharacterGenerator.cs.
+
+Pure functions — no I/O, no state. Given inputs, return the assembled strings.
+"""
+
+import re
+from typing import Optional
+import importlib
+
+
+def _reload_prompts():
+    """Reload prompts module to pick up edits made during the session."""
+    from game_state import prompts
+    importlib.reload(prompts)
+    return prompts
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# CHARACTER GENERATION
+# ──────────────────────────────────────────────────────────────────────────────
+
+def assemble_character_prompts(
+    name_origin: str,
+    age: int,
+    gender: str,
+    other_name: Optional[str] = None,
+    other_bio: Optional[str] = None,
+) -> tuple[str, str]:
+    """
+    Returns (system_prompt, user_prompt) for the single character-generation call.
+
+    Replaces the former four-call chain (name -> life -> sin -> stance). The order of
+    the format block inside characterFullUserPrompt carries the conditioning those
+    separate calls used to provide -- generation is autoregressive, so each field is
+    written knowing the ones above it. Do not reorder that block casually.
+
+    If other_name and other_bio are given, appends the anti-duplication block (Character 2).
+    """
+    p = _reload_prompts()
+    system = p.characterSetupSystemPrompt
+    user = (p.characterFullUserPrompt
+            .replace("{NAME_ORIGIN}", name_origin)
+            .replace("{AGE}", str(age))
+            .replace("{GENDER}", gender))
+
+    if other_name is not None and other_bio is not None:
+        block = (p.characterFullAntiDuplicationBlock
+                 .replace("{OTHER_NAME}", other_name)
+                 .replace("{OTHER_BIO}", other_bio))
+        user += "\n\n" + block
+
+    return system, user
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# FIELD EXTRACTION (mirrors CharacterGenerator.ExtractField)
+# ──────────────────────────────────────────────────────────────────────────────
+
+# A '**' at the start of a line: how extract_field spots the next heading.
+_HEADING_START = re.compile(r"^\*\*", re.M)
+
+
+def extract_field(response: str, field_name: str) -> Optional[str]:
+    """
+    Find **field_name** in response and return the content up to the next heading
+    (or end of string). Trimmed. Returns None if the marker isn't found.
+
+    The end marker is the next '**' that STARTS A LINE, not the next '**' anywhere.
+    Headings are always written on their own line, so anchoring to line starts tells
+    them apart from emphasis inside a value -- previously a value containing inline
+    bold ("teacher **and** coach") was silently truncated at the first inner marker.
+    No response on record contains mid-line '**', so this is defensive rather than a
+    change to how any existing run parses.
+    """
+    if not response:
+        return None
+    marker = f"**{field_name}**"
+    start = response.find(marker)
+    if start < 0:
+        return None
+    start += len(marker)
+    # Skip leading newlines/CR
+    while start < len(response) and response[start] in ("\n", "\r"):
+        start += 1
+    nxt = _HEADING_START.search(response, start)
+    content = response[start:nxt.start()] if nxt else response[start:]
+    return content.strip()
+
+
+# Field key -> the **heading** it is written under in the generation response.
+# Order matches the format block in prompts.characterFullUserPrompt.
+CHARACTER_FIELDS = {
+    "name": "Name",
+    "occupation": "Occupation",
+    # The relationship precedes the death deliberately: generation is autoregressive,
+    # so a death written before these fields cannot be caused by the person in them.
+    # That ordering is what made every death read as disconnected through v4.
+    "who_loved": "Who you loved",
+    "who_hated": "Who you hated",
+    "cause_of_death": "Cause of Death",
+    "prose_body": "Life",
+    "reason_true": "Reason for Damnation — True",
+    "reason_self_told": "Reason for Damnation — Self-told",
+    "refuse_to_admit": "What you refuse to admit about yourself",
+    "personality_trait": "Defining personality trait",
+    "want": "What you want from the others in the room",
+}
+
+
+def parse_character_response(response: str) -> dict:
+    """All eleven character fields from one generation response. Values may be None."""
+    return {key: extract_field(response, label) for key, label in CHARACTER_FIELDS.items()}
+
+
+def character_parse_complete(parsed: dict) -> bool:
+    """True only when every field came back non-empty; drives the parse retry."""
+    return all((parsed.get(key) or "").strip() for key in CHARACTER_FIELDS)
+
+
+def assemble_bio(
+    occupation: str,
+    cause_of_death: str,
+    who_loved: str,
+    who_hated: str,
+    reason_true: str,
+    reason_self_told: str,
+    personality_trait: str,
+    refuse_to_admit: str,
+    want: str,
+    prose_body: str,
+) -> str:
+    """
+    Assembles the final bio string in the display order (matches CharacterGenerator).
+
+    This is DISPLAY order and is deliberately NOT identical to CHARACTER_FIELDS:
+    the relationship precedes the death as it does there, but the trait is shown
+    before the refusal, the reverse of the order they are generated in. Changing
+    this changes the dialogue system prompt, since the bio is substituted into it.
+    """
+    sections = [
+        f"**Occupation**\n{occupation}",
+        f"**Who you loved**\n{who_loved}",
+        f"**Who you hated**\n{who_hated}",
+        f"**Cause of Death**\n{cause_of_death}",
+        f"**Reason for Damnation — True**\n{reason_true}",
+        f"**Reason for Damnation — Self-told**\n{reason_self_told}",
+        f"**Defining personality trait**\n{personality_trait}",
+        f"**What you refuse to admit about yourself**\n{refuse_to_admit}",
+        f"**What you want from the others in the room**\n{want}",
+        "---",
+        prose_body,
+    ]
+    return "\n\n".join(sections)
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# DIALOGUE
+# ──────────────────────────────────────────────────────────────────────────────
+
+def assemble_dialogue_system_prompt(name: str, character_description: str) -> str:
+    """Substitutes {NAME} and {CHARACTER_DESCRIPTION} into the dialogue template."""
+    p = _reload_prompts()
+    return (p.dialogueSystemPromptTemplate
+            .replace("{NAME}", name)
+            .replace("{CHARACTER_DESCRIPTION}", character_description))
+
+
+def assemble_dialogue_user_message(
+    info_other_1: list[str],
+    info_other_2: list[str],
+    recent_dialogue_formatted: str,
+    speaker_person_no: int,
+    player_message: str,
+) -> str:
+    """
+    Builds the per-turn dialogue user message.
+    Mirrors SendRequestForCharacter assembly.
+    """
+    def info_block(infos: list[str]) -> str:
+        filtered = [i for i in infos if i and i.strip()]
+        if not filtered:
+            return "Nothing has been revealed yet."
+        return "\n".join(filtered)
+
+    return (
+        "## What you know about the others in the room\n\n"
+        f"<other_1>:\n{info_block(info_other_1)}\n\n"
+        f"<other_2>:\n{info_block(info_other_2)}\n\n"
+        f"## Recent dialogue in the room\n{recent_dialogue_formatted}\n\n"
+        "---\n\n"
+        f"[<other_{speaker_person_no}> is speaking to you]\n"
+        f"{player_message}"
+    )
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# ADDRESSING
+# ──────────────────────────────────────────────────────────────────────────────
+
+def assemble_addressing_system_prompt(
+    char1_info: list[str],
+    char2_info: list[str],
+    latest_dialogues_context: str,
+) -> str:
+    """
+    Mirrors SendRequestForAdress assembly.
+    Note: uses Unity's "Character 1/2" format (the addressing path doesn't use <other_N>).
+    """
+    p = _reload_prompts()
+
+    def char_info_section(char_no: int, infos: list[str]) -> str:
+        filtered = [i for i in infos if i and i.strip()]
+        if not filtered:
+            return f"Nothing known for Character {char_no}"
+        body = "\n".join(f'"{i}"' for i in filtered)
+        return f"Character {char_no} information known: \n{body}\n "
+
+    char1_section = char_info_section(1, char1_info)
+    char2_section = char_info_section(2, char2_info)
+
+    return (
+        p.adressingSystemPromptIntro + "\n "
+        + char1_section + "\n "
+        + char2_section + "\n "
+        + p.adressingSystemPromptContext + "\n "
+        + latest_dialogues_context + "\n "
+        + p.adressingSystemPromptActions
+    )
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# INFO EXTRACTION
+# ──────────────────────────────────────────────────────────────────────────────
+
+def get_info_extraction_system_prompt() -> str:
+    p = _reload_prompts()
+    return p.infoExtractionSystemPrompt
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# NARRATOR
+# ──────────────────────────────────────────────────────────────────────────────
+
+def get_narrator_prompts() -> tuple[str, str]:
+    """Returns (system_prompt, user_prompt) for the narrator call."""
+    p = _reload_prompts()
     return p.narratorSystemPrompt, p.narratorUserPrompt```

## config.py

```diff
--- config.py (previous)
+++ config.py (this version)
@@ -68,4 +68,4 @@
 REQUEST_TIMEOUT = 180
 
 # ── Parsing retry config ──
-PARSE_RETRY_ATTEMPTS = 2+PARSE_RETRY_ATTEMPTS = 2
```

## game.py

```diff
--- game.py (previous)
+++ game.py (this version)
@@ -1,221 +1,232 @@
-"""
-Game state, person mapping, dialogue history, infoShared tracking.
-Mirrors the state held by CharacterController.cs in Unity.
-"""
-
-from dataclasses import dataclass, field
-from typing import Optional
-from datetime import datetime
-import uuid
-
-from game_state import config
-
-
-@dataclass
-class Character:
-    """Mirrors PersonController + CharacterEntry."""
-    name: str = ""
-    description: str = ""  # The assembled bio string
-    gender: str = ""
-    age: int = 0
-    info_shared: list[str] = field(default_factory=list)
-
-    # Parsed fields (used for character generation anti-duplication and other tooling)
-    occupation: str = ""
-    cause_of_death: str = ""
-    who_loved: str = ""
-    who_hated: str = ""
-    prose_body: str = ""
-    reason_true: str = ""
-    reason_self_told: str = ""
-    refuse_to_admit: str = ""
-    personality_trait: str = ""
-    want: str = ""
-
-
-@dataclass
-class DialogueEntry:
-    """Mirrors DialogueEntry in CharacterController.cs."""
-    character_id: int  # 0 = player, 1 = Char 1, 2 = Char 2, 3 = narrator
-    character_label: str  # "Character 0", "Character 1", etc. — for latestDialoguesContext
-    dialogue_text: str
-    timestamp: str = ""
-
-
-@dataclass
-class GameState:
-    """
-    Full mutable game state for a session.
-    Index 0 in `characters` is the player (kept for symmetry with Unity's PersonController list).
-    """
-    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
-    session_started: str = field(default_factory=lambda: datetime.utcnow().isoformat())
-    characters: dict[int, Character] = field(default_factory=dict)
-    dialogue_entries: list[DialogueEntry] = field(default_factory=list)
-    turn_count: int = 0
-
-    # Tracking for restart/clear semantics
-    characters_generated: bool = False  # True after both Char 1 and Char 2 exist
-    narrator_played: bool = False
-
-    def __post_init__(self):
-        # Initialize empty player slot (index 0). Player has no bio.
-        if 0 not in self.characters:
-            self.characters[0] = Character(name="Player")
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# PERSON MAPPING (mirrors GetPersonMapping / GetPersonNumberFor)
-# ──────────────────────────────────────────────────────────────────────────────
-
-def get_person_mapping(replying_char: int) -> tuple[int, int]:
-    """
-    From replying_char's perspective, returns (person1_index, person2_index).
-    Person 1 = the other AI character. Person 2 = the player.
-    """
-    other_char = 2 if replying_char == 1 else 1
-    return (other_char, 0)
-
-
-def get_person_number_for(replying_char: int, speaker_index: int) -> int:
-    """
-    Returns 1 or 2: the person label number for speaker_index from replying_char's view.
-    Falls back to 2 on unexpected input (mirrors Unity's behavior + warning).
-    """
-    p1, p2 = get_person_mapping(replying_char)
-    if speaker_index == p1:
-        return 1
-    if speaker_index == p2:
-        return 2
-    # Narrator (id=3) falls here. Mirrors Unity's "Unexpected speakerIndex" path.
-    return 2
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# DIALOGUE HISTORY FORMATTING
-# ──────────────────────────────────────────────────────────────────────────────
-
-def format_dialogue_for_character(state: GameState, current_character: int) -> str:
-    """
-    Formats the last N dialogue entries from current_character's perspective.
-    Mirrors FormatDialogueForCharacter in CharacterController.cs.
-    """
-    if not state.dialogue_entries:
-        return "No one has spoken yet."
-
-    window = config.DIALOGUE_HISTORY_WINDOW
-    recent = state.dialogue_entries[-window:]
-
-    lines = []
-    for entry in recent:
-        speaker_id = entry.character_id
-        if speaker_id == current_character:
-            label = "You"
-        else:
-            label = f"<other_{get_person_number_for(current_character, speaker_id)}>"
-        lines.append(f"{label}: {entry.dialogue_text}")
-
-    return "\n".join(lines)
-
-
-def get_latest_dialogues_context(state: GameState) -> str:
-    """
-    Builds the shared addressing-context string.
-    Mirrors UpdateLatestDialoguesContext in CharacterController.cs.
-    Uses "Character N" format (not <other_N>) per Unity's addressing path.
-    """
-    window = config.DIALOGUE_HISTORY_WINDOW
-    recent = state.dialogue_entries[-window:]
-    lines = []
-    for entry in recent:
-        lines.append(f"Character {entry.character_id}: {entry.dialogue_text}")
-    return "\n".join(lines) + "\n" if lines else ""
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# DIALOGUE LOGGING
-# ──────────────────────────────────────────────────────────────────────────────
-
-def log_dialogue(state: GameState, character_id: int, text: str) -> None:
-    """Adds a dialogue entry. Mirrors LogDialogueEntry in CharacterController.cs."""
-    entry = DialogueEntry(
-        character_id=character_id,
-        character_label=f"Character {character_id}",
-        dialogue_text=text,
-        timestamp=datetime.utcnow().isoformat(),
-    )
-    state.dialogue_entries.append(entry)
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# INFO SHARED
-# ──────────────────────────────────────────────────────────────────────────────
-
-def add_info(state: GameState, character_id: int, info: str) -> None:
-    """Add an extracted info string to a character's infoShared list."""
-    if info and info.strip() and info.strip().lower() != "none":
-        if character_id not in state.characters:
-            state.characters[character_id] = Character()
-        state.characters[character_id].info_shared.append(info.strip())
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# RESET / CLEAR OPERATIONS
-# ──────────────────────────────────────────────────────────────────────────────
-
-def restart_new(state: GameState) -> GameState:
-    """Fresh characters, fresh dialogue, fresh infoShared. Returns a new GameState."""
-    return GameState()
-
-
-def restart_same(state: GameState) -> None:
-    """Keep bios; clear dialogue and infoShared. Mutates state in place."""
-    state.dialogue_entries.clear()
-    state.turn_count = 0
-    state.narrator_played = False
-    for char_id, char in state.characters.items():
-        char.info_shared.clear()
-
-
-def clear_dialogue(state: GameState) -> None:
-    """Clear dialogue history only. Keep infoShared and bios."""
-    state.dialogue_entries.clear()
-    state.turn_count = 0
-
-
-def clear_info(state: GameState) -> None:
-    """Clear infoShared for all characters. Keep dialogue and bios."""
-    for char_id, char in state.characters.items():
-        char.info_shared.clear()
-
-
-def clear_all(state: GameState) -> None:
-    """Clear both dialogue history and infoShared. Keep bios."""
-    clear_dialogue(state)
-    clear_info(state)
-
-
-# ──────────────────────────────────────────────────────────────────────────────
-# STATE SUMMARY (for `status` command)
-# ──────────────────────────────────────────────────────────────────────────────
-
-def state_summary(state: GameState) -> str:
-    """Human-readable summary of current state."""
-    lines = [
-        f"Session: {state.session_id} (started {state.session_started})",
-        f"Turns: {state.turn_count}",
-        f"Characters generated: {state.characters_generated}",
-        f"Narrator played: {state.narrator_played}",
-        f"Dialogue entries: {len(state.dialogue_entries)}",
-        "",
-    ]
-    for char_id in sorted(state.characters.keys()):
-        char = state.characters[char_id]
-        if char_id == 0:
-            continue  # skip player
-        info_count = len(char.info_shared)
-        lines.append(f"Character {char_id}: {char.name or '(no name)'}, {info_count} infoShared item(s)")
-        if char.info_shared:
-            for info in char.info_shared:
-                lines.append(f"  - {info}")
+"""
+Game state, person mapping, dialogue history, infoShared tracking.
+Mirrors the state held by CharacterController.cs in Unity.
+"""
+
+from dataclasses import dataclass, field
+from typing import Optional
+from datetime import datetime, timezone
+import uuid
+
+from game_state import config
+
+
+def _utc_now_iso() -> str:
+    """
+    UTC timestamp in the exact shape utcnow().isoformat() produced.
+
+    utcnow() is deprecated, but the naive (offset-free) form is kept deliberately:
+    every stored run uses it and run_viewer sorts these as plain strings, so an
+    offset-bearing format would mix two shapes in one column.
+    """
+    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()
+
+
+@dataclass
+class Character:
+    """Mirrors PersonController + CharacterEntry."""
+    name: str = ""
+    description: str = ""  # The assembled bio string
+    gender: str = ""
+    age: int = 0
+    info_shared: list[str] = field(default_factory=list)
+
+    # Parsed fields (used for character generation anti-duplication and other tooling)
+    occupation: str = ""
+    cause_of_death: str = ""
+    who_loved: str = ""
+    who_hated: str = ""
+    prose_body: str = ""
+    reason_true: str = ""
+    reason_self_told: str = ""
+    refuse_to_admit: str = ""
+    personality_trait: str = ""
+    want: str = ""
+
+
+@dataclass
+class DialogueEntry:
+    """Mirrors DialogueEntry in CharacterController.cs."""
+    character_id: int  # 0 = player, 1 = Char 1, 2 = Char 2, 3 = narrator
+    character_label: str  # "Character 0", "Character 1", etc. — for latestDialoguesContext
+    dialogue_text: str
+    timestamp: str = ""
+
+
+@dataclass
+class GameState:
+    """
+    Full mutable game state for a session.
+    Index 0 in `characters` is the player (kept for symmetry with Unity's PersonController list).
+    """
+    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
+    session_started: str = field(default_factory=_utc_now_iso)
+    characters: dict[int, Character] = field(default_factory=dict)
+    dialogue_entries: list[DialogueEntry] = field(default_factory=list)
+    turn_count: int = 0
+
+    # Tracking for restart/clear semantics
+    characters_generated: bool = False  # True after both Char 1 and Char 2 exist
+    narrator_played: bool = False
+
+    def __post_init__(self):
+        # Initialize empty player slot (index 0). Player has no bio.
+        if 0 not in self.characters:
+            self.characters[0] = Character(name="Player")
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# PERSON MAPPING (mirrors GetPersonMapping / GetPersonNumberFor)
+# ──────────────────────────────────────────────────────────────────────────────
+
+def get_person_mapping(replying_char: int) -> tuple[int, int]:
+    """
+    From replying_char's perspective, returns (person1_index, person2_index).
+    Person 1 = the other AI character. Person 2 = the player.
+    """
+    other_char = 2 if replying_char == 1 else 1
+    return (other_char, 0)
+
+
+def get_person_number_for(replying_char: int, speaker_index: int) -> int:
+    """
+    Returns 1 or 2: the person label number for speaker_index from replying_char's view.
+    Falls back to 2 on unexpected input (mirrors Unity's behavior + warning).
+    """
+    p1, p2 = get_person_mapping(replying_char)
+    if speaker_index == p1:
+        return 1
+    if speaker_index == p2:
+        return 2
+    # Narrator (id=3) falls here. Mirrors Unity's "Unexpected speakerIndex" path.
+    return 2
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# DIALOGUE HISTORY FORMATTING
+# ──────────────────────────────────────────────────────────────────────────────
+
+def format_dialogue_for_character(state: GameState, current_character: int) -> str:
+    """
+    Formats the last N dialogue entries from current_character's perspective.
+    Mirrors FormatDialogueForCharacter in CharacterController.cs.
+    """
+    if not state.dialogue_entries:
+        return "No one has spoken yet."
+
+    window = config.DIALOGUE_HISTORY_WINDOW
+    recent = state.dialogue_entries[-window:]
+
+    lines = []
+    for entry in recent:
+        speaker_id = entry.character_id
+        if speaker_id == current_character:
+            label = "You"
+        else:
+            label = f"<other_{get_person_number_for(current_character, speaker_id)}>"
+        lines.append(f"{label}: {entry.dialogue_text}")
+
+    return "\n".join(lines)
+
+
+def get_latest_dialogues_context(state: GameState) -> str:
+    """
+    Builds the shared addressing-context string.
+    Mirrors UpdateLatestDialoguesContext in CharacterController.cs.
+    Uses "Character N" format (not <other_N>) per Unity's addressing path.
+    """
+    window = config.DIALOGUE_HISTORY_WINDOW
+    recent = state.dialogue_entries[-window:]
+    lines = []
+    for entry in recent:
+        lines.append(f"Character {entry.character_id}: {entry.dialogue_text}")
+    return "\n".join(lines) + "\n" if lines else ""
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# DIALOGUE LOGGING
+# ──────────────────────────────────────────────────────────────────────────────
+
+def log_dialogue(state: GameState, character_id: int, text: str) -> None:
+    """Adds a dialogue entry. Mirrors LogDialogueEntry in CharacterController.cs."""
+    entry = DialogueEntry(
+        character_id=character_id,
+        character_label=f"Character {character_id}",
+        dialogue_text=text,
+        timestamp=_utc_now_iso(),
+    )
+    state.dialogue_entries.append(entry)
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# INFO SHARED
+# ──────────────────────────────────────────────────────────────────────────────
+
+def add_info(state: GameState, character_id: int, info: str) -> None:
+    """Add an extracted info string to a character's infoShared list."""
+    if info and info.strip() and info.strip().lower() != "none":
+        if character_id not in state.characters:
+            state.characters[character_id] = Character()
+        state.characters[character_id].info_shared.append(info.strip())
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# RESET / CLEAR OPERATIONS
+# ──────────────────────────────────────────────────────────────────────────────
+
+def restart_new(state: GameState) -> GameState:
+    """Fresh characters, fresh dialogue, fresh infoShared. Returns a new GameState."""
+    return GameState()
+
+
+def restart_same(state: GameState) -> None:
+    """Keep bios; clear dialogue and infoShared. Mutates state in place."""
+    state.dialogue_entries.clear()
+    state.turn_count = 0
+    state.narrator_played = False
+    for char_id, char in state.characters.items():
+        char.info_shared.clear()
+
+
+def clear_dialogue(state: GameState) -> None:
+    """Clear dialogue history only. Keep infoShared and bios."""
+    state.dialogue_entries.clear()
+    state.turn_count = 0
+
+
+def clear_info(state: GameState) -> None:
+    """Clear infoShared for all characters. Keep dialogue and bios."""
+    for char_id, char in state.characters.items():
+        char.info_shared.clear()
+
+
+def clear_all(state: GameState) -> None:
+    """Clear both dialogue history and infoShared. Keep bios."""
+    clear_dialogue(state)
+    clear_info(state)
+
+
+# ──────────────────────────────────────────────────────────────────────────────
+# STATE SUMMARY (for `status` command)
+# ──────────────────────────────────────────────────────────────────────────────
+
+def state_summary(state: GameState) -> str:
+    """Human-readable summary of current state."""
+    lines = [
+        f"Session: {state.session_id} (started {state.session_started})",
+        f"Turns: {state.turn_count}",
+        f"Characters generated: {state.characters_generated}",
+        f"Narrator played: {state.narrator_played}",
+        f"Dialogue entries: {len(state.dialogue_entries)}",
+        "",
+    ]
+    for char_id in sorted(state.characters.keys()):
+        char = state.characters[char_id]
+        if char_id == 0:
+            continue  # skip player
+        info_count = len(char.info_shared)
+        lines.append(f"Character {char_id}: {char.name or '(no name)'}, {info_count} infoShared item(s)")
+        if char.info_shared:
+            for info in char.info_shared:
+                lines.append(f"  - {info}")
     return "\n".join(lines)```

## providers.py

```diff
--- providers.py (previous)
+++ providers.py (this version)
@@ -13,7 +13,7 @@
 
 import requests
 import time
-from dataclasses import dataclass, field
+from dataclasses import dataclass
 from typing import Optional, Any
 
 from game_state import config
```
