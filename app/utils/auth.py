"""API 키 인증 관리 유틸리티"""

import json
import os
from pathlib import Path
from typing import Optional


def load_openai_api_key() -> Optional[str]:
    """저장된 OpenAI API 키를 로드합니다."""
    auth_file = Path(".auth/openai_api.json")

    if not auth_file.exists():
        return None

    try:
        with open(auth_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("api_key")
    except (json.JSONDecodeError, KeyError, FileNotFoundError):
        return None


def save_openai_api_key(api_key: str) -> bool:
    """OpenAI API 키를 저장합니다."""
    auth_dir = Path(".auth")
    auth_dir.mkdir(exist_ok=True)

    auth_file = auth_dir / "openai_api.json"

    try:
        data = {"api_key": api_key}
        with open(auth_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def get_openai_api_key() -> Optional[str]:
    """OpenAI API 키를 가져옵니다. 파일에서 우선 로드하고, 없으면 환경변수에서 로드합니다."""
    # 1. 파일에서 로드 시도
    api_key = load_openai_api_key()
    if api_key:
        return api_key

    # 2. 환경변수에서 로드 시도
    return os.getenv("OPENAI_API_KEY")
