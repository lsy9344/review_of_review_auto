# 네이버 스마트플레이스 API 호출 성공 방법 (403 Forbidden 해결 과정)

이 문서는 네이버 스마트플레이스의 내부 API(`/api/refined-businesses`) 호출 시 발생했던 `403 Forbidden` 오류를 해결하고, 최종적으로 API 호출에 성공하기까지의 과정을 상세히 기록합니다.

## 1. 문제 상황

로그인 로직 수정 후, 쿠키를 이용한 세션 인증에는 성공했지만, 사업장 목록을 가져오는 첫 번째 API 호출에서 지속적으로 `403 Forbidden` 오류가 발생했습니다.

**초기 오류 로그:**
```
[ERROR] 사업장 ID '1051707' 확인 실패: 플레이스 목록 API 요청 실패: 상태 코드 403
```

## 2. 오류 해결 시도 및 실패

일반적인 웹 API의 403 오류 원인을 가정하여 다음과 같은 해결책들을 순서대로 시도했으나, 모두 실패했습니다.

1.  **`Referer` 헤더 추가**: 요청의 출처를 확인하는 `Referer` 헤더가 문제일 것으로 가정하고, `https://new.smartplace.naver.com/`를 추가했으나 실패했습니다.
2.  **`X-Requested-With` 헤더 추가**: AJAX 요청임을 명시하는 `X-Requested-With: XMLHttpRequest` 헤더를 추가했으나 실패했습니다.
3.  **`X-CSRF-TOKEN` 헤더 추가**: CSRF 방지 토큰이 문제일 것으로 가정하고, 로그인 시 획득한 토큰을 헤더에 추가했으나 동일하게 실패했습니다.

## 3. 분석 방법의 전환: 실제 요청 분석

가설 기반의 접근법이 모두 실패함에 따라, **실제 브라우저가 보내는 성공적인 요청**을 직접 분석하는 방식으로 전환했습니다.

사용자의 도움을 받아, 크롬 개발자 도구의 '네트워크(Network)' 탭에서 `/api/refined-businesses` API가 성공적으로 호출될 때의 모든 `Request Headers`(요청 헤더) 정보를 캡처했습니다.

## 4. 결정적 단서 발견: 헤더 비교

캡처된 실제 요청 헤더와 우리 코드(수정 전 `login_service.py`)가 보내는 요청 헤더를 비교한 결과, 다음과 같은 결정적인 차이점을 발견했습니다.

| 헤더                 | 실제 브라우저 요청 | 코드 생성 요청 (오류 당시) | 분석                                                                 |
| -------------------- | ------------------ | -------------------------- | -------------------------------------------------------------------- |
| `x-naver-id`         | **포함됨**         | **누락됨**                 | **문제의 핵심 원인.** 서버가 요청자를 식별하는 필수 헤더였습니다.    |
| `x-csrf-token`       | **누락됨**         | 포함됨                     | 이 API는 CSRF 토큰을 요구하지 않았습니다. 불필요한 헤더였습니다.     |
| `x-requested-with`   | **누락됨**         | 포함됨                     | 이 API는 AJAX 요청 헤더를 요구하지 않았습니다. 불필요한 헤더였습니다. |

**결론:** 우리의 코드는 잘못된 헤더(`x-csrf-token`, `x-requested-with`)를 추가하고, 필수적인 헤더(`x-naver-id`)를 누락하고 있었습니다.

## 5. 최종 해결책

분석 결과를 바탕으로, `app/services/login_service.py`의 `get_authenticated_client` 함수를 다음과 같이 수정하여 실제 브라우저 요청과 동일하게 만들었습니다.

1.  **`user_id` 인자 추가**: `x-naver-id` 헤더에 값을 채우기 위해, 함수가 `user_id`를 인자로 받도록 변경했습니다.
2.  **헤더 재구성**: 불필요한 헤더들을 제거하고, `x-naver-id`를 추가했습니다.

**수정된 `get_authenticated_client` 코드:**
```python
# in app/services/login_service.py

def get_authenticated_client(self, user_id: str) -> httpx.Client:
    """Create and return an authenticated httpx client using stored session data."""
    # ... (쿠키 로드 로직은 동일) ...

    client = httpx.Client()
    # ... (쿠키 설정 로직은 동일) ...

    # Set common headers to mimic a real browser request
    client.headers["Accept"] = "application/json, text/plain, */*"
    client.headers["Accept-Language"] = "ko-KR,ko;q=0.9"
    client.headers["Referer"] = "https://new.smartplace.naver.com/"
    client.headers["User-Agent"] = USER_AGENT
    client.headers["x-naver-id"] = user_id  # 결정적인 헤더 추가!

    return client
```

또한, `app/ui/main_window.py`의 `_OrchestrationWorker`가 위 함수를 호출할 때 `user_id`를 전달하도록 수정했습니다.

```python
# in app/ui/main_window.py

# ...
client = self._login_service.get_authenticated_client(
    user_id=self._config.user_id
)
# ...
```

## 6. 추가 발견: API 응답 구조 변화

403 오류 해결 후, `AttributeError: 'list' object has no attribute 'get'` 라는 새로운 오류가 발생했습니다. 이는 API 응답의 JSON 구조가 예상과 달랐기 때문입니다.

-   **예상**: `{ "bookingBusinesses": [...] }` (딕셔너리)
-   **실제**: `[ { "bookingBusinesses": [...] } ]` (리스트)

`app/services/store_enumerator.py`에서 응답이 리스트일 경우 첫 번째 요소를 사용하도록 간단히 수정하여 이 문제를 해결했습니다.

## 7. 결론

문서화되지 않은 내부 API를 다룰 때는, 가설에만 의존하기보다 실제 성공 사례(브라우저 요청)를 직접 분석하고 1:1로 비교하는 것이 가장 확실한 문제 해결 방법임을 확인했습니다.
