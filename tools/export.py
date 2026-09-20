"""
Packages session outputs into a downloadable zip.
"""

import shutil
from pathlib import Path
from datetime import datetime, timezone

import simulator  # for OUTPUT_DIR + file paths


from _paths import PROJECT_ROOT, GAME_STATE

EXPORT_DIR = PROJECT_ROOT / "noexit_exports"


def export_session(label: str = "") -> Path:
    """
    Bundle transcript files, edits log, current game_state/, and state snapshot
    into a zip in EXPORT_DIR.

    Returns the path to the created zip.
    """
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    suffix = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if label:
        suffix = f"{label}_{suffix}"
    out_dir = EXPORT_DIR / f"noexit_session_{suffix}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Copy everything in OUTPUT_DIR
    for f in simulator.OUTPUT_DIR.iterdir():
        if f.is_file():
            shutil.copy(f, out_dir / f.name)

    # Also copy the current game_state/ (prompts, config, assembly, game, providers)
    game_state_src = GAME_STATE
    if game_state_src.exists():
        shutil.copytree(game_state_src, out_dir / "game_state", ignore=shutil.ignore_patterns("__pycache__"))

    # Zip it
    zip_base = str(EXPORT_DIR / f"noexit_session_{suffix}")
    shutil.make_archive(zip_base, "zip", out_dir)
    zip_path = Path(zip_base + ".zip")

    # Cleanup the temp directory
    shutil.rmtree(out_dir)

    return zip_path


def write_session_notes(state, summary: str = "") -> Path:
    """
    Generate a session_notes.md file summarizing the session.
    The `summary` arg is free-form text from Claude (what was tested, what was learned).
    """
    notes_path = simulator.OUTPUT_DIR / "session_notes.md"

    content = [
        "# noexit harness session notes",
        "",
        f"**Session ID:** `{state.session_id}`",
        f"**Started:** {state.session_started}",
        f"**Turns played:** {state.turn_count}",
        f"**Characters generated:** {state.characters_generated}",
        f"**Narrator played:** {state.narrator_played}",
        "",
        "## Characters",
    ]
    for cid in sorted(state.characters.keys()):
        if cid == 0:
            continue
        char = state.characters[cid]
        content.append("")
        content.append(f"### Character {cid}: {char.name or '(unnamed)'}")
        content.append(f"- **Age/Gender:** {char.age}, {char.gender}")
        content.append(f"- **Occupation:** {char.occupation}")
        content.append(f"- **Cause of Death:** {char.cause_of_death}")
        content.append(f"- **Personality:** {char.personality_trait}")
        content.append(f"- **Wants:** {char.want}")
        if char.info_shared:
            content.append("- **infoShared:**")
            for info in char.info_shared:
                content.append(f"  - {info}")

    content.append("")
    content.append(f"## Dialogue ({len(state.dialogue_entries)} entries)")
    for e in state.dialogue_entries[-10:]:  # last 10 for brevity
        content.append(f"- **{e.character_label}:** {e.dialogue_text}")
    if len(state.dialogue_entries) > 10:
        content.append(f"- ...({len(state.dialogue_entries) - 10} earlier entries — see transcript.csv)")

    if summary:
        content.append("")
        content.append("## Session summary")
        content.append(summary)

    content.append("")
    content.append("## Files")
    content.append("- `transcript.csv` — full per-call log")
    content.append("- `transcript.json` — same data, structured")
    content.append("- `edits.csv` — prompt edits made this session")
    content.append("- `session_state.json` — full state snapshot for resumption")
    content.append("- `game_state/` — current working prompts, config, assembly, game, providers")

    notes_path.write_text("\n".join(content), encoding="utf-8")
    return notes_path


def write_migration_brief(original_prompts: dict, current_prompts: dict) -> Path:
    """
    Diff original vs. current prompts; write a Claude Code brief documenting changes.
    Returns the path to the brief.
    """
    brief_path = simulator.OUTPUT_DIR / "migration_brief.md"

    changed = []
    for name, original in original_prompts.items():
        current = current_prompts.get(name)
        if current is not None and current != original:
            changed.append((name, original, current))

    if not changed:
        brief_path.write_text("# Migration brief\n\nNo prompt changes detected.\n", encoding="utf-8")
        return brief_path

    content = [
        "# Migration brief — prompt updates from harness session",
        "",
        "## Context",
        "",
        f"During an interactive harness session, {len(changed)} prompt(s) were edited. "
        "This brief lists each change to apply to `PromptsController.cs` in the Unity project.",
        "",
        "## Files affected",
        "",
        "- `Assets/Scripts/PromptsController.cs` — update Init() string assignments for the fields listed below",
        "",
        "## Changes",
        "",
    ]

    for name, original, current in changed:
        content.append(f"### `{name}`")
        content.append("")
        content.append("**Before:**")
        content.append("```")
        content.append(original)
        content.append("```")
        content.append("")
        content.append("**After:**")
        content.append("```")
        content.append(current)
        content.append("```")
        content.append("")

    content.append("## What is NOT changed")
    content.append("")
    content.append("- Code in `CharacterController.cs`, `CharacterGenerator.cs`, `APIRequestHandler.cs`, `InfoExtractorHandler.cs` — prompt content only")
    content.append("- Any prompt field not listed above")
    content.append("")
    content.append("## Verification")
    content.append("")
    content.append("1. After applying changes, run `Init()` (refresh AssembledPromptsPreview in Inspector) and confirm each updated field shows the new content.")
    content.append("2. Play a session in Unity and confirm behavior matches what was tested in the harness.")

    brief_path.write_text("\n".join(content), encoding="utf-8")
    return brief_path