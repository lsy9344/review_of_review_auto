## 구성 파일 (`config.yaml`) 가이드

### 키와 의미
- **max_reviews_per_run**: 2
- **store_selection**: `first | name | id | all`
- **llm.provider**: `openai`
- **llm.model**: 기본 `gpt-5-nano`
- **llm.api_key_env**: 예) `OPENAI_API_KEY`
- **reply_style.tone**: 존댓말 톤 설명 문자열
- **reply_style.length_limit**: 기본 350
- **reply_style.banned_words**: 금칙어 목록
- **reply_style.closing**: 마지막 문장 템플릿
- **selectors_profile**: `default` 등 프로파일 이름

### 검증 규칙
- 타입 체크 + 허용값 체크 + 기본값 머지
- `max_reviews_per_run` > 10일 경우 10으로 캡
- `length_limit` 200~500 권장, 범위 밖이면 경고 로그

### 샘플
```yaml
run_mode: assist
max_reviews_per_run: 10
store_selection: first
llm:
  provider: openai
  model: gpt-5-nano
  api_key_env: OPENAI_API_KEY
reply_style:
  tone: 친절하고 공손한 존댓말
  length_limit: 350
  banned_words: ["환불", "법적"]
  closing: "소중한 시간 내어 후기를 남겨주셔서 진심으로 감사합니다."
selectors_profile: default
```

