"""
Single source of truth for project paths.

Every script in tools/ imports from here instead of deriving paths from its own
__file__. That mattered when these scripts lived at the project root and each one
computed `ROOT = Path(__file__).parent`: moving them into tools/ would silently
have repointed that at tools/, so save_version.py would have created a fresh empty
tools/backups/ and started a new version history rather than failing loudly.

Importing this module also puts the project root on sys.path, because game_state is
a top-level package and running a script out of tools/ puts tools/ on sys.path, not
the root. Any module here that does `from game_state import ...` must import _paths
first -- the sys.path insert happens at import time.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BACKUPS = PROJECT_ROOT / "backups"
GAME_STATE = PROJECT_ROOT / "game_state"
RUNS = PROJECT_ROOT / "runs"
OUTPUTS = PROJECT_ROOT / "noexit_outputs"
UI = PROJECT_ROOT / "ui"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
