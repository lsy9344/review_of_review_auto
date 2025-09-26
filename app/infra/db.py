"""SQLite initialization and migration helpers (placeholder)."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: Path = Path("runs/reviews.db")) -> sqlite3.Connection:
    db_path.parent.mkdir(exist_ok=True)
    return sqlite3.connect(str(db_path))
