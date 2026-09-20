"""
Restore game_state/ (prompts, config, assembly, game, providers) from a
previous backups/ version.

This is a MIRROR restore: the live game_state/ folder ends up an exact copy
of the chosen version's game_state/ -- any file added since that version
(and not present back then) is removed, not just overwritten.

Before restoring, the CURRENT state is automatically saved as a new
"pre-restore" safety version, so restoring never loses work.

Usage:
    python restore_version.py 2026-08-09_shorter-dialogue-cap
    python restore_version.py shorter-dialogue-cap        # unambiguous suffix match
    python restore_version.py 2026-08-09_baseline --yes   # skip confirmation prompt
"""

import argparse
import shutil
import sys
from pathlib import Path

from save_version import save_version, write_current, tracked_files, GAME_STATE_DIR

ROOT = Path(__file__).parent
BACKUPS = ROOT / "backups"


def resolve_version(name: str) -> Path:
    exact = BACKUPS / name
    if exact.is_dir():
        return exact
    matches = [p for p in BACKUPS.iterdir() if p.is_dir() and p.name.endswith(name)] if BACKUPS.exists() else []
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Ambiguous version '{name}', matches: {[m.name for m in matches]}")
        sys.exit(1)
    print(f"No version found matching '{name}'")
    sys.exit(1)


def diff_summary(live_dir: Path, target_dir: Path):
    """
    Byte-for-byte comparison of every tracked file in both trees, all types --
    not just .py, so a non-Python file can no longer be silently overwritten or
    deleted by a restore without showing up in the confirmation preview.

    Returns [(relpath, kind), ...].
    """
    live_files = tracked_files(live_dir)
    target_files = tracked_files(target_dir)
    changed = []
    for rel in sorted(live_files | target_files, key=str):
        live_file, target_file = live_dir / rel, target_dir / rel
        if not live_file.exists():
            changed.append((rel, "will be added (present in backup, missing live)"))
        elif not target_file.exists():
            changed.append((rel, "will be removed (present live, not in this backup)"))
        elif live_file.read_bytes() != target_file.read_bytes():
            changed.append((rel, "will change"))
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="version folder name (or unambiguous suffix)")
    parser.add_argument("--yes", action="store_true", help="skip confirmation prompt")
    args = parser.parse_args()

    target = resolve_version(args.version)
    target_state = target / "game_state"
    if not target_state.exists():
        print(f"'{target.name}' has no game_state/ folder (pre-migration backup?). Nothing to restore.")
        sys.exit(1)

    print(f"Restoring from: {target.name}\n")
    changed = diff_summary(GAME_STATE_DIR, target_state)
    if not changed:
        print("Current game_state/ already matches this version. Nothing to do.")
        return
    for rel, kind in changed:
        print(f"  {rel}: {kind}")

    if not args.yes:
        confirm = input("\nProceed with restore? [y/N] ").strip().lower()
        if confirm != "y":
            print("Aborted.")
            return

    safety_dir = save_version("pre-restore-safety", f"Auto-saved before restoring {target.name}")
    print(f"Safety snapshot of current state saved to: {safety_dir.name}")

    shutil.rmtree(GAME_STATE_DIR)
    shutil.copytree(target_state, GAME_STATE_DIR, ignore=shutil.ignore_patterns("__pycache__"))

    # save_version() above pointed CURRENT at the safety snapshot -- i.e. at the
    # state we just discarded. Live game_state/ now matches the restored version,
    # so CURRENT has to say so, or every run generated next gets tagged with the
    # abandoned state.
    write_current(target)

    print(f"\nRestored {target.name}. Previous state was preserved as {safety_dir.name} (see backups/CHANGELOG.md).")
    print(f"backups/CURRENT now points at {target.name} -- runs saved from here are tagged with it.")


if __name__ == "__main__":
    main()
