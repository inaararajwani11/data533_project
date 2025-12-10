"""Test configuration: ensure project root is on sys.path for IDE runs."""
from __future__ import annotations

import sys
from pathlib import Path

# Add repository root to sys.path so `import core` works even when tests
# are executed with working directory set to test/.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
