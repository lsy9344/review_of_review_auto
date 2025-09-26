# `placeSeq` ID 확인 및 수집 방법

## 1. 문제 정의

네이버 스마트플레이스 시스템은 하나의 사업장에 대해 여러 종류의 ID를 사용합니다. 본 프로젝트에서는 두 가지 주요 ID가 발견되었습니다.

- `bookingBusinessId`: `1051707`과 같은 숫자 형태. 주로 백엔드 API에서 사업장을 식별하는 데 사용됩니다.
- `placeSeq`: `9298145`와 같은 문자열 형태. 주로 프론트엔드 URL 경로에 사용됩니다. (예: `.../place/9298145/reviews`)

리뷰 수집 API를 호출하기 위해서는 `bookingBusinessId`를 사용해야 하지만, 동시에 정상적인 요청처럼 보이기 위해 `Referer` 헤더에 `placeSeq`가 포함된 URL을 지정해야 합니다. 따라서, 설정 파일에 있는 `bookingBusinessId`를 가지고 `placeSeq`를 동적으로 찾아내는 방법이 필요했습니다.

## 2. ID 관계 분석 과정

`placeSeq`를 동적으로 찾아내기 위해 다음과 같은 분석 과정을 거쳤습니다.

1.  **리뷰 페이지 URL 분석:**
    - 특정 가게의 리뷰 페이지에 접속했을 때, 브라우저 주소창에 두 ID가 모두 포함된 것을 확인했습니다.
    - `https://new.smartplace.naver.com/bizes/place/{placeSeq}/reviews?bookingBusinessId={bookingBusinessId}`
    - 이를 통해 두 ID가 1:1로 매핑된다는 사실을 알게 되었습니다.

2.  **페이지 소스 분석 시도 (실패):**
    - 로그인 후 나타나는 메인 대시보드 페이지(`https://new.smartplace.naver.com/`)의 HTML 소스 코드에 모든 가게의 ID 정보가 포함되어 있을 것이라 가정했습니다.
    - 하지만, 해당 페이지는 '스켈레톤 UI'를 먼저 보여주고 실제 데이터는 나중에 로드하는 방식으로 동작하여, 초기 HTML에는 원하는 정보가 없었습니다.

3.  **네트워크 트래픽 분석 (성공):**
    - 브라우저의 개발자 도구(F12) `Network` 탭을 사용하여, 메인 대시보드 페이지가 로드된 후 백그라운드에서 호출되는 모든 API 요청을 분석했습니다.
    - 그 결과, 다음 API가 사용자가 관리하는 모든 사업장의 상세 정보 목록을 반환하는 것을 발견했습니다.

## 3. 해결 방법

**API Endpoint:** `https://new.smartplace.naver.com/api/refined-businesses`

- **동작:** 로그인된 세션으로 이 API를 `GET` 방식으로 호출합니다.
- **응답:** 아래와 같은 형식의 JSON 데이터를 반환합니다. 이 데이터 안의 `bookingBusinesses` 배열에 각 사업장 정보가 들어있으며, 여기에 두 종류의 ID가 모두 포함되어 있습니다.

```json
{
    "bookingBusinesses": [
        {
            "placeSeq": "9298145",
            "placeId": "1709826546",
            "bookingBusinessId": 1051707,
            "name": "다비스튜디오셀프사진관송산점",
            ...
        }
    ]
}
```

## 4. 최종 구현

위 분석 결과를 바탕으로 다음과 같이 시스템을 구현했습니다.

1.  **`StoreEnumerator` 서비스 생성 (`app/services/store_enumerator.py`):**
    - `.../api/refined-businesses` API를 호출하는 역할을 전담합니다.
    - `bookingBusinessId`를 입력받아, API 응답에서 일치하는 항목을 찾은 뒤 해당 항목의 `placeSeq` 값을 반환합니다.

2.  **실행 흐름 변경 (`main_window.py`):**
    - 메인 실행 로직(`_OrchestrationWorker`)이 **로그인 -> `StoreEnumerator` 호출 -> 리뷰 수집** 순서로 동작하도록 변경했습니다.
    - `StoreEnumerator`를 통해 얻은 `placeSeq`와 기존 `bookingBusinessId`를 모두 `ReviewCrawler`에 전달합니다.

3.  **`ReviewCrawler` 수정 (`app/services/review_crawler.py`):**
    - `bookingBusinessId`는 리뷰 API를 호출하는 데 사용합니다.
    - `placeSeq`는 `Referer` 헤더를 생성하는 데 사용합니다.
