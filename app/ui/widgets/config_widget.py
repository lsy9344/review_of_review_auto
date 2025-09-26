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
        default_prompt = "안녕하세요~ {작성자}님~과 같은 비슷한 패턴으로 모두 다르게  시작하세요. ({작성자}는 실제 크롤링 한 작성자를 넣으세요}) 사람같은 말투를 사용하고 동일한 단어를 너무 많이 반복하지 말 것, 너무 딱딱하게 들리지 않게 좀 친근한 스타일을 사용하세요. 모든 답변을 하나의 로봇이 작성한것 같은 느낌을 없애고 다양하게 작성하세요."
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
