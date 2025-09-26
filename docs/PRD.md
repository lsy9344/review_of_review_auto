# 네이버 스마트플레이스 리뷰 자동응답 PRD

> 목적: Windows 환경에서 네이버 스마트플레이스의 각 매장 리뷰 중 “사장님 답글이 없는 리뷰”를 최대 10개까지 자동(또는 반자동)으로 응답한다. 답변 문구는 사용자가 지정한 프롬프트/톤을 기반으로 LLM이 생성한다. 실행 과정이 보이는 **헤디드(Headed)** 자동화를 기본으로 하며, DOM 변경에 강한 **셋렉터 추상화 계층**과 \*\*안전 장치(검수·속도 제한·CAPTCHA 대응)\*\*를 포함한다.

---

## 1. 범위 정의

* **In Scope**

  * 네이버 → 스마트플레이스 로그인 (쿠키 재사용 + 수동 2FA 지원)
  * 매장 목록에서 1개 매장 선택 후 리뷰 페이지 진입
  * 리뷰 목록 크롤링(화면 기반), **‘사장님 답글 없음’** 상태 식별
  * 사용자 프롬프트(톤/금칙어/길이) + 리뷰 텍스트를 **자동 크롤링**하여 LLM으로 답변 생성
  * 1회 실행 시 **최대 10건 자동 등록**
  * 실행 로그/에러 캡처, 재시도 큐, 중복 방지
  * 로컬 구성: `config.yaml` + SQLite(`reviews.db`)

* **Out of Scope**

  * 네이버 공식 비공개 API 활용(없음 가정)

---

## 2. 성공 지표 (KPIs)

* 리뷰 응답 커버리지: 미응답 중 \*\*≥95%\*\*를 후보로 수집
* 제출 성공률: 자동 제출 시 **≥90%** (CAPTCHA/DOM변경 제외)
* 안전제어: 1회 10건 제한, 클릭·입력 사이 랜덤 지연(2\~6초), 인지 가능한 헤디드 실행
* 운영 편의: **무설명 실행 가능한 단일 `.exe`** + 시각 로그/진행바

---

## 3. 사용자 시나리오 (핵심 플로우)

1. 실행파일을 더블클릭 → 로그인 창 또는 저장 쿠키 사용

2. 첫 번째 매장 프로세스 끝난 후 **자동으로 두 번째 매장 \~ 마지막 매장까지 순차 실행**(매장별: 리뷰 수집 → 답변 생성 → 제출 자동화)

3. 리뷰 탭 자동 진입 → 페이지 내 아이템 스캔

4. \*\*‘사장님 답글 없음’\*\*인 리뷰만 수집 → 상단 패널에 카드로 미리보기

5. 우측 패널의 **프롬프트 입력란**에 톤/스타일 지시어 입력 (템플릿 선택 가능)

6. **생성** 클릭 → 각 리뷰별 제안 답변 카드가 채워짐

7. **오토 모드 전용**: '실행' 버튼으로 시작, '정지' 버튼 클릭 시 **모든 시퀀스 즉시 종료**(현재 리뷰/매장 루틴 포함).

8. 완료 후 리포트(성공 N건/스킵 사유 목록)

---

## 4. 아키텍처 & 기술 스택 제안

* **형태**: **Windows 데스크톱 앱 (결정)**
* **언어/프레임워크**:

  * **Python 3.11+**
  * **Playwright**(Chromium, Headed)
  * **PySide6**(또는 PySimpleGUI)
  * **SQLite**
  * **PyInstaller** (단일 `.exe`)
  * **OpenAI API** (예: `gpt-4o-mini`; 환경변수 `OPENAI_API_KEY` 사용)

---

## 5. 워크플로우 (상세)

### 5.1 로그인

