"""
컨트롤 위젯 - 간단한 실행/정지 버튼
"""

from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QPushButton, QWidget


class ControlWidget(QWidget):
    """실행 컨트롤 위젯"""

    # 시그널 정의
    start_requested = pyqtSignal()  # 실행 시작
    stop_requested = pyqtSignal()  # 실행 정지
    view_results_requested = pyqtSignal()  # 결과 보기
    generate_replies_requested = pyqtSignal()  # 답변만 생성

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_running = False
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """UI 초기화"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 실행 버튼
        self.start_button = QPushButton("실행")
        self.start_button.setMinimumSize(100, 50)
        self.start_button.setFont(QFont("맑은 고딕", 12, QFont.Weight.Bold))

        # 정지 버튼
        self.stop_button = QPushButton("정지")
        self.stop_button.setMinimumSize(100, 50)
        self.stop_button.setFont(QFont("맑은 고딕", 12, QFont.Weight.Bold))
        self.stop_button.setEnabled(False)

        # 답변 생성 버튼
        self.generate_replies_button = QPushButton("답변만 생성")
        self.generate_replies_button.setMinimumSize(120, 50)
        self.generate_replies_button.setFont(QFont("맑은 고딕", 10, QFont.Weight.Bold))
        self.generate_replies_button.setEnabled(False)  # 결과가 있을 때만 활성화

        # 결과 보기 버튼
        self.view_results_button = QPushButton("결과 보기")
        self.view_results_button.setMinimumSize(100, 50)
        self.view_results_button.setFont(QFont("맑은 고딕", 12, QFont.Weight.Bold))
        self.view_results_button.setEnabled(False)  # 기본적으로 비활성화

        # 자동 제출 체크박스
        self.auto_submit_checkbox = QCheckBox("답변 자동 제출")
        self.auto_submit_checkbox.setFont(QFont("맑은 고딕", 18))
        self.auto_submit_checkbox.setStyleSheet("color: black;")

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.generate_replies_button)
        layout.addWidget(self.view_results_button)
        layout.addWidget(self.auto_submit_checkbox)
        layout.addStretch()

    def connect_signals(self):
        """시그널 연결"""
        self.start_button.clicked.connect(self.on_start_clicked)
        self.stop_button.clicked.connect(self.on_stop_clicked)
        self.generate_replies_button.clicked.connect(
            self.generate_replies_requested.emit
        )
        self.view_results_button.clicked.connect(self.view_results_requested.emit)

    def is_auto_submit_enabled(self) -> bool:
        """자동 제출 체크박스 상태 반환"""
        return self.auto_submit_checkbox.isChecked()

    def on_start_clicked(self):
        """실행 버튼 클릭"""
        self.is_running = True
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.generate_replies_button.setEnabled(False)  # 실행 중에는 비활성화
        self.view_results_button.setEnabled(False)  # 실행 중에는 비활성화
        self.start_requested.emit()

    def on_stop_clicked(self):
        """정지 버튼 클릭"""
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.stop_requested.emit()

    def update_status(self, message: str):
        """현재 작업 상태 업데이트 (호환성을 위해 유지)"""
        pass

    def update_progress(self, current: int, total: int):
        """진행률 업데이트 (호환성을 위해 유지)"""
        pass

    def update_counts(self, processed: int, success: int, failed: int):
        """처리 건수 업데이트 (호환성을 위해 유지)"""
        pass

    def execution_completed(self, success_count: int, failed_count: int):
        """실행 완료 처리"""
        self.is_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        if success_count > 0:
            self.generate_replies_button.setEnabled(
                True
            )  # 리뷰가 있으면 답변 생성 가능
            self.view_results_button.setEnabled(True)
