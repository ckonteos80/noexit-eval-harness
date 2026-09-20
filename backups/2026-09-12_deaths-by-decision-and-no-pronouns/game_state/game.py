"""
Game state, person mapping, dialogue history, infoShared tracking.
Mirrors the state held by CharacterController.cs in Unity.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid

from game_state import config


@dataclass
class Character:
    """Mirrors PersonController + CharacterEntry."""
    name: str = ""
    description: str = ""  # The assembled bio string
    gender: str = ""
    age: int = 0
    info_shared: list[str] = field(default_factory=list)

    # Parsed fields (used for character generation anti-duplication and other tooling)
    occupation: str = ""
    cause_of_death: str = ""
    who_loved: str = ""
    who_hated: str = ""
    prose_body: str = ""
    reason_true: str = ""
    reason_self_told: str = ""
    refuse_to_admit: str = ""
    personality_trait: str = ""
    want: str = ""


@dataclass
class DialogueEntry:
    """Mirrors DialogueEntry in CharacterController.cs."""
    character_id: int  # 0 = player, 1 = Char 1, 2 = Char 2, 3 = narrator
    character_label: str  # "Character 0", "Character 1", etc. — for latestDialoguesContext
    dialogue_text: str
    timestamp: str = ""


@dataclass
class GameState:
    """
    Full mutable game state for a session.
    Index 0 in `characters` is the player (kept for symmetry with Unity's PersonController list).
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    session_started: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    characters: dict[int, Character] = field(default_factory=dict)
    dialogue_entries: list[DialogueEntry] = field(default_factory=list)
    turn_count: int = 0

    # Tracking for restart/clear semantics
    characters_generated: bool = False  # True after both Char 1 and Char 2 exist
    narrator_played: bool = False

    def __post_init__(self):
        # Initialize empty player slot (index 0). Player has no bio.
        if 0 not in self.characters:
            self.characters[0] = Character(name="Player")


# ──────────────────────────────────────────────────────────────────────────────
# PERSON MAPPING (mirrors GetPersonMapping / GetPersonNumberFor)
# ──────────────────────────────────────────────────────────────────────────────

def get_person_mapping(replying_char: int) -> tuple[int, int]:
    """
    From replying_char's perspective, returns (person1_index, person2_index).
    Person 1 = the other AI character. Person 2 = the player.
    """
    other_char = 2 if replying_char == 1 else 1
    return (other_char, 0)


def get_person_number_for(replying_char: int, speaker_index: int) -> int:
    """
    Returns 1 or 2: the person label number for speaker_index from replying_char's view.
    Falls back to 2 on unexpected input (mirrors Unity's behavior + warning).
    """
    p1, p2 = get_person_mapping(replying_char)
    if speaker_index == p1:
        return 1
    if speaker_index == p2:
        return 2
    # Narrator (id=3) falls here. Mirrors Unity's "Unexpected speakerIndex" path.
    return 2


# ──────────────────────────────────────────────────────────────────────────────
# DIALOGUE HISTORY FORMATTING
# ──────────────────────────────────────────────────────────────────────────────

def format_dialogue_for_character(state: GameState, current_character: int) -> str:
    """
    Formats the last N dialogue entries from current_character's perspective.
    Mirrors FormatDialogueForCharacter in CharacterController.cs.
    """
    if not state.dialogue_entries:
        return "No one has spoken yet."

    window = config.DIALOGUE_HISTORY_WINDOW
    recent = state.dialogue_entries[-window:]

    lines = []
    for entry in recent:
        speaker_id = entry.character_id
        if speaker_id == current_character:
            label = "You"
        else:
            label = f"<other_{get_person_number_for(current_character, speaker_id)}>"
        lines.append(f"{label}: {entry.dialogue_text}")

    return "\n".join(lines)


def get_latest_dialogues_context(state: GameState) -> str:
    """
    Builds the shared addressing-context string.
    Mirrors UpdateLatestDialoguesContext in CharacterController.cs.
    Uses "Character N" format (not <other_N>) per Unity's addressing path.
    """
    window = config.DIALOGUE_HISTORY_WINDOW
    recent = state.dialogue_entries[-window:]
    lines = []
    for entry in recent:
        lines.append(f"Character {entry.character_id}: {entry.dialogue_text}")
    return "\n".join(lines) + "\n" if lines else ""


# ──────────────────────────────────────────────────────────────────────────────
# DIALOGUE LOGGING
# ──────────────────────────────────────────────────────────────────────────────

def log_dialogue(state: GameState, character_id: int, text: str) -> None:
    """Adds a dialogue entry. Mirrors LogDialogueEntry in CharacterController.cs."""
    entry = DialogueEntry(
        character_id=character_id,
        character_label=f"Character {character_id}",
        dialogue_text=text,
        timestamp=datetime.utcnow().isoformat(),
    )
    state.dialogue_entries.append(entry)


# ──────────────────────────────────────────────────────────────────────────────
# INFO SHARED
# ──────────────────────────────────────────────────────────────────────────────

def add_info(state: GameState, character_id: int, info: str) -> None:
    """Add an extracted info string to a character's infoShared list."""
    if info and info.strip() and info.strip().lower() != "none":
        if character_id not in state.characters:
            state.characters[character_id] = Character()
        state.characters[character_id].info_shared.append(info.strip())


# ──────────────────────────────────────────────────────────────────────────────
# RESET / CLEAR OPERATIONS
# ──────────────────────────────────────────────────────────────────────────────

def restart_new(state: GameState) -> GameState:
    """Fresh characters, fresh dialogue, fresh infoShared. Returns a new GameState."""
    return GameState()


def restart_same(state: GameState) -> None:
    """Keep bios; clear dialogue and infoShared. Mutates state in place."""
    state.dialogue_entries.clear()
    state.turn_count = 0
    state.narrator_played = False
    for char_id, char in state.characters.items():
        char.info_shared.clear()


def clear_dialogue(state: GameState) -> None:
    """Clear dialogue history only. Keep infoShared and bios."""
    state.dialogue_entries.clear()
    state.turn_count = 0


def clear_info(state: GameState) -> None:
    """Clear infoShared for all characters. Keep dialogue and bios."""
    for char_id, char in state.characters.items():
        char.info_shared.clear()


def clear_all(state: GameState) -> None:
    """Clear both dialogue history and infoShared. Keep bios."""
    clear_dialogue(state)
    clear_info(state)


# ──────────────────────────────────────────────────────────────────────────────
# STATE SUMMARY (for `status` command)
# ──────────────────────────────────────────────────────────────────────────────

def state_summary(state: GameState) -> str:
    """Human-readable summary of current state."""
    lines = [
        f"Session: {state.session_id} (started {state.session_started})",
        f"Turns: {state.turn_count}",
        f"Characters generated: {state.characters_generated}",
        f"Narrator played: {state.narrator_played}",
        f"Dialogue entries: {len(state.dialogue_entries)}",
        "",
    ]
    for char_id in sorted(state.characters.keys()):
        char = state.characters[char_id]
        if char_id == 0:
            continue  # skip player
        info_count = len(char.info_shared)
        lines.append(f"Character {char_id}: {char.name or '(no name)'}, {info_count} infoShared item(s)")
        if char.info_shared:
            for info in char.info_shared:
                lines.append(f"  - {info}")
    return "\n".join(lines)