* 쿠키 저장소(`.auth/cookies.json`) 우선 사용 → 만료 시 수동 로그인 유도
* 2FA/CAPTCHA 발생 시 **어시스트 모드로 일시 전환**(사용자 해결 대기)
* 로그인 성공 신호: 프로필 메뉴/매장 목록 DOM 존재 확인

### 5.2 매장 선택

* 기본값: 첫 번째 매장 자동 진입(요구사항 반영)
* 옵션: 드롭다운에서 매장 선택(다중 매장 확장 대비)

### 5.3 리뷰 페이지 진입 & 파싱

* 안정성: **셋렉터 추상화 계층**

  * `selectors.yaml`에 **의미 기반 키** → 실제 CSS/XPath 매핑
  * 예: `review.item`, `review.text`, `review.hasOwnerReply`, `review.replyButton`, `review.replyTextarea`, `review.submitBtn`, `pagination.next`
* 각 리뷰 카드에서 추출: `review_id`, `작성일`, `별점`, `본문`, `사진여부`, `사장님답글여부`
* 페이지네이션: 다음 페이지 버튼 탐지 → 10건 충족 시 조기 종료

### 5.4 미응답 필터 & 큐잉

* 조건: `hasOwnerReply == false`
* 중복 방지: SQLite `unique(review_id, store_id)`
* 실행당 상한: 최대 10건(설정 가능)

### 5.5 LLM 답변 생성

* 입력: 사용자 프롬프트 템플릿 + 리뷰 본문 + 메타(방문일/별점 등)
* 제약: 길이 제한(네이버 입력란 최대 글자수 고려), **금칙어 필터**, 말투(존댓말) 고정
* 샘플 템플릿(요약):

  * 톤: 따뜻한/차분한/신속대응
  * 구조: 감사 → 구체사항 언급 → 개선/재방문 제안 → 마무리 인사
* 반복 생성 방지: \*\*유사도 체크(문장 임베딩)\*\*로 동일문구 남용 최소화(선택)

### 5.6 제출(오토)

* 자동으로 텍스트 입력 → 제출 → 성공 토스트/DOM 변화 확인 → 다음 리뷰로 진행
* 클릭/입력 사이 **랜덤 지연 2\~6초** + 안정화 대기(`wait_for_selector`)
* **정지 버튼** 클릭 시 즉시 종료(현재 입력/제출 루틴도 중단)

### 5.7 로깅 & 리포트

* `runs/날짜-시간.log` + SQLite `runs`, `submissions`
* 실패 사유 분류: 로그인/DOM불일치/CAPTCHA/길이제한/네트워크/권한
* 완료 후 요약: 성공/실패/스킵 목록 + 재시도 버튼

---

## 6. 구성 파일 예시

### 6.1 `config.yaml`

````yaml
max_reviews_per_run: 10
store_selection: all  # all = 첫 매장부터 마지막 매장까지 순차 실행
llm:
  provider: openai
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
reply_style:
  tone: 친절하고 공손한 존댓말
  length_limit: 350
  banned_words: ["환불", "법적"]
  closing: "소중한 시간 내어 후기를 남겨주셔서 진심으로 감사합니다."
selectors_profile: default
controls:
  start_button: true
  stop_button: true
```yaml
run_mode: assist   # dryrun | assist | auto
max_reviews_per_run: 10
store_selection: first   # first | name | id
llm:
  provider: openai       # openai | gemini | openrouter | local
  model: gpt-4o-mini
  api_key_env: OPENAI_API_KEY
reply_style:
  tone: 친절하고 공손한 존댓말
  length_limit: 350   # 네이버 입력 제한 고려 (필요시 조정)
  banned_words: ["환불", "법적"]
  closing: "소중한 시간 내어 후기를 남겨주셔서 진심으로 감사합니다."
selectors_profile: default
````

### 6.2 `selectors.yaml`

```yaml
default:
  login:
    id_input: 'input#id'
    pw_input: 'input#pw'
    submit_btn: 'button[type="submit"]'
  nav:
    store_list: 'div.store-list'
    first_store: 'div.store-list > .store-item:first-child'
    review_tab_btn: 'a[aria-controls="reviews"]'
  review:
    item: 'div.review-card'
    text: 'div.review-text'
    has_owner_reply: 'div.owner-reply, div.reply--owner'
    reply_button: 'button.reply'
    reply_textarea: 'textarea.reply-input'
    submit_btn: 'button.submit-reply'
    next_page: 'button.pager-next'
