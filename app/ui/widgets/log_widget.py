"""
로그 위젯 - 애플리케이션 로그를 표시하는 위젯
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QGroupBox,
)
from PySide6.QtGui import QFont, QTextCursor


class LogWidget(QWidget):
    """로그 표시 위젯"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # 로그 그룹 박스
        self.log_group = QGroupBox("실행 로그")
        log_layout = QVBoxLayout(self.log_group)
        log_layout.setContentsMargins(10, 30, 10, 10)
        log_layout.setSpacing(5)

        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("맑은 고딕", 14))
        self.log_text.setMinimumHeight(200)

        # 로그 컨트롤 버튼들
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(10)

        self.clear_button = QPushButton("로그 지우기")
        self.copy_button = QPushButton("로그 복사")

        # 버튼 스타일 클래스 설정
        self.clear_button.setProperty("class", "secondary")
        self.copy_button.setProperty("class", "secondary")

        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addStretch()

        # 레이아웃 구성
        log_layout.addWidget(self.log_text)
        log_layout.addLayout(button_layout)

        layout.addWidget(self.log_group)

        # 시그널 연결
        self.clear_button.clicked.connect(self.clear_logs)
        self.copy_button.clicked.connect(self.copy_logs)

    def apply_styles(self):
        """스타일 적용"""
        # 로그 텍스트 영역 스타일
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 14pt;
                selection-background-color: #007bff;
            }
        """)

        # 그룹 박스 스타일
        self.log_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14pt;
                color: #495057;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f8f9fa;
            }
        """)

        # 버튼 스타일 (기본 스타일시트를 따르도록 설정)
        self.clear_button.setStyleSheet("")
        self.copy_button.setStyleSheet("")

    def add_log_message(self, level: str, message: str, timestamp: str):
        """로그 메시지 추가"""
        # 로그 레벨에 따른 색상 설정
        color_map = {
            "INFO": "#17a2b8",  # 청록색
            "WARNING": "#ffc107",  # 노란색
            "ERROR": "#dc3545",  # 빨간색
            "SUCCESS": "#28a745",  # 녹색
        }

        color = color_map.get(level, "#6c757d")  # 기본 회색

        # HTML 형식으로 로그 메시지 추가
        formatted_message = (
            f'<span style="color: {color};">[{level}]</span> '
            f'<span style="color: #6c757d;">{timestamp}</span> '
            f"<span>{message}</span>"
        )

        self.log_text.append(formatted_message)

        # 항상 최신 로그가 보이도록 스크롤
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def clear_logs(self):
        """로그 지우기"""
        self.log_text.clear()

    def copy_logs(self):
        """로그 복사"""
        clipboard = self.log_text.textCursor()
        clipboard.select(QTextCursor.Document)
        self.log_text.copy()
