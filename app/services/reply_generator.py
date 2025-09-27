"""LLM-backed reply generation with tone/length rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from app.domain.prompts import (
    DEFAULT_BUSINESS_TYPE,
    DEFAULT_TONE,
    build_reply_prompt,
    clean_reply_text,
)
from app.infra.llm_openai import LLMClient


@dataclass
class ReplyConfig:
    """답변 생성 설정"""

    tone: str = DEFAULT_TONE
    business_type: str = DEFAULT_BUSINESS_TYPE
    store_name: str | None = None
    max_tokens: int = 300
    temperature: float = 0.7
    openai_api_key: str | None = None
    custom_prompt: str = ""


@dataclass
class ReviewReplyPair:
    """리뷰와 생성된 답변의 쌍"""

    review_id: str
    review_text: str
    review_rating: int | None = None
    review_author: str | None = None
    generated_reply: str = ""
    error: str | None = None


LogCallback = Callable[[str, str], None]


class ReplyGenerator:
    """OpenAI를 사용한 리뷰 답변 생성기"""

    def __init__(self, config: ReplyConfig):
        self.config = config
        try:
            self.llm_client = LLMClient(
                model="gpt-4o-mini", api_key=config.openai_api_key
            )
        except Exception as e:
            raise RuntimeError(f"OpenAI 클라이언트 초기화 실패: {e}")

    def generate(
        self, review_text: str, review_author: str | None = None, log: LogCallback | None = None
    ) -> str:
        """단일 리뷰에 대한 답변을 생성합니다."""
        if not review_text.strip():
            return ""

        def emit(level: str, message: str) -> None:
            if log:
                log(level, message)

        try:
            # 사용자 정의 프롬프트가 있으면 사용, 없으면 기본 프롬프트 시스템 사용
            if self.config.custom_prompt.strip():
                # {작성자}를 실제 리뷰어 이름으로 교체
                custom_prompt = self.config.custom_prompt
                if review_author:
                    custom_prompt = custom_prompt.replace("{작성자}", review_author)
                prompt = f"{custom_prompt}\n\n리뷰:\n{review_text}\n\n답변:"
            else:
                prompt = build_reply_prompt(
                    review_text=review_text,
                    tone=self.config.tone,
                    business_type=self.config.business_type,
                    store_name=self.config.store_name,
                )

            # 최종 프롬프트 디버그 로그
            emit(
                "DEBUG",
                f"Final prompt for review by '{review_author}':\n{prompt}",
            )

            raw_reply = self.llm_client.generate(
                prompt=prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
            )

            return clean_reply_text(raw_reply)

        except Exception as e:
            raise RuntimeError(f"답변 생성 실패: {e}")

    def generate_batch(
        self, reviews: list[dict[str, Any]], log: LogCallback | None = None
    ) -> list[ReviewReplyPair]:
        """여러 리뷰에 대한 답변을 일괄 생성합니다."""

        def emit(level: str, message: str) -> None:
            if log:
                log(level, message)

        emit("INFO", f"{len(reviews)}개 리뷰에 대한 답변 생성을 시작합니다.")

        results: list[ReviewReplyPair] = []

        for i, review in enumerate(reviews, 1):
            review_id = review.get("id", f"review_{i}")
            review_text = self._extract_review_text(review)
            review_rating = review.get("rating")
            review_author = self._extract_author_name(review)

            emit("INFO", f"[{i}/{len(reviews)}] 리뷰 '{review_id}' 답변 생성 중...")

            try:
                if not review_text.strip():
                    emit("WARNING", f"리뷰 '{review_id}': 텍스트 내용이 없음")
                    results.append(
                        ReviewReplyPair(
                            review_id=review_id,
                            review_text="",
                            error="리뷰 텍스트 없음",
                        )
                    )
                    continue

                generated_reply = self.generate(review_text, review_author, log=emit)

                if not generated_reply:
                    emit("WARNING", f"리뷰 '{review_id}': 답변 생성 실패")
                    results.append(
                        ReviewReplyPair(
                            review_id=review_id,
                            review_text=review_text,
                            review_rating=review_rating,
                            review_author=review_author,
                            error="답변 생성 실패",
                        )
                    )
                    continue

                results.append(
                    ReviewReplyPair(
                        review_id=review_id,
                        review_text=review_text,
                        review_rating=review_rating,
                        review_author=review_author,
                        generated_reply=generated_reply,
                    )
                )

                emit(
                    "SUCCESS",
                    f"리뷰 '{review_id}' 답변 생성 완료: {generated_reply[:50]}...",
                )

            except Exception as e:
                error_msg = str(e)
                emit("ERROR", f"리뷰 '{review_id}' 답변 생성 실패: {error_msg}")
                results.append(
                    ReviewReplyPair(
                        review_id=review_id,
                        review_text=review_text,
                        review_rating=review_rating,
                        review_author=review_author,
                        error=error_msg,
                    )
                )

        success_count = len([r for r in results if r.error is None])
        emit("SUCCESS", f"답변 생성 완료: {success_count}/{len(reviews)}개 성공")

        return results

    def _extract_review_text(self, review: dict[str, Any]) -> str:
        """리뷰 데이터에서 텍스트 내용을 추출합니다."""
        # GraphQL API 응답 구조에 맞춰 텍스트 추출
        content = review.get("content", {})
        if isinstance(content, dict):
            return content.get("text", "")
        elif isinstance(content, str):
            return content
        else:
            # 다른 필드에서 텍스트를 찾아볼 수 있음
            return review.get("text", "")

    def _extract_author_name(self, review: dict[str, Any]) -> str | None:
        """리뷰 데이터에서 작성자 이름을 추출합니다."""
        author = review.get("author", {})
        if isinstance(author, dict):
            return author.get("displayName")
        return None
