# 네이버 스마트플레이스 답글 등록 API 분석 결과

## 1. API 엔드포인트

- **URL:** `https://new.smartplace.naver.com/graphql?opName=createReply`
- **Method:** `POST`

## 2. 주요 요청 헤더 (Headers)

- `content-type`: `application/json`
- `cookie`: NID_SES, NID_AUT, csrf_token 등 인증 및 세션 관련 쿠키 포함
- `referer`: `https://new.smartplace.naver.com/bizes/place/{place_seq}/reviews?bookingBusinessId={booking_id}&menu=visitor` 형식
- `from-system`: `smartplace`

## 3. 요청 페이로드 (Payload)

요청 본문은 다음 세 가지 키를 가진 JSON 객체입니다.

- `operationName`: `"createReply"`
- `variables`: API에 전달하는 변수
- `query`: 실행할 GraphQL 뮤테이션

### Variables 상세

`variables` 객체는 `input` 객체를 포함하며, `input`의 구조는 다음과 같습니다.

```json
{
  "input": {
    "text": "등록할 답변 내용",
    "reviewId": "답변을 달 리뷰의 고유 ID",
    "bookingBusinessId": "사업장의 booking ID"
  }
}
```

### Query (GraphQL Mutation)

```graphql
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
```
