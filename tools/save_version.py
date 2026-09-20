"""
Snapshot game_state/ (prompts, config, assembly, game, providers) into
backups/<date>_<slug>/, with a diff against the previous version, an entry
in backups/CHANGELOG.md, and a note on which Unity .cs files to check.

Usage:
    python tools/save_version.py "slug-name" "One-line summary of this version's state/changes"
"""

import argparse
import ast
import difflib
import json
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path

from _paths import PROJECT_ROOT, BACKUPS, GAME_STATE as GAME_STATE_DIR, RUNS as RUNS_DIR

ROOT = PROJECT_ROOT
CURRENT_FILE = BACKUPS / "CURRENT"

# Files inside game_state/ that are copied but never meaningfully diffed.
IGNORED_PARTS = {"__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}

# Which game_state/ file mirrors which Unity C# file(s). Used to write
# backups/UNITY_MAPPING.md and each version's "Unity files to update" note.
UNITY_MAPPING = {
    "prompts.py": [
        "Assets/Scripts/PromptsController.cs -- Init() string field assignments",
    ],
    "config.py": [
        "CharacterController.cs -- 'temp' field (shared by TEMP_DIALOGUE/TEMP_ADDRESSING/"
        "TEMP_NARRATOR -- changing just one of these three constants has no independent "
        "Unity equivalent; verify all three still agree before treating this as a clean port)",
        "CharacterController.cs -- useQween0_6, useHuggingFaceProvider toggles",
        "CharacterGenerator.cs -- temperature, age Random.Range(25,65), gender assignment",
        "ModelNamesController -- model strings",
    ],
    "assembly.py": [
        "CharacterController.cs -- SendRequestForCharacter, SendRequestForAdress",
        "CharacterGenerator.cs -- ExtractField",
    ],
    "game.py": [
        "CharacterController.cs -- PersonController/CharacterEntry, DialogueEntry, "
        "GetPersonMapping, GetPersonNumberFor, FormatDialogueForCharacter, "
        "UpdateLatestDialoguesContext, LogDialogueEntry",
    ],
    "providers.py": [
        "APIRequestHandler.cs -- SendOpenAIRequest",
        "InfoExtractorHandler.cs -- ExtractInfo",
    ],
}

UNTRACKED_UNITY_NOTE = (
    "tools/simulator.py is outside game_state/ and so is not snapshotted, but its call-flow "
    "mirrors Unity: CharacterGenerator.cs (GenerateCharacter) and CharacterController.cs "
    "(ParsedText) -- the sequencing of generation calls and reply/addressing routing. If you "
    "change *when* addressing triggers, reply routing, or the generation sequence, check "
    "those Unity methods too, even though this tool won't flag it automatically."
)


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.strip().lower())
    return s.strip("-") or "version"


def list_versions():
    """
    All version folders, sorted by name. This is DISPLAY order, not authority --
    it is alphabetical, so two versions saved on the same date are ordered by slug
    rather than by when they were saved. Never use [-1] to mean "the version that
    matches live game_state/"; use current_version() for that.
    """
    if not BACKUPS.exists():
        return []
    return sorted(p for p in BACKUPS.iterdir() if p.is_dir())


def write_current(version_dir: Path):
    """Record which version the live game_state/ now matches."""
    BACKUPS.mkdir(exist_ok=True)
    CURRENT_FILE.write_text(json.dumps({
        "version": version_dir.name,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }, indent=2), encoding="utf-8")


def current_version() -> Path | None:
    """
    The version folder whose game_state/ matches what is live right now.

    Read from backups/CURRENT, which save_version() and restore_version.py both
    maintain. Falls back to the last folder by name if CURRENT is missing (only
    expected on repos predating CURRENT), which is why that path warns.
    """
    if CURRENT_FILE.exists():
        try:
            name = json.loads(CURRENT_FILE.read_text(encoding="utf-8")).get("version")
        except (json.JSONDecodeError, OSError):
            name = None
        if name:
            candidate = BACKUPS / name
            if candidate.is_dir():
                return candidate
            print(f"WARNING: backups/CURRENT names '{name}', which does not exist.")

    versions = list_versions()
    if not versions:
        return None
    print("WARNING: backups/CURRENT missing or unreadable -- falling back to the "
          f"last version by name ({versions[-1].name}). This is a guess; run "
          "save_version.py to re-establish it.")
    return versions[-1]