```

> 실제 셀렉터는 사이트 DOM에 따라 조정 필요. **키 이름은 고정**, 값만 바꿔 유지보수 비용 최소화.

---

## 7. 데이터 모델 (SQLite)

* `stores(store_id TEXT PRIMARY KEY, name TEXT)`
* `reviews(review_id TEXT, store_id TEXT, created_at TEXT, rating INT, text TEXT, has_owner_reply INT, UNIQUE(review_id, store_id))`
* `submissions(review_id TEXT, store_id TEXT, status TEXT, error TEXT, created_at TEXT)`
* `runs(run_id TEXT PRIMARY KEY, started_at TEXT, mode TEXT, success INT, fail INT, skipped INT)`

---

## 8. 에러 처리 & 안전장치

* **CAPTCHA/2FA**: 감지 시 화면 알림 + **사용자 처리 대기**
* **DOM 변경**: 셀렉터 매칭 실패 시 `selectors_profile` 폴백(secondary) + 진단 덤프(문서 스냅샷 HTML 저장)
* **길이 초과**: 자동 축약(요지 유지) 후 제출, 실패 시 수동 검수 모드 제안
* **중복 제출 방지**: `submissions` 확인 → 이미 성공이면 스킵
* **속도 제한**: 랜덤 지연 + 한 번에 10건 한도 + 실행 간 최소 간격 설정(옵션)

---

## 9. 보안/컴플라이언스

* **계정·쿠키**는 로컬에만 저장, Windows DPAPI로 암호화(또는 OS 사용자 단위 폴더 권한)
* 서비스 약관 준수, 자동화 티가 나는 대량·고빈도 액션 금지
* LLM로 전송되는 데이터: **민감정보 마스킹**(전화·주문번호 등) 옵션 제공

---

## 10. 테스트 계획 & 수용 기준

* **수집 정확도**: 표시상 미응답 10건 중 ≥9건을 정확히 탐지
* **제출 검증**: 제출 후 DOM에 **사장님 답글 블록** 생성 확인
* **회귀**: 셀렉터 변경 시 `selectors.yaml`만 교체하여 동일 시나리오 통과
* **장애 시나리오**: 로그인 실패, CAPTCHA, 네트워크 오류 각각에서 안전 복구

---

## 11. 전달물

* `reply-bot.exe` (단일 실행파일)
* `config.yaml`, `selectors.yaml`, `README_설치_가이드.md`
* (옵션) `prompt_samples/친절_기본.txt`, `prompt_samples/사과_필요.txt`

---

## 12. 구현 계획 (20년차의 제안)

* **Sprint 0 (0.5d)**: 계정/DOM 시료 수집, 셀렉터 초안, 리스크 점검
* **Sprint 1 (1.5d)**: 로그인·쿠키·매장선택·리뷰 파싱(헤디드), 드라이런 CSV
* **Sprint 2 (1.5d)**: LLM 연결, 템플릿/금칙어/길이제어, 어시스트 모드 제출
* **Sprint 3 (1.0d)**: 오토 모드, 로그/리포트, SQLite 중복방지, 10건 제한
* **Sprint 4 (0.5d)**: 패키징(.exe), 설정 파일, 사용 가이드/동영상 캡쳐

---

## 13. 필요 정보 요청 (체크리스트)

1. **매장 목록이 보이는 페이지의 HTML/스크린샷**

   * 가능한 경우: 매장 카드 1개 `outerHTML` 복사 → 붙여넣기
2. **리뷰 리스트 1개 아이템의 HTML/스크린샷**

   * ‘사장님 답글 영역’이 있는 사례(있음/없음 각각 1개)
3. **리뷰 답글 입력란의 글자수 제한** (정확 숫자)
4. **로그인 방식**: 일반 로그인/2FA 방식, 백업 이메일·인증앱 여부
5. **운영 정책**: 1일 최대 실행 횟수, 심야 시간대 제한 여부
6. **답변 톤/금칙어/브랜드 문장** 예시 3개 (긍정/보통/부정 리뷰용)

> 위 ①\~②의 DOM 시료만 확보되면, `selectors.yaml`을 신속히 고정하고 바로 구현 가능합니다.

---

## 14. 추후 확장

* 다중 매장 일괄 처리(순차) / 매장별 톤 프리셋
* LLM 비용 절감: 로컬 요약 → 짧은 프롬프트 입력
* 부정 리뷰 시 **상담 폼 링크** 자동 첨부 등 워크플로우 분기

---

## 15. 의사코드 (핵심 루프)

```pseudo
login_or_use_cookie()
select_store(first=True)
go_to_reviews()
reviews = collect_reviews_until(limit=20)  # 후보는 넉넉히
candidates = filter(r in reviews where r.has_owner_reply == False)
queue = take_first(candidates, max_n=10)
for r in queue:
  draft = llm_generate(prompt_template, r.text, meta=r)
  if mode == 'assist':
    paste_and_focus(r, draft); user_confirms_submit()
  elif mode == 'auto':
    paste_and_submit(r, draft)
  else:
    save_csv(r, draft)
  log_result(r, status)
