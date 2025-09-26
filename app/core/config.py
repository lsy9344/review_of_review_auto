"""
Configuration loading and validation utilities.

This module will later provide typed configuration schemas and robust
load/merge/validation logic. For now, it exposes a minimal stub.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class CrawlConfig:
    """A container for all settings required for an orchestration run."""

    user_id: str
    password: str
    business_ids: list[str] = field(default_factory=list)
    browser_visible: bool = False

    # 답변 생성 관련 설정
    openai_api_key: str = ""
    business_type: str = "일반"
    tone: str = "친절하고 정중한"
    custom_prompt: str = ""

    # 답변 제출 관련 설정
    auto_submit_replies: bool = False
    enable_reply_generation: bool = True


def load_config() -> Dict[str, Any]:
    """Load application configuration.

    Returns a dictionary for now. Will be replaced by a typed schema.
    """
    return {}