def tracked_files(root: Path) -> set:
    """
    Every file under root that is worth diffing -- all file types, not just .py,
    minus the compiled-Python noise that copytree already ignores.
    """
    if not root.exists():
        return set()
    out = set()
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if IGNORED_PARTS & set(p.parts) or p.suffix in IGNORED_SUFFIXES:
            continue
        out.add(p.relative_to(root))
    return out


def next_version_dir(slug: str) -> Path:
    base_name = f"{date.today().isoformat()}_{slug}"
    candidate = BACKUPS / base_name
    if not candidate.exists():
        return candidate
    i = 2
    while (BACKUPS / f"{base_name}-{i}").exists():
        i += 1
    return BACKUPS / f"{base_name}-{i}"


def parse_prompt_fields(text: str) -> dict:
    """
    Extracts every module-level `NAME = <string literal>` from prompts.py source.

    Uses ast rather than a regex so quote style is irrelevant -- a single-quoted
    prompt is captured exactly like a triple-quoted one. (The previous regex only
    matched triple quotes, which silently hid changes to characterNameGenderSuffix,
    adressingSystemPromptContext and narratorUserPrompt from every DIFF.md.)
    """
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}
    fields = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                fields[target.id] = node.value.value
    return fields


def diff_prompt_fields(prev_text: str, new_text: str) -> str:
    """Field-level before/after (maps directly to PromptsController.cs field granularity)."""
    prev_fields = parse_prompt_fields(prev_text) if prev_text else {}
    new_fields = parse_prompt_fields(new_text) if new_text else {}
    sections = []
    for name in sorted(set(prev_fields) | set(new_fields)):
        old, new = prev_fields.get(name), new_fields.get(name)
        if old == new:
            continue
        if old is None:
            sections.append(f"**`{name}`** -- added:\n```\n{new}\n```\n")
        elif new is None:
            sections.append(f"**`{name}`** -- removed (was):\n```\n{old}\n```\n")
        else:
            sections.append(f"**`{name}`** -- before:\n```\n{old}\n```\nafter:\n```\n{new}\n```\n")
    return "\n".join(sections) if sections else "_(no field-level text change detected)_\n"


def compute_file_diffs(prev_dir: Path, new_dir: Path) -> dict:
    """
    Returns {relpath: diff_text_markdown} for every changed file under game_state/.

    Covers all file types, not just *.py -- a .json or .txt living in game_state/
    used to be snapshotted but never diffed, so changes to it vanished silently.
    """
    prev_state = (prev_dir / "game_state") if prev_dir else None
    new_state = new_dir / "game_state"
    prev_files = tracked_files(prev_state) if prev_state else set()
    new_files = tracked_files(new_state)

    diffs = {}
    for rel in sorted(prev_files | new_files, key=str):
        prev_file = (prev_state / rel) if prev_state else None
        new_file = new_state / rel
        prev_bytes = prev_file.read_bytes() if prev_file and prev_file.exists() else b""
        new_bytes = new_file.read_bytes() if new_file.exists() else b""
        if prev_bytes == new_bytes:
            continue
        try:
            prev_text = prev_bytes.decode("utf-8")
            new_text = new_bytes.decode("utf-8")
        except UnicodeDecodeError:
            diffs[rel] = ("_Binary file changed "
                          f"({len(prev_bytes)} -> {len(new_bytes)} bytes) -- no text diff._\n")
            continue
        if rel.name == "prompts.py":
            diffs[rel] = diff_prompt_fields(prev_text, new_text)
        else:
            prev_lines = prev_text.splitlines(keepends=True)
            new_lines = new_text.splitlines(keepends=True)
            diff_lines = list(difflib.unified_diff(
                prev_lines, new_lines, fromfile=f"{rel} (previous)", tofile=f"{rel} (this version)"))
            diffs[rel] = f"```diff\n{''.join(diff_lines)}```\n"
    return diffs


def write_diff(prev_dir: Path, new_dir: Path) -> dict:
    diffs = compute_file_diffs(prev_dir, new_dir)
    content = "\n".join(f"## {rel}\n\n{text}" for rel, text in diffs.items()) if diffs else "_No changes to tracked files._\n"
    (new_dir / "DIFF.md").write_text(content, encoding="utf-8")
    return diffs


