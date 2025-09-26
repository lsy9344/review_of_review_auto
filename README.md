# 네이버 스마트플레이스 리뷰 자동응답 시스템

네이버 스마트플레이스의 리뷰에 자동으로 답글을 생성하고 등록하는 데스크톱 애플리케이션입니다.

## 주요 기능

- **네이버 로그인**: 쿠키 재사용으로 편리한 로그인
- **리뷰 자동 수집**: 사장님 답글이 없는 리뷰 자동 탐지
- **LLM 답글 생성**: OpenAI GPT를 활용한 자연스러운 답글 생성
- **3가지 실행 모드**: DryRun(미리보기), Assist(반자동), Auto(완전자동)
- **안전 장치**: 속도 제한, 글자수 제한, 금칙어 필터
- **실시간 모니터링**: 진행 상황 및 결과 실시간 표시

## 시스템 요구사항

- **운영체제**: Windows 10 이상
- **Python**: 3.11 이상
- **메모리**: 최소 4GB RAM
- **네트워크**: 인터넷 연결 필수

## 설치 방법

### 1. Python 환경 설정

```bash
# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화 (Windows)
venv\\Scripts\\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

OpenAI API 키를 환경변수에 설정:

```bash
# Windows
set OPENAI_API_KEY=your_api_key_here

# macOS/Linux
export OPENAI_API_KEY=your_api_key_here
```

## 실행 방법

### 일반 모드 실행

```bash
python run.py
```

또는

```bash
python -m app.main
```

### 개발 모드 실행 (자동 재시작)

코드 수정 시 자동으로 프로그램이 재시작됩니다:

```bash
# 기본 개발 모드
python dev.py

# 특정 디렉토리만 감시
python dev.py --watch app configs

# 커스텀 명령어로 실행
python dev.py --command "python -m pytest"

# 상세 로그 출력
python dev.py --verbose
```

**개발 모드 특징:**
- 📁 `.py`, `.ui`, `.qss`, `.yaml`, `.json` 파일 변경 감지
- 🚫 `__pycache__`, `logs`, `.git` 등 자동 제외
- ⚡ 1초 내 중복 재시작 방지
- 🔄 실시간 프로세스 출력 표시
- ⏹️ Ctrl+C로 안전한 종료

### 실행 스크린샷

![메인 화면](docs/screenshots/main_window.png)

## 사용법

### 1. 로그인
- 네이버 아이디와 비밀번호를 입력
- "로그인 테스트" 버튼으로 연결 확인
- 성공 시 쿠키가 저장되어 다음 실행 시 자동 로그인

### 2. 설정
- **프롬프트 탭**: 답글 생성을 위한 LLM 프롬프트 설정
- **실행 설정 탭**: 모드 선택, 처리 제한, 지연 시간 설정
- **LLM 설정 탭**: OpenAI 모델 및 파라미터 설정

### 3. 실행
- "실행" 버튼으로 시작
- "정지" 버튼으로 즉시 중단
- "일시정지" 버튼으로 임시 중단/재개

### 4. 결과 확인
- **처리 결과 탭**: 개별 리뷰 처리 현황
- **실행 로그 탭**: 상세 실행 로그
- **오류 분석 탭**: 오류 유형별 분석

## 설정 파일

### config.yaml
```yaml
max_reviews_per_run: 10
run_mode: assist
llm:
  provider: openai
  model: gpt-4o-mini
reply_style:
  tone: 친절하고 공손한 존댓말
  length_limit: 350
  banned_words: ["환불", "법적"]
```

### selectors.yaml
```yaml
default:
  login:
    id_input: 'input#id'
    pw_input: 'input#pw'
  review:
    item: 'div.review-card'
    text: 'div.review-text'
    has_owner_reply: 'div.owner-reply'
```

## 안전 기능

- **속도 제한**: 동작 간 2-6초 랜덤 지연
- **처리 제한**: 1회 최대 10건 처리
- **글자수 제한**: 350자 이하 답글 생성
- **금칙어 필터**: 민감한 단어 자동 제거
- **중복 방지**: 이미 답글이 있는 리뷰 건너뜀

## 문제 해결

### 자주 발생하는 오류

1. **로그인 실패**
   - 네이버 계정 정보 확인
   - 2단계 인증 설정 확인
   - 쿠키 파일 삭제 후 재시도

2. **DOM 요소 찾기 실패**
   - selectors.yaml 파일 업데이트
   - 네이버 페이지 구조 변경 확인

3. **LLM API 오류**
   - OPENAI_API_KEY 환경변수 확인
   - API 사용량 및 잔액 확인

### 로그 파일 위치

- **애플리케이션 로그**: `logs/app.log`
- **실행 로그**: `runs/YYYY-MM-DD-HH-MM-SS.log`
- **오류 로그**: `logs/error.log`

## 개발자 정보

### 프로젝트 구조

```
app/
├── ui/                 # 사용자 인터페이스
│   ├── widgets/       # UI 위젯들
│   ├── styles/        # 스타일시트
│   └── viewmodel.py   # 데이터 바인딩
├── core/              # 핵심 로직 (향후 구현)
├── services/          # 비즈니스 서비스 (향후 구현)
└── main.py           # 애플리케이션 진입점
```

### 기여 방법

1. 이슈 등록
2. 브랜치 생성
3. 기능 구현
4. 테스트 작성
5. Pull Request 제출

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 면책 조항

- 이 도구는 교육 및 개인 사용 목적으로 제작되었습니다
- 네이버 서비스 약관을 준수하여 사용하세요
- 대량 또는 상업적 사용은 금지됩니다
- 사용으로 인한 계정 제재는 사용자 책임입니다

## 지원

문제가 있으시면 GitHub Issues에 등록해주세요.
