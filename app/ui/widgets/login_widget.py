"""
로그인 위젯 - 네이버 계정 로그인 및 인증 상태 관리
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QGroupBox,
    QGridLayout,
)
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtGui import QFont


class LoginWidget(QWidget):
    """네이버 로그인 위젯"""

    # 시그널 정의
    login_requested = pyqtSignal(str, str)  # 아이디, 비밀번호
    test_login_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 그룹박스로 묶기
        group_box = QGroupBox("네이버 로그인 정보")
        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(10)

        # 로그인 폼
        form_layout = QGridLayout()
        form_layout.setColumnStretch(1, 1)

        # 아이디 입력
        self.id_label = QLabel("네이버 아이디:")
        self.id_input = QLineEdit()
        self.id_input.setText("dltnduf4318")
        self.id_input.setPlaceholderText("네이버 아이디를 입력하세요")
        self.id_input.setMaxLength(50)

        form_layout.addWidget(self.id_label, 0, 0)
        form_layout.addWidget(self.id_input, 0, 1)

        # 비밀번호 입력
        self.pw_label = QLabel("네이버 비밀번호:")
        self.pw_input = QLineEdit()
        self.pw_input.setText("Doolim01!@")
        self.pw_input.setPlaceholderText("비밀번호를 입력하세요")
        self.pw_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pw_input.setMaxLength(100)

        form_layout.addWidget(self.pw_label, 1, 0)
        form_layout.addWidget(self.pw_input, 1, 1)

        group_layout.addLayout(form_layout)

        # 버튼 영역
        button_layout = QHBoxLayout()

        self.test_button = QPushButton("로그인 테스트")
        self.test_button.setMinimumHeight(35)
        self.clear_button = QPushButton("지우기")
        self.clear_button.setMinimumHeight(35)

        button_layout.addWidget(self.test_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        group_layout.addLayout(button_layout)

        # 상태 표시 영역
        self.status_frame = QFrame()
        self.status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        self.status_frame.setMinimumHeight(60)

        status_layout = QVBoxLayout(self.status_frame)

        self.status_label = QLabel("상태: 로그인 필요")
        self.status_label.setFont(QFont("맑은 고딕", 9, QFont.Weight.Bold))

        self.status_detail = QLabel(
            "네이버 계정 정보를 입력하고 로그인 테스트를 진행하세요."
        )
        self.status_detail.setWordWrap(True)
        self.status_detail.setStyleSheet("color: #666; font-size: 14pt;")

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.status_detail)

        group_layout.addWidget(self.status_frame)

        layout.addWidget(group_box)
        layout.addStretch()

        # 초기 스타일 설정
        self.set_status(
            "ready",
            "로그인 필요",
            "네이버 계정 정보를 입력하고 로그인 테스트를 진행하세요.",
        )

    def connect_signals(self):
        """시그널 연결"""
        self.test_button.clicked.connect(self.on_test_login)
        self.clear_button.clicked.connect(self.clear_inputs)
        self.pw_input.returnPressed.connect(self.on_test_login)

    def on_test_login(self):
        """로그인 테스트 버튼 클릭"""
        user_id = self.id_input.text().strip()
        password = self.pw_input.text().strip()

        if not user_id or not password:
            self.set_status(
                "error", "입력 오류", "아이디와 비밀번호를 모두 입력해주세요."
            )
            return

        self.set_status(
            "testing", "로그인 테스트 중...", "네이버에 로그인을 시도하고 있습니다."
        )
        self.test_button.setEnabled(False)

        # 로그인 요청 시그널 발송
        self.login_requested.emit(user_id, password)

    def clear_inputs(self):
        """입력 필드 지우기"""
        self.id_input.clear()
        self.pw_input.clear()
        self.id_input.setFocus()
        self.set_status(
            "ready",
            "로그인 필요",
            "네이버 계정 정보를 입력하고 로그인 테스트를 진행하세요.",
        )

    def set_status(self, status_type: str, status_text: str, detail_text: str):
        """상태 표시 업데이트"""
        self.status_label.setText(f"상태: {status_text}")
        self.status_detail.setText(detail_text)

        # 상태에 따른 스타일 변경
        if status_type == "success":
            self.status_frame.setStyleSheet("""
                QFrame {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 4px;
                }
            """)
            self.status_label.setStyleSheet("color: #155724; font-weight: bold;")
        elif status_type == "error":
            self.status_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                }
            """)
            self.status_label.setStyleSheet("color: #721c24; font-weight: bold;")
        elif status_type == "testing":
            self.status_frame.setStyleSheet("""
                QFrame {
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 4px;
                }
            """)
            self.status_label.setStyleSheet("color: #856404; font-weight: bold;")
        else:  # ready
            self.status_frame.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                }
            """)
            self.status_label.setStyleSheet("color: #495057; font-weight: bold;")

    def login_success(self, message: str = "로그인 성공"):
        """로그인 성공 시 호출"""
        self.set_status("success", "로그인 성공", message)
        self.test_button.setEnabled(True)
        self.test_button.setText("다시 테스트")

    def login_failed(self, error_message: str):
        """로그인 실패 시 호출"""
        self.set_status("error", "로그인 실패", error_message)
        self.test_button.setEnabled(True)
        self.test_button.setText("다시 시도")

    def using_cookies(self, message: str = "저장된 쿠키 사용중"):
        """쿠키 사용 중일 때 호출"""
        self.set_status("success", "쿠키 사용중", message)
        self.test_button.setText("쿠키 갱신")

    def get_credentials(self) -> tuple:
        """입력된 계정 정보 반환"""
        return self.id_input.text().strip(), self.pw_input.text().strip()
