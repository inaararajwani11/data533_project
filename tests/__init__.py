# Marks test directory as a package for unittest imports.
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PROJECT = SRC / "project"

for path in (PROJECT, SRC, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
