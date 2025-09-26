## 시스템 아키텍처

### 개요
- Windows 데스크톱 앱(Python 3.11+, PySide6)에서 Playwright(Headed)로 네이버 스마트플레이스 UI를 자동화하고, LLM(OpenAI)을 통해 리뷰 답글을 생성합니다. 실행은 `dryrun | assist | auto` 3가지 모드를 지원합니다.

### 구성요소
- UI: 실행/정지, 프롬프트 입력, 진행바/로그 뷰어
- 컨트롤러: 상태머신(실행/정지/에러복구), 시퀀스 제어, 인터럽트 처리
- 자동화 엔진: Playwright 드라이버, 셀렉터 레지스트리, 안정화 대기
- LLM 서비스: `LLMClient` 추상화, OpenAI 구현, 프롬프트 빌더/제약(길이·금칙어)
- 구성/시크릿: `config.yaml` 로더/검증, 환경변수 키
- 저장소: SQLite(`reviews.db`) + 중복 방지/런·제출 기록
- 로깅/리포트: 구조화 로그(JSON 컨텍스트), 실행 요약 레포트

### 데이터 플로우
1. 설정 로드 → 브라우저 세션 준비 → 로그인/쿠키 복원
2. 매장 선택 → 리뷰 탭 진입 → 리뷰 수집(페이지네이션)
3. 미응답 필터 → 최대 10건 큐 구성
4. 프롬프트 생성 → LLM 호출 → 초안 정제(길이/금칙어)
5. assist/auto로 제출 → DOM/토스트 확인
6. 저장/로그/리포트 갱신 → 종료/에러 복구

### 의존성
- 외부: 네이버 웹 UI, OpenAI API
- 내부: `config.yaml`, `selectors.yaml`, SQLite 파일, `.auth/cookies.json`

### 품질 속성
- 안정성: 셀렉터 추상화/폴백, 타임아웃/백오프, 사용자介入 assist 모드
- 보안: 로컬 저장, 키는 환경변수, PII 마스킹 옵션
- 유지보수성: 모듈 경계 명확, 인터페이스 우선 설계

### 상태머신(간단)
- Idle → Running(collect → queue → generate → submit) → Report → Idle
- 중단: Running(any step) → Aborting → CleanUp → Idle