def unity_notes_for(changed_relpaths) -> str:
    fnames = sorted({Path(rel).name for rel in changed_relpaths})
    if not fnames:
        return "_No tracked files changed -- nothing to port to Unity this version._\n"
    lines = []
    for fname in fnames:
        targets = UNITY_MAPPING.get(fname, ["(no mapping recorded -- check backups/UNITY_MAPPING.md)"])
        lines.append(f"- **{fname}** ->")
        lines.extend(f"  - {t}" for t in targets)
    return "\n".join(lines)


def write_unity_mapping_doc():
    lines = ["# Unity file mapping", "", "Which `game_state/` file corresponds to which Unity C# file(s).", ""]
    for fname, targets in UNITY_MAPPING.items():
        lines.append(f"## {fname}")
        lines.extend(f"- {t}" for t in targets)
        lines.append("")
    lines.append("## Not tracked in game_state/, but also Unity-relevant")
    lines.append("")
    lines.append(UNTRACKED_UNITY_NOTE)
    lines.append("")
    (BACKUPS / "UNITY_MAPPING.md").write_text("\n".join(lines), encoding="utf-8")


def archive_runs_for_version(version_dir: Path) -> int:
    """
    Copy (not move) every run tagged meta.game_state_version == version_dir.name into
    version_dir/runs/. Called with the *previous* version when a new one is saved --
    that's the moment we know the previous version's "run era" is closed.
    """
    if not RUNS_DIR.exists():
        return 0
    count = 0
    dest = version_dir / "runs"
    for run_path in RUNS_DIR.glob("*.json"):
        try:
            run_obj = json.loads(run_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        if run_obj.get("meta", {}).get("game_state_version") != version_dir.name:
            continue
        dest.mkdir(exist_ok=True)
        shutil.copy(run_path, dest / run_path.name)
        count += 1
    return count


def prepend_changelog_entry(new_dir: Path, prev_dir: Path, summary: str):
    changelog = BACKUPS / "CHANGELOG.md"
    entry = (
        f"## {new_dir.name}\n\n"
        f"**{summary}**\n\n"
        f"Previous: {prev_dir.name if prev_dir else '(none)'}\n\n"
        f"---\n\n"
    )
    if changelog.exists():
        existing = changelog.read_text(encoding="utf-8")
    else:
        existing = "# Prompt version changelog\n\n"
    header, sep, rest = existing.partition("\n\n")
    if sep:
        changelog.write_text(header + "\n\n" + entry + rest, encoding="utf-8")
    else:
        changelog.write_text(existing + "\n\n" + entry, encoding="utf-8")


def save_version(slug: str, summary: str) -> Path:
    BACKUPS.mkdir(exist_ok=True)
    slug = slugify(slug)
    # The version being superseded is whatever matched live game_state/ until now --
    # not the last folder by name, which is wrong after a restore or a same-day save.
    prev_dir = current_version() if list_versions() else None

    new_dir = next_version_dir(slug)
    new_dir.mkdir(parents=True)
    shutil.copytree(GAME_STATE_DIR, new_dir / "game_state", ignore=shutil.ignore_patterns("__pycache__"))

    diffs = write_diff(prev_dir, new_dir)
    unity_section = unity_notes_for(diffs.keys())

    notes = f"""# {new_dir.name}

**Date:** {date.today().isoformat()}
**Previous version:** {prev_dir.name if prev_dir else '(none this is the first version)'}

## State

{summary}

## Changes from previous version

- {summary}

(Edit this section with more detail if useful see DIFF.md for the exact diff.)

## Unity files to update

{unity_section}
"""
    (new_dir / "NOTES.md").write_text(notes, encoding="utf-8")
    prepend_changelog_entry(new_dir, prev_dir, summary)
    write_unity_mapping_doc()

    if prev_dir:
        n = archive_runs_for_version(prev_dir)
        if n:
            print(f"  archived {n} run(s) generated under {prev_dir.name} into {prev_dir.name}/runs/")

    # Live game_state/ now matches this version. Runs saved from here on are
    # tagged with it, so this must be written before any session is generated.
    write_current(new_dir)

    return new_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", help="short kebab-case label, e.g. 'shorter-dialogue-cap'")
    parser.add_argument("summary", help="one-line summary of this version's state/changes")
    args = parser.parse_args()

    new_dir = save_version(args.slug, args.summary)
    print(f"Saved version: {new_dir.name}")
    print(f"  -> {new_dir}")


if __name__ == "__main__":
    main()
