"""
사업장 리스트 위젯 - 사업장 번호 입력
"""

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtWidgets import QGroupBox, QLabel, QTextEdit, QVBoxLayout, QWidget


class BusinessListWidget(QWidget):
    """사업장 리스트 위젯"""

    # 시그널 정의
    business_list_changed = pyqtSignal(list)  # 사업장 리스트 변경

    def __init__(self, parent=None):
        super().__init__(parent)

        # 기본 사업장 리스트
        self.default_biz_list = ["1051707"]

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 그룹박스로 묶기
        group_box = QGroupBox("사업장 리스트")
        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(10)

        # 설명 라벨
        self.label = QLabel("사업장 번호:")
        group_layout.addWidget(self.label)

        # 텍스트 입력 영역
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("사업장 번호를 한 줄에 하나씩 입력하세요")
        self.text_edit.setMaximumHeight(120)

        # 기본값 설정
        default_text = "\n".join(self.default_biz_list)
        self.text_edit.setPlainText(default_text)

        group_layout.addWidget(self.text_edit)

        layout.addWidget(group_box)
        layout.addStretch()

    def connect_signals(self):
        """시그널 연결"""
        self.text_edit.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        """텍스트 변경 시 호출"""
        business_list = self.get_business_list()
        self.business_list_changed.emit(business_list)

    def get_business_list(self) -> list:
        """입력된 사업장 리스트 반환"""
        text = self.text_edit.toPlainText().strip()
        if not text:
            return []

        # 줄 단위로 분리하고 공백 제거
        lines = [line.strip() for line in text.split("\n")]
        # 빈 줄 제거
        business_list = [line for line in lines if line]

        return business_list

    def set_business_list(self, business_list: list):
        """사업장 리스트 설정"""
        text = "\n".join(business_list)
        self.text_edit.setPlainText(text)
