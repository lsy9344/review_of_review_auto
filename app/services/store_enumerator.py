"""
A service to enumerate stores and resolve their various IDs.
"""
from __future__ import annotations

import logging

import httpx

from app.core.errors import StoreEnumerationError

logger = logging.getLogger(__name__)

# 이 API는 로그인 후 메인 대시보드에서 호출되어 관리하는 모든 비즈니스 목록을 반환합니다.
ENUMERATION_URL = "https://new.smartplace.naver.com/api/refined-businesses"


class StoreEnumerator:
    """
    Enumerates businesses associated with the logged-in user and finds the
    mapping between different ID types.
    """

    def __init__(self, client: httpx.Client):
        """
        Initializes the enumerator with an authenticated httpx client.

        Args:
            client: An httpx.Client instance with valid session cookies.
        """
        self.client = client

    def get_store_ids(self, booking_business_id: str, user_id: str) -> dict[str, str]:
        """
        Finds the 'placeSeq' and 'placeId' corresponding to a given 'bookingBusinessId'.

        Args:
            booking_business_id: The booking business ID to find the match for.
            user_id: The Naver user ID for the 'x-naver-id' header.

        Returns:
            A dictionary containing 'place_seq' and 'place_id'.

        Raises:
            StoreEnumerationError: If no matching business is found.
        """
        logger.info("연동된 플레이스 목록을 가져와 ID를 확인합니다...")
        try:
            headers = {
                "Referer": "https://new.smartplace.naver.com/",
                "x-naver-id": user_id,
            }
            response = self.client.get(ENUMERATION_URL, headers=headers, timeout=15.0)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as e:
            raise StoreEnumerationError(
                f"플레이스 목록 API 요청 실패: 상태 코드 {e.response.status_code}"
            ) from e
        except Exception as e:
            raise StoreEnumerationError(f"플레이스 목록 조회 중 알 수 없는 오류: {e}") from e

        if not isinstance(data, list):
            raise StoreEnumerationError(f"API 응답이 예상된 리스트 형태가 아닙니다. 응답: {data}")

        for business_group in data:
            booking_businesses = business_group.get("bookingBusinesses", [])
            for business in booking_businesses:
                if str(business.get("bookingBusinessId")) == booking_business_id:
                    place_seq = business.get("placeSeq")
                    place_id = business.get("placeId")
                    if place_seq and place_id:
                        logger.info(
                            f"ID 확인 성공: bookingId '{booking_business_id}' -> placeSeq '{place_seq}', placeId '{place_id}'"
                        )
                        return {"place_seq": place_seq, "place_id": place_id}
                    raise StoreEnumerationError(
                        f"'{booking_business_id}'에 해당하는 플레이스는 찾았지만, placeSeq 또는 placeId가 없습니다."
                    )

        raise StoreEnumerationError(
            f"설정된 bookingBusinessId '{booking_business_id}'에 해당하는 플레이스를 찾을 수 없습니다. "
            "계정에 연결된 플레이스가 맞는지 확인해주세요."
        )