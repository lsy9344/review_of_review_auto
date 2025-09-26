"""Submit replies to Naver SmartPlace using GraphQL API."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable

import httpx

# The GraphQL mutation query for creating a reply.
# This is extracted from the network request analysis.
CREATE_REPLY_MUTATION = """
fragment CommonReviewReplyFields on ReviewReply {
  text
  isSuspended
  isQualified
  createdDateTime
  updatedDateTime
  isDeleted
  useReplyCandidate
  replierDisplayName
  suspendPostingReason
  __typename
}

mutation createReply($input: CreateReviewReplyInput!) {
  createReviewReply(input: $input) {
    reply {
      ...CommonReviewReplyFields
      __typename
    }
    __typename
  }
}
"""


@dataclass
class SubmissionResult:
    """The result of submitting a single reply."""

    review_id: str
    success: bool
    error: str | None = None
    submitted_text: str = ""


LogCallback = Callable[[str, str], None]


class ReplySubmitter:
    """Submits replies to Naver SmartPlace automatically via its internal GraphQL API."""

    def __init__(self, client: httpx.Client):
        """
        Initializes the submitter with an authenticated httpx client.

        Args:
            client: An httpx.Client instance that has been authenticated
                    (i.e., contains the necessary login cookies).
        """
        self.client = client
        self.graphql_endpoint = (
            "https://new.smartplace.naver.com/graphql?opName=createReply"
        )

    def submit_batch(
        self,
        reply_pairs: list[dict[str, Any]],
        place_seq: str,
        booking_id: str,
        log: LogCallback | None = None,
    ) -> list[SubmissionResult]:
        """Submits multiple replies in a batch."""

        def emit(level: str, message: str) -> None:
            if log:
                log(level, message)

        emit("INFO", f"{len(reply_pairs)}개 답변에 대한 API 제출을 시작합니다.")
        results: list[SubmissionResult] = []

        # The csrf_token is sent as a cookie, which httpx.Client handles automatically.
        # We just need to ensure it was obtained during login.
        if "csrf_token" not in self.client.cookies:
            emit(
                "ERROR",
                "CSRF 토큰을 쿠키에서 찾을 수 없습니다. 로그인 과정이 올바른지 확인하세요.",
            )
            for pair in reply_pairs:
                results.append(
                    SubmissionResult(
                        review_id=pair.get("review_id", "unknown"),
                        success=False,
                        error="CSRF token not found in cookies.",
                    )
                )
            return results

        for i, pair in enumerate(reply_pairs, 1):
            review_id = pair.get("review_id")
            reply_text = pair.get("reply_text", "")

            if not review_id or not reply_text.strip():
                emit(
                    "WARNING",
                    f"리뷰 '{review_id or 'N/A'}': 리뷰 ID 또는 답변 텍스트가 비어있어 건너뜁니다.",
                )
                results.append(
                    SubmissionResult(
                        review_id=review_id or f"unknown_{i}",
                        success=False,
                        error="Review ID or reply text is empty.",
                    )
                )
                continue

            emit("INFO", f"[{i}/{len(reply_pairs)}] 리뷰 '{review_id}' 답변 제출 중...")

            try:
                # Construct the payload for the GraphQL mutation
                variables = {
                    "input": {
                        "text": reply_text,
                        "reviewId": review_id,
                        "bookingBusinessId": int(booking_id),
                    }
                }
                payload = {
                    "operationName": "createReply",
                    "variables": variables,
                    "query": CREATE_REPLY_MUTATION,
                }

                # Construct headers, mimicking the captured request
                headers = {
                    "accept": "*/*",
                    "accept-language": "ko-KR,ko;q=0.9",
                    "content-type": "application/json",
                    "from-system": "smartplace",
                    "origin": "https://new.smartplace.naver.com",
                    "referer": f"https://new.smartplace.naver.com/bizes/place/{place_seq}/reviews?bookingBusinessId={booking_id}&menu=visitor",
                    # user-agent is set on the client by LoginService
                }

                # Make the API call
                response = self.client.post(
                    self.graphql_endpoint,
                    json=payload,
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()

                response_data = response.json()

                if "errors" in response_data:
                    error_detail = response_data["errors"][0]["message"]
                    raise httpx.HTTPError(f"GraphQL API Error: {error_detail}")

                if response_data.get("data", {}).get("createReviewReply"):
                    emit(
                        "SUCCESS",
                        f"리뷰 '{review_id}' 답변이 성공적으로 제출되었습니다.",
                    )
                    results.append(
                        SubmissionResult(
                            review_id=review_id, success=True, submitted_text=reply_text
                        )
                    )
                else:
                    raise httpx.HTTPError("Unexpected GraphQL response format.")

            except (httpx.HTTPStatusError, httpx.RequestError, httpx.HTTPError) as e:
                error_msg = f"API call failed: {e}"
                emit("ERROR", f"리뷰 '{review_id}' 답변 제출 실패. {error_msg}")
                results.append(
                    SubmissionResult(review_id=review_id, success=False, error=str(e))
                )
            except Exception as e:
                error_msg = f"An unexpected error occurred: {e}"
                emit("ERROR", f"리뷰 '{review_id}' 답변 제출 실패. {error_msg}")
                results.append(
                    SubmissionResult(review_id=review_id, success=False, error=str(e))
                )

            # Add a short delay between requests to avoid rate-limiting
            if i < len(reply_pairs):
                time.sleep(1.5)

        success_count = len([r for r in results if r.success])
        emit("SUCCESS", f"API 제출 완료: {success_count}/{len(reply_pairs)}개 성공")

        return results
