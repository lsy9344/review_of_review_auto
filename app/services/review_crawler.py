"""
Review crawler using the new Naver SmartPlace GraphQL API.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any, Callable

import httpx

from app.core.errors import ReviewAPIAuthError
from app.services.stop_signal import StopSignal

# GraphQL API 엔드포인트
GRAPHQL_API_URL = "https://new.smartplace.naver.com/graphql?opName=getReviews"

# GraphQL 쿼리 (사용자 제공 데이터 기반)
GET_REVIEWS_QUERY = """
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

fragment CommonReviewFields on Review {
  author {
    displayName
    reviewCount
    imageCount
    profileImage
    visitCount
    userId
    __typename
  }
  placeDetail {
    id
    __typename
  }
  bookingDetail {
    bookingUserDetail
    business
    bizItem
    items
    __typename
  }
  content {
    text
    mediaItems {
      id
      type
      thumbnail
      url
      trailer
      metadata
      __typename
    }
    rating
    tags {
      votedKeywords {
        category
        keywords {
          code
          emojiCode
          emojiUrl
          label {
            ko
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    textGradeInspection {
      grade
      __typename
    }
    __typename
  }
  reply {
    ...CommonReviewReplyFields
    __typename
  }
  reactionStat {
    id
    targetId
    totalCount
    sortedTypeCountEntries
    __typename
  }
  createdDateTime
  displayUpdatedDateTime
  id
  rating
  isSuspended
  suspendPostingReason
  isQualified
  source
  mainPov
  visitCount
  visitDateTime
  cp
  hasReply
  hasText
  hasVotedKeyword
  hasNegativeTextGrade
  __typename
}

query getReviews($input: GetReviewsInput!) {
  reviews(input: $input) {
    totalCount
    items {
      ...CommonReviewFields
      __typename
    }
    __typename
  }
}
"""

LogCallback = Callable[[str, str], None]


@dataclass
class StoreCrawlResult:
    """Container for a single store's crawl result."""

    booking_id: str
    place_id: str
    place_seq: str
    review_count: int = 0
    reviews: list[dict] = field(default_factory=list)
    error: str | None = None

    @property
    def review_url(self) -> str:
        return f"https://new.smartplace.naver.com/bizes/place/{self.place_seq}/reviews"


@dataclass
class CrawlResult:
    """Container for the entire crawl result."""

    stores: list[StoreCrawlResult] = field(default_factory=list)


class ReviewCrawler:
    """
    Fetches SmartPlace reviews via the new GraphQL API.
    """

    def __init__(self, client: httpx.Client, stop_signal: StopSignal | None = None):
        self.client = client
        self.stop_signal = stop_signal

    def fetch_reviews(
        self,
        stores: list[dict[str, str]],
        log: LogCallback | None = None,
    ) -> CrawlResult:
        def emit(level: str, message: str) -> None:
            if log:
                log(level, message)

        emit("INFO", f"{len(stores)}개 플레이스 리뷰 API 수집을 시작합니다.")

        crawl_results: list[StoreCrawlResult] = []

        for i, store_map in enumerate(stores, 1):
            # 중단 신호 체크
            if self.stop_signal and self.stop_signal.is_set():
                emit("INFO", "크롤링이 중단되었습니다.")
                break

            booking_id = store_map["booking_id"]
            place_seq = store_map["place_seq"]
            place_id = store_map["place_id"]

            emit(
                "INFO",
                f"[{i}/{len(stores)}] 플레이스 {booking_id} (placeId: {place_id}) 리뷰 API 호출",
            )

            try:
                response_data = self._fetch_reviews_for_store(
                    booking_id, place_id, place_seq, emit
                )

                reviews = (
                    response_data.get("data", {}).get("reviews", {}).get("items", [])
                )

                # 서버에서 필터링했으므로 클라이언트 필터링은 불필요합니다.
                review_count = len(reviews)

                result = StoreCrawlResult(
                    booking_id=booking_id,
                    place_id=place_id,
                    place_seq=place_seq,
                    review_count=review_count,
                    reviews=reviews,
                )
                crawl_results.append(result)

                emit(
                    "SUCCESS",
                    f"플레이스 {booking_id} 답글 없는 리뷰 {review_count}건 수집 완료",
                )

            except (httpx.HTTPStatusError, ReviewAPIAuthError) as e:
                error_message = str(e)
                emit("ERROR", f"플레이스 {booking_id} 리뷰 수집 실패: {error_message}")
                crawl_results.append(
                    StoreCrawlResult(
                        booking_id=booking_id,
                        place_id=place_id,
                        place_seq=place_seq,
                        error=error_message,
                    )
                )
            except Exception as e:
                error_message = f"알 수 없는 오류: {e}"
                emit("ERROR", f"플레이스 {booking_id} 리뷰 수집 실패: {error_message}")
                crawl_results.append(
                    StoreCrawlResult(
                        booking_id=booking_id,
                        place_id=place_id,
                        place_seq=place_seq,
                        error=error_message,
                    )
                )

        total_reviews = sum(res.review_count for res in crawl_results)
        emit(
            "SUCCESS",
            f"총 {len(stores)}개 플레이스에서 {total_reviews}건 리뷰 수집 완료",
        )

        return CrawlResult(stores=crawl_results)

    def _fetch_reviews_for_store(
        self,
        booking_id: str,
        place_id: str,
        place_seq: str,
        emit: LogCallback,
    ) -> dict[str, Any]:
        """Fetch all reviews for a single store using the GraphQL API."""

        # GraphQL 변수 설정
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=365 * 2)  # 2년 전
        variables = {
            "input": {
                "size": 10,  # 한 번에 최대 n개 요청
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": today.strftime("%Y-%m-%d"),
                "isSuspended": False,
                "placeId": place_id,
                "hasReply": False,  # 답글 없는 리뷰만 가져오기
            }
        }

        payload = {
            "operationName": "getReviews",
            "variables": variables,
            "query": GET_REVIEWS_QUERY,
        }

        headers = {
            "Content-Type": "application/json",
            "from-system": "smartplace",
            "Origin": "https://new.smartplace.naver.com",
            "Referer": f"https://new.smartplace.naver.com/bizes/place/{place_seq}?bookingBusinessId={booking_id}",
        }

        emit("DEBUG", f"GraphQL URL: {GRAPHQL_API_URL}")
        emit("DEBUG", f"GraphQL Payload: {payload}")
        emit("DEBUG", f"GraphQL Headers: {headers}")

        try:
            response = self.client.post(
                GRAPHQL_API_URL, json=payload, headers=headers, timeout=30.0
            )

            if response.status_code in [401, 403]:
                raise ReviewAPIAuthError(
                    f"GraphQL API 인증 오류 (상태 코드: {response.status_code}) - {response.text}"
                )

            response.raise_for_status()

            data = response.json()
            if "errors" in data:
                raise ReviewAPIAuthError(f"GraphQL API 오류: {data['errors']}")

            return data

        except httpx.HTTPStatusError as e:
            emit(
                "ERROR",
                f"API 요청 실패: 상태 코드 {e.response.status_code} - {e.response.text}",
            )
            raise
        except (ValueError, TypeError) as e:
            emit("ERROR", f"API 응답 파싱 실패: {e}")
            emit("ERROR", f"수신된 응답 내용 (첫 500자): {response.text[:500]}")
            raise ValueError("API 응답을 JSON으로 파싱할 수 없습니다.") from e
