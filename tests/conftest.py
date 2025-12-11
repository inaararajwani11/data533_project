"""Test configuration: ensure project root is on sys.path for IDE runs."""
from __future__ import annotations

import sys
from pathlib import Path

# Add repository src and package path to sys.path so `import project.core` works regardless of CWD.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PROJECT = SRC / "project"

for path in (PROJECT, SRC, ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