report()
```

---

## 16. 운영 가이드 (요약)

1. `config.yaml`에서 `run_mode`와 LLM 설정 확인
2. `reply-bot.exe` 실행 → 로그인/매장 선택
3. 우측 프롬프트에 톤 지정 → **생성**
4. '실행'으로 시작하고, 중단이 필요하면 **'정지'** 버튼 클릭(즉시 종료)
5. 리포트 확인, 필요한 경우 재시도

---

## 17. 리스크 & 대응

* **도메인/DOM 변경**: 셀렉터 프로파일로 대응, 변경 시에도 코드 수정 없이 교체 가능
* **계정 리스크**: 사람이 보는 속도/패턴, 오토 대신 어시스트 기본 운영 권장
* **LLM 품질**: 금칙어·톤 템플릿 + 길이 제어 + 반복문구 유사도 감시

---

## 18. 부록: 프롬프트 템플릿 샘플

```
[역할]
- 당신은 아기/육아 고객이 많은 셀프사진관 매장의 점주입니다.
- 따뜻하고 공손한 한국어 존댓말로만 답합니다.

[지시]
- 고객 리뷰의 핵심(칭찬/불편)을 1문장으로 요약 후, 감사/개선/재방문 유도 순서로 3~5문장 작성.
- 과도한 사과/보상 약속 금지. 민감정보 언급 금지.
- 최대 ${length_limit}자.

[입력]
- 별점: {rating}/5
- 리뷰 본문: "{review_text}"
- 매장명: {store_name}

