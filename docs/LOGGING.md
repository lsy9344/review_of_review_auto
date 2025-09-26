## 로깅/리포트 표준

### 레벨
- INFO, WARN, ERROR, DEBUG

### 에러 코드
- AUTH_CAPTCHA, AUTH_2FA_REQUIRED
- DOM_SELECTOR_MISSING, DOM_STALE
- LLM_BAD_OUTPUT, LLM_LENGTH_OVERFLOW
- SUBMIT_FAILED, NETWORK_TIMEOUT
- DUPLICATE_SKIPPED, USER_ABORT

### 포맷
`ts | run_id | level | code | message | ctx(json)`

### 리포트
- 실행 요약(JSON + 화면 요약): 성공/실패/스킵 카운트와 상세 목록

