"""OpenAI LLM client implementation."""

from __future__ import annotations

import os
import time
from typing import Any

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class LLMClient:
    """OpenAI API 클라이언트"""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None) -> None:
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter")

        self.client = OpenAI(api_key=self.api_key)
        self.max_retries = 3
        self.retry_delay = 1.0

    def generate(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """프롬프트에 대한 응답을 생성합니다."""

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=30.0
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"OpenAI API 호출 실패 (최대 재시도 초과): {e}")

                wait_time = self.retry_delay * (2 ** attempt)
                time.sleep(wait_time)

        return ""  # Should not reach here

    def generate_batch(self, prompts: list[str], max_tokens: int = 500, temperature: float = 0.7) -> list[str]:
        """여러 프롬프트에 대한 응답을 순차적으로 생성합니다."""
        results = []

        for i, prompt in enumerate(prompts):
            try:
                result = self.generate(prompt, max_tokens, temperature)
                results.append(result)

                # API 레이트 리미트 고려한 지연
                if i < len(prompts) - 1:
                    time.sleep(0.1)

            except Exception as e:
                results.append(f"오류 발생: {e}")

        return results
