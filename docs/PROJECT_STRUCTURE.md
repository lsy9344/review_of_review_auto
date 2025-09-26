## 프로젝트 디렉터리 구조(제안)

```
app/
  core/
    config.py            # 설정 스키마/로드/검증
    errors.py            # 예외 정의 (LoginError, DomMismatchError 등)
    events.py            # RunEvent, StoreEvent, ReviewEvent 등 이벤트 타입
    state.py             # Orchestrator 상태/전이 정의
    logging.py           # 로거 초기화 유틸
  domain/
    models.py            # Store, Review, ReplyDraft, Submission, RunStats 등 (Pydantic)
    prompts.py           # 템플릿/금칙어/후처리 규칙
    selectors.py         # 논리키→CSS/XPath 매핑 로더
  infra/
    browser.py           # Playwright 런처, 쿠키 재사용, 안정화/대기 유틸
    llm_openai.py        # LLMClient 인터페이스 구현(OpenAI)
    db.py                # SQLite 초기화/마이그레이션
  services/
    repository.py        # DB CRUD (runs, reviews, submissions)
    selector_resolver.py # selectors.yaml 해석기(프로파일 지원)
    store_enumerator.py  # 매장 리스트 파싱/순회
    review_crawler.py    # 리뷰 수집/미응답 필터/페이지네이션
    reply_generator.py   # LLM 호출/길이제한/금칙어/톤 후처리
    submitter.py         # 답글 입력/제출/검증
    throttle.py          # 랜덤 지연, 속도 제어(2~6초)
    captcha_watch.py     # CAPTCHA/2FA 감지 후 알림(오토 중단 정책)
    stop_signal.py       # 스레드-세이프 플래그/컨텍스트 매니저
  ui/
    main_window.py       # 실행/정지 버튼, 진행률, 로그 뷰
    viewmodel.py         # UI<->오케스트레이터 바인딩
  runner.py              # 오케스트레이터 진입점(run_once)
  main.py                # 앱 엔트리포인트 (GUI 부팅)
configs/
  config.example.yaml
  selectors.example.yaml
assets/
  icons/
  prompt_samples/
tests/
  unit/
  e2e/
```

### 빌드 산출물
- `reply-bot.exe` (PyInstaller)
- 동작 파일: `config.yaml`, `selectors.yaml`, `reviews.db`, `.auth/cookies.json`

