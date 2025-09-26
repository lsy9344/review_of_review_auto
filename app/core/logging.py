"""Logging setup utilities for the application."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_app_logging(level: int = logging.INFO) -> None:
    """Configure basic logging to file and stdout.

    Mirrors the current setup in app.main for future consolidation.
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
