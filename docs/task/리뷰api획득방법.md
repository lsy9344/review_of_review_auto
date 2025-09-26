# 네이버 스마트플레이스 리뷰 크롤링 API 변경 및 성공 과정

이 문서는 기존 REST API 방식의 리뷰 크롤링이 실패하고, 최신 GraphQL API를 성공적으로 호출하기까지의 전체 디버깅 과정과 최종 해결 방법을 기록합니다.

## 1. 기존 REST API 방식의 한계

초기 분석 단계에서는 `partner.booking.naver.com` 도메인의 REST API를 통해 리뷰를 수집하려고 시도했습니다.

- **API 엔드포인트**: `https://partner.booking.naver.com/api/businesses/{booking_id}/reviews`
- **문제점**: 인증된 세션으로 이 API를 호출했을 때, 서버는 오류 코드(4xx)가 아닌 **HTTP 200 (정상)** 상태 코드와 함께 **내용이 완전히 비어있는(empty) 응답**을 반환했습니다.

이로 인해 `JSON 파싱 오류`가 발생했으며, 이는 해당 API 엔드포인트가 더 이상 리뷰 조회용으로 사용되지 않거나, 다른 특별한 인증 방식을 요구하는 것으로 판단되었습니다.

## 2. 새로운 API 발견: GraphQL

문제 해결을 위해 실제 브라우저의 동작을 분석하는 방식으로 전환했습니다. 크롬 개발자 도구의 네트워크 탭을 통해, 스마트플레이스 리뷰 페이지가 실제로 어떤 API를 호출하는지 확인했습니다.

**결정적 발견:**
최신 스마트플레이스 UI는 더 이상 REST API를 사용하지 않고, **GraphQL API**를 통해 데이터를 주고받는 것을 확인했습니다.

- **새로운 API 엔드포인트**: `https://new.smartplace.naver.com/graphql?opName=getReviews`
- **시사점**: 이 발견으로 인해, 리뷰 수집 로직 전체를 기존의 REST 방식에서 GraphQL 방식에 맞게 재작성해야 했습니다.

## 3. GraphQL API 호출 성공 과정

단순히 주소만 바꾸는 것만으로는 충분하지 않았고, 실제 브라우저와 동일한 요청을 만들기 위해 여러 단계의 디버깅을 거쳤습니다.

### 3.1. 요청 구조 분석

GraphQL은 `POST` 방식으로, 정해진 형식의 JSON 본문(Payload)을 보내야 합니다. 브라우저 분석을 통해 다음 구조를 파악했습니다.

- **요청 방식**: `POST`
- **요청 본문 (Payload)**: `operationName`, `variables`, `query` 세 가지 키를 포함하는 JSON
- **핵심 변수**: `variables` 안에 `placeId`가 사용됨을 확인. 이로 인해 `StoreEnumerator` 서비스가 기존의 `placeSeq` 외에 `placeId`도 함께 수집하도록 수정해야 했습니다.

### 3.2. 1차 실패: `BAD_REQUEST` (헤더 불일치)

GraphQL 구조에 맞춰 1차 요청을 보냈으나, 서버는 `BAD_REQUEST` 오류를 반환했습니다. 실제 브라우저의 요청 헤더와 코드의 요청 헤더를 비교한 결과, 다음과 같은 차이점을 발견하고 수정했습니다.

- **누락된 헤더 추가**:
  - `Content-Type: application/json`: POST 요청의 본문이 JSON임을 명시합니다.
  - `from-system: smartplace`: 스마트플레이스 시스템에서 보낸 요청임을 알립니다.
  - `Origin: https://new.smartplace.naver.com`: 요청의 출처를 명시합니다.

### 3.3. 2차 실패: `BAD_REQUEST` (size 파라미터 초과)

필수 헤더를 모두 추가한 후에도 `BAD_REQUEST` 오류가 계속 발생했습니다. 하지만 이번에는 GraphQL 오류 메시지의 `path`가 `['reviews', 'items']`에서 `['reviews', 'totalCount']`로 변경된 것을 확인했습니다. 이는 요청의 일부가 처리되기 시작했음을 의미하는 긍정적인 신호였습니다.

- **원인**: 코드에서는 한 번에 200개의 리뷰를 요청(`"size": 200`)했지만, 실제 브라우저는 2개(`"size": 2`)만 요청하고 있었습니다.
- **가설 및 해결**: `200`이라는 값이 서버가 허용하는 페이지 당 최대 크기를 초과했을 것으로 판단하고, 이 값을 보다 안전한 `100`으로 수정했습니다.

### 3.4. 최종 성공

`size` 파라미터까지 수정한 결과, 마침내 GraphQL 서버로부터 정상적인 리뷰 데이터가 포함된 응답을 받아 크롤링에 성공했습니다.

## 4. 최종 구현 코드

위 과정을 거쳐 완성된 `review_crawler.py`의 리뷰 요청 생성 부분은 다음과 같습니다.

```python
# in app/services/review_crawler.py

def _fetch_reviews_for_store(...):
    # ...
    variables = {
        "input": {
            "size": 100,  # 한 번에 최대 100개 요청
            "startDate": start_date.strftime("%Y-%m-%d"),
            "endDate": today.strftime("%Y-%m-%d"),
            "isSuspended": False,
            "placeId": place_id, # 수집된 placeId 사용
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

    response = self.client.post(GRAPHQL_API_URL, json=payload, headers=headers, timeout=30.0)
    # ...
```

## 5. 결론

- 네이버 스마트플레이스의 리뷰 API는 REST에서 GraphQL로 변경되었습니다.
- 성공적인 API 리버스 엔지니어링을 위해서는, 실제 브라우저의 요청을 **헤더와 본문(Payload)까지 모두** 면밀히 비교하고 1:1로 재현하는 과정이 필수적입니다.
- 서버의 오류 메시지(특히 GraphQL의 `path` 변경)는 디버깅 과정에서 중요한 단서를 제공합니다.
