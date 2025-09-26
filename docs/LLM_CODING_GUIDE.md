## LLM-우호적 코딩 가이드

### 원칙
- 함수는 작고 단일 책임, 명시적 입력/출력
- 인터페이스 우선, 구현 분리/교체 가능
- 결정적 동작, 랜덤/시간 의존은 주입 가능 파라미터화
- 예외 메시지는 행동 지침 포함
- 셀렉터 키는 상수/열거형으로 관리
- 대기/재시도는 타임아웃/백오프 규칙 명시
- 로그는 구조화(JSON), PII 마스킹

### 워크플로우
1. PRD/TASKS를 참조하여 모듈/함수 시그니처 생성
2. 인터페이스/추상화 먼저 작성 → 간단한 구현체 추가
3. 순수 함수(파싱/검증/프롬프트)는 테스트 우선
4. DOM/네트워크 의존은 어댑터로 분리
5. 구성값/셀렉터는 주입, 하드코딩 금지

### 예시 시그니처
```python
class LLMClient(Protocol):
    def generate(self, prompt: str, max_tokens: int | None = None) -> str: ...

class SelectorRegistry:
    def get(self, key: str) -> str: ...
```