[출력]
- 매장 답글(따옴표 없이 한 단락)
```

---

## 19. 시스템 아키텍처 개요

* **컴포넌트**
  * UI(데스크톱): PySide6 기반, 실행/정지/프롬프트 패널, 진행바/로그 뷰어
  * 컨트롤러: `run_mode(dryrun|assist|auto)` 상태머신, 시퀀스 제어 및 인터럽트 처리
  * 자동화 엔진: Playwright(Chromium, Headed) 드라이버 + 셀렉터 레지스트리
  * LLM 서비스: `LLMClient` 추상화(OpenAI 기본), 프롬프트 빌더/길이·금칙어 필터
  * 구성/시크릿: `config.yaml` 로더/검증, 환경변수 키
  * 저장소: SQLite(`reviews.db`), 중복 방지/런/제출 로그
  * 로깅/리포트: 파일 로그(`runs/*.log`) + 실행 리포트 요약

* **데이터 경로(고수준)**
  1) UI에서 실행 → 컨트롤러가 브라우저 세션 생성/로그인
  2) 네비게이션 → 리뷰 파싱 → 미응답 필터/큐잉
  3) 각 리뷰에 대해 프롬프트 생성 → LLM 호출 → 초안 생성
  4) assist: 붙여넣기 후 사용자 확인 / auto: 자동 제출
  5) 결과를 SQLite/로그에 기록, 리포트 렌더링

---

## 20. 프로젝트 디렉터리 구조(제안)

```
review_reply_auto/
  app/
    controllers/
    ui/
    automation/
    selectors/
    llm/
    config/
    storage/
    logging/
    utils/
  resources/
    selectors.yaml
    prompt_samples/
  docs/
  runs/
  .auth/
  scripts/
  tests/
```

* `app/controllers`: 실행 플로우/상태머신, 중단 처리
* `app/ui`: PySide6 화면, 이벤트 바인딩
* `app/automation`: Playwright 시나리오, DOM 조작, 안정화 대기
* `app/selectors`: 의미 키 ↔ 실제 셀렉터 맵 로더/검증, 프로파일 폴백
* `app/llm`: `LLMClient` 인터페이스, OpenAI 구현, 프롬프트 빌더
* `app/config`: `config.yaml` 스키마/검증/기본값
* `app/storage`: SQLite 리포지토리, 중복 키 보장
* `app/logging`: 표준 로거/이벤트, 리포트 생성기
* `resources`: 정적 셀렉터/프롬프트 예시

---

## 21. 모듈 설계와 인터페이스(요약)

* `ConfigLoader`/`ConfigValidator`
  * `load(path) -> Config`
  * 검증: 타입/허용값/기본값 merge, 오류 메시지 일관화

* `SelectorRegistry`
  * `load(profile) -> SelectorMap`
  * `get(key) -> css/xpath`
  * 폴백 프로파일 지원, 진단 덤프(매칭 실패 시)

* `NaverSessionManager`
  * `login_or_resume()` 쿠키 복원→만료 시 수동 로그인 대기→성공 신호 검증

* `StoreNavigator`
  * `select_first_or(target)` 및 리뷰 탭 진입

* `ReviewParser`
  * `collect_until(limit) -> list[ReviewItem]`
  * 페이지네이션/안정화 대기/필드 추출

* `ReviewQueueBuilder`
  * `filter_unreplied(reviews) -> list[ReviewItem]`
  * `take_first(candidates, n) -> list[ReviewItem]`

* `LLMClient`
  * `generate(prompt: PromptInput) -> str`
  * 구현체: `OpenAIClient`

* `ReplyGenerator`
  * 템플릿 머지, 길이 제한/금칙어 필터, 존댓말 고정

* `SubmissionExecutor`
  * `assist_mode(review, draft)` / `auto_mode(review, draft)`
  * 제출 확인: 토스트/DOM 변화 검증

* `PersistenceRepository`
  * `upsert_reviews`, `record_submission`, `record_run`

---

## 22. 런타임 데이터 플로우

1) Config 로드/검증 → 브라우저 세션 생성
2) 로그인 상태 확인(쿠키→수동) → 매장 선택 → 리뷰 탭 진입
3) 리뷰 수집(안정화 대기/페이지네이션) → 미응답 필터 → 큐 생성(max 10)
4) 각 항목에 대해: 프롬프트 빌드 → LLM 호출 → 초안 정제(길이/금칙어)
5) assist/auto 분기로 제출 → DOM 확인 → 저장소/로그 기록
6) 인터럽트(정지 버튼) 시 즉시 루틴 중단, 리소스 정리 및 리포트

---

## 23. 로깅/이벤트 표준

* 레벨: INFO(진행), WARN(복구 가능), ERROR(실패), DEBUG(선택)
* 에러 코드 예시
  * `AUTH_CAPTCHA`, `AUTH_2FA_REQUIRED`
  * `DOM_SELECTOR_MISSING`, `DOM_STALE`
  * `LLM_BAD_OUTPUT`, `LLM_LENGTH_OVERFLOW`
  * `SUBMIT_FAILED`, `NETWORK_TIMEOUT`
  * `DUPLICATE_SKIPPED`, `USER_ABORT`
* 포맷: `ts | run_id | level | code | message | ctx(json)`
* 실행 리포트: 성공/실패/스킵 카운트와 상세 목록(JSON + 화면 요약)

---

## 24. LLM 프롬프트/토큰/비용 전략

* 모델: 기본 `gpt-5-nano`, 토큰 상한 및 요금 고려
* 토큰 예산: 리뷰 본문 길이 트리밍(문장 단위), 메타는 숫자 위주
* 샘플링: `temperature 0.5`, 반복 패널티로 유사 문장 남용 억제
* 길이 제한: `${length_limit}` 강제, 초과 시 자동 축약 규칙
* 금칙어: 사전 필터 + 사후 검수(치환/제거)
* 캐싱: 동일/유사 리뷰 임베딩 유사도(옵션)로 중복 방지

---

## 25. 기능 단위 태스크(DoD 포함)

1) 로그인/세션 관리
   - DoD: 쿠키 재사용/만료 시 수동 로그인 전환, 성공 신호 검증
2) 매장 선택/탭 진입
   - DoD: 첫 매장 자동 진입, 리뷰 탭 DOM 확인
3) 셀렉터 프로파일 로더/폴백
   - DoD: 프로파일 2개 전환, 미스매치 시 진단 덤프 저장
4) 리뷰 파서(페이지네이션 포함)
   - DoD: 샘플 페이지에서 20개 수집 정확도 ≥90%
5) 미응답 필터/큐 빌더
   - DoD: `has_owner_reply==false` 정확 필터, 최대 10건 제한
6) LLM 클라이언트 + 프롬프트 빌더
   - DoD: 샘플 입력으로 합리적 초안 반환, 오류 리트라이
7) 길이/금칙어/톤 제약
   - DoD: 150자 이하 보장, 금칙어 미포함, 존댓말 유지
8) 제출 실행기(assist/auto)
   - DoD: DOM 변화/토스트 확인, 실패 재시도 1회
9) 정지 버튼 인터럽트
   - DoD: 현재 루틴 즉시 중단, 자원 정리, 리포트 표시
10) 로깅/리포트
   - DoD: 표준 포맷 로그 생성, 성공/실패/스킵 요약 표시
11) SQLite 저장소
   - DoD: 중복 제출 방지 유니크 키, 기본 CRUD 동작
12) 구성 로더/검증
   - DoD: 잘못된 키/타입에 친절한 메시지, 기본값 적용
13) 패키징(.exe)
   - DoD: Windows 에서 무설명 실행, LLM 키만 필요

---

## 26. LLM-우호적 코딩 가이드라인

* 함수는 30~50줄 이하, 단일 책임, 명시적 입력/출력 타입
* 인터페이스 우선(추상화) 후 구현체 교체 가능하게 설계
* 결정적 동작(랜덤 지연은 파라미터화), 외부 상태 최소화
* 예외 메시지는 행동 지침 포함(원인/재시도/수동모드 전환)
* 셀렉터 키는 상수/열거형으로 관리, 하드코딩 금지
* 네트워크/DOM 대기는 가시적 타임아웃/백오프 규칙 사용
* 로그 컨텍스트는 JSON으로 구조화, PII 마스킹
* 테스트 가능한 분리: 파싱/프롬프트/검증 로직은 순수 함수로 구성
