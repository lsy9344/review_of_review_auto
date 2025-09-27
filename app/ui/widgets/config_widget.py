"""
설정 위젯 - 프롬프트 입력 및 API 설정 관리
"""

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtWidgets import (
    QGroupBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ConfigWidget(QWidget):
    """설정 위젯"""

    # 시그널 정의
    config_changed = pyqtSignal(dict)  # 설정 변경

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_signals()
        self.load_default_values()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 프롬프트 입력 그룹
        prompt_group = QGroupBox("프롬프트 템플릿")
        prompt_layout = QVBoxLayout(prompt_group)

        # 프롬프트 텍스트 영역
        self.prompt_text = QTextEdit()
        self.prompt_text.setMinimumHeight(200)
        self.prompt_text.setPlaceholderText(
            "사용자 정의 프롬프트를 입력하세요 (비워두면 기본 프롬프트 사용)"
        )
        prompt_layout.addWidget(self.prompt_text)

        layout.addWidget(prompt_group)
        layout.addStretch()

    def connect_signals(self):
        """입력 변경 시 설정 업데이트"""
        self.prompt_text.textChanged.connect(self.on_config_changed)

    def load_default_values(self):
        """기본값 로드"""
        # MainWindow와 일치하는 기본 프롬프트 사용
        default_prompt = """# 역할:
당신은 고객 리뷰에 답변하는 사진관 사장님입니다. 고객의 닉네임이 아무리 특이해도 그대로 불러주며 친근하게 소통하세요.
목표:
고객 리뷰를 읽고 진심이 느껴지는 개인화된 답변 작성하기
핵심 규칙:

반드시 안녕하세요, {작성자}님!으로 시작
{작성자} 자리에는 주어진 닉네임을 절대 바꾸지 말고 그대로 사용
'고객님', '회원님' 같은 일반적인 호칭으로 바꾸지 말 것

말투와 스타일:

진짜 사람이 쓴 것처럼 자연스럽게
너무 과하지 않게 친근하고 따뜻하게
이모티콘 2-3개 정도 자연스럽게 섞어서 (🥰, ✨, 😊 등)
실제 사장님이 쓸 법한 표현 사용

답변 작성 가이드:

리뷰에서 언급한 구체적인 내용 언급하기 (아기, 사진, 편집, 서비스 등)
"정말 특별한", "너무 소중했을 것 같아요" 같은 어색한 표현 피하기
실제 사람들이 쓰는 자연스러운 말투로 ("기뻐요", "좋았다니 다행이에요" 등)
매번 다른 느낌으로 시작하되, 이름 부르는 건 절대 바꾸지 않기

사용하지 말아야 할 문장:

추억을 바로 간직하실 수 있어...
긍정적인 반응
행복한 사진 촬영 되시길 바래요
사진이 잘 나왔나 봐요.
상상이 가네요.

주의사항:

250자 이내로 작성
높임말, 존댓말 사용 (반말 금지) ("좋았나봐요"와 같은 반말 금지)
너무 형식적이거나 템플릿 같지 않게
실제 사진관 사장님이 쓸 법한 자연스러운 표현 사용"""
        self.prompt_text.setPlainText(default_prompt)

    def on_config_changed(self):
        """설정 변경 시 시그널 발송"""
        self.config_changed.emit(self.get_config())

    def get_config(self) -> dict:
        """현재 설정값 반환"""
        return {
            "business_type": "일반",
            "tone": "친절하고 정중한",
            "custom_prompt": self.prompt_text.toPlainText(),
        }
