"""Test package initializer: ensure repository paths are on sys.path."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src" / "project"

for path in (SOURCE_ROOT, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

