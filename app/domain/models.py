"""Domain models (placeholder stubs).

Intended to be implemented with Pydantic models for:
- Store, Review, ReplyDraft, Submission, RunStats, etc.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Store:  # placeholder
    id: str
    name: str


@dataclass
class Review:  # placeholder
    id: str
    author: str
    content: str
    rating: Optional[int] = None


@dataclass
class ReplyDraft:  # placeholder
    review_id: str
    content: str
