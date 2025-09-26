"""
결과 위젯 - 실행 결과 및 로그 표시
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QPushButton,
    QFrame,
    QGridLayout,
    QHeaderView,
    QAbstractItemView,
    QFileDialog,
    QMessageBox,
)
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtGui import QFont, QColor
from datetime import datetime


class ResultsWidget(QWidget):
    """실행 결과 위젯"""

    # 시그널 정의
    export_requested = pyqtSignal(str)  # 내보내기 형식
    retry_requested = pyqtSignal(list)  # 재시도할 항목들

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results_data = []
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 결과 그룹 헤더
        header_layout = QHBoxLayout()

        header_label = QLabel("실행 결과")
        header_label.setFont(QFont("맑은 고딕", 12, QFont.Weight.Bold))
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # 내보내기 버튼들
        self.export_csv_btn = QPushButton("CSV 내보내기")
        self.export_json_btn = QPushButton("JSON 내보내기")
        self.clear_btn = QPushButton("결과 지우기")

        header_layout.addWidget(self.export_csv_btn)
        header_layout.addWidget(self.export_json_btn)
        header_layout.addWidget(self.clear_btn)

        layout.addLayout(header_layout)

        # 요약 통계 영역
        self.create_summary_section(layout)

        # 탭 위젯으로 결과 구분
        self.tab_widget = QTabWidget()

        # 결과 테이블 탭
        self.create_results_table_tab()

        # 로그 표시 탭
        self.create_log_tab()

        # 오류 상세 탭
        self.create_error_tab()

        layout.addWidget(self.tab_widget, 1)

    def create_summary_section(self, parent_layout):
        """요약 통계 섹션 생성"""
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_frame.setMaximumHeight(80)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
        """)

        summary_layout = QGridLayout(summary_frame)
        summary_layout.setContentsMargins(15, 10, 15, 10)

        # 통계 라벨들
        self.total_label = QLabel("총 처리: 0건")
        self.total_label.setFont(QFont("맑은 고딕", 10, QFont.Weight.Bold))

        self.success_label = QLabel("성공: 0건")
        self.success_label.setStyleSheet("color: #28a745; font-weight: bold;")

        self.failed_label = QLabel("실패: 0건")
        self.failed_label.setStyleSheet("color: #dc3545; font-weight: bold;")

        self.skipped_label = QLabel("건너뜀: 0건")
        self.skipped_label.setStyleSheet("color: #ffc107; font-weight: bold;")

        self.success_rate_label = QLabel("성공률: 0%")
        self.success_rate_label.setFont(QFont("맑은 고딕", 10, QFont.Weight.Bold))

        self.last_run_label = QLabel("마지막 실행: -")
        self.last_run_label.setStyleSheet("color: #6c757d; font-size: 9pt;")

        # 레이아웃에 배치
        summary_layout.addWidget(self.total_label, 0, 0)
        summary_layout.addWidget(self.success_label, 0, 1)
        summary_layout.addWidget(self.failed_label, 0, 2)
        summary_layout.addWidget(self.skipped_label, 0, 3)
        summary_layout.addWidget(self.success_rate_label, 1, 0)
        summary_layout.addWidget(self.last_run_label, 1, 1, 1, 3)

        parent_layout.addWidget(summary_frame)

    def create_results_table_tab(self):
        """결과 테이블 탭 생성"""
        results_widget = QWidget()
        layout = QVBoxLayout(results_widget)

        # 테이블 위젯
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels(
            [
                "시간",
                "매장명",
                "리뷰내용",
                "생성된 답글",
                "상태",
                "오류",
                "소요시간",
                "재시도",
            ]
        )

        # 테이블 설정
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 시간
        header.setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )  # 매장명
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 리뷰내용
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 답글
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # 상태
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # 오류
        header.setSectionResizeMode(
            6, QHeaderView.ResizeMode.ResizeToContents
        )  # 소요시간
        header.setSectionResizeMode(
            7, QHeaderView.ResizeMode.ResizeToContents
        )  # 재시도

        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.results_table.setSortingEnabled(True)

        layout.addWidget(self.results_table)

        # 테이블 하단 컨트롤
        table_controls = QHBoxLayout()

        self.retry_selected_btn = QPushButton("선택한 항목 재시도")
        self.retry_failed_btn = QPushButton("실패한 항목 모두 재시도")
        self.delete_selected_btn = QPushButton("선택한 항목 삭제")

        table_controls.addWidget(self.retry_selected_btn)
        table_controls.addWidget(self.retry_failed_btn)
        table_controls.addStretch()
        table_controls.addWidget(self.delete_selected_btn)

        layout.addLayout(table_controls)

        self.tab_widget.addTab(results_widget, "처리 결과")

    def create_log_tab(self):
        """로그 탭 생성"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)

        # 로그 필터 컨트롤
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("로그 레벨:"))

        self.log_level_combo = QPushButton("전체")
        self.log_level_combo.setMaximumWidth(100)

        filter_layout.addWidget(self.log_level_combo)
        filter_layout.addStretch()

        self.clear_log_btn = QPushButton("로그 지우기")
        self.save_log_btn = QPushButton("로그 저장")

        filter_layout.addWidget(self.clear_log_btn)
        filter_layout.addWidget(self.save_log_btn)

        layout.addLayout(filter_layout)

        # 로그 텍스트 영역
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """)

        layout.addWidget(self.log_text)

        self.tab_widget.addTab(log_widget, "실행 로그")

    def create_error_tab(self):
        """오류 상세 탭 생성"""
        error_widget = QWidget()
        layout = QVBoxLayout(error_widget)

        # 오류 테이블
        self.error_table = QTableWidget()
        self.error_table.setColumnCount(5)
        self.error_table.setHorizontalHeaderLabels(
            ["시간", "오류 유형", "오류 메시지", "상세 정보", "해결방법"]
        )

        # 오류 테이블 설정
        error_header = self.error_table.horizontalHeader()
        error_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        error_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        error_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        error_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        error_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.error_table.setAlternatingRowColors(True)

        layout.addWidget(self.error_table)

        # 오류 통계
        error_stats_frame = QFrame()
        error_stats_frame.setMaximumHeight(60)
        error_stats_frame.setStyleSheet(
            "background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px;"
        )

        error_stats_layout = QHBoxLayout(error_stats_frame)

        self.error_stats_label = QLabel(
            "오류 통계: 로그인 오류 0건, DOM 오류 0건, LLM 오류 0건, 네트워크 오류 0건"
        )
        error_stats_layout.addWidget(self.error_stats_label)

        layout.addWidget(error_stats_frame)

        self.tab_widget.addTab(error_widget, "오류 분석")

    def connect_signals(self):
        """시그널 연결"""
        self.export_csv_btn.clicked.connect(lambda: self.export_data("csv"))
        self.export_json_btn.clicked.connect(lambda: self.export_data("json"))
        self.clear_btn.clicked.connect(self.clear_results)
        self.retry_selected_btn.clicked.connect(self.retry_selected_items)
        self.retry_failed_btn.clicked.connect(self.retry_failed_items)
        self.delete_selected_btn.clicked.connect(self.delete_selected_items)
        self.clear_log_btn.clicked.connect(self.clear_log)
        self.save_log_btn.clicked.connect(self.save_log)

    def add_result(self, result_data: dict):
        """결과 추가"""
        self.results_data.append(result_data)

        # 테이블에 행 추가
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        # 데이터 설정
        timestamp = result_data.get("timestamp", datetime.now().strftime("%H:%M:%S"))
        store_name = result_data.get("store_name", "")
        review_text = (
            result_data.get("review_text", "")[:100] + "..."
            if len(result_data.get("review_text", "")) > 100
            else result_data.get("review_text", "")
        )
        reply_text = (
            result_data.get("reply_text", "")[:100] + "..."
            if len(result_data.get("reply_text", "")) > 100
            else result_data.get("reply_text", "")
        )
        status = result_data.get("status", "")
        error = result_data.get("error", "")
        duration = result_data.get("duration", "")

        self.results_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.results_table.setItem(row, 1, QTableWidgetItem(store_name))
        self.results_table.setItem(row, 2, QTableWidgetItem(review_text))
        self.results_table.setItem(row, 3, QTableWidgetItem(reply_text))

        # 상태에 따른 색상 설정
        status_item = QTableWidgetItem(status)
        if status == "성공":
            status_item.setBackground(QColor("#d4edda"))
            status_item.setForeground(QColor("#155724"))
        elif status == "실패":
            status_item.setBackground(QColor("#f8d7da"))
            status_item.setForeground(QColor("#721c24"))
        elif status == "건너뜀":
            status_item.setBackground(QColor("#fff3cd"))
            status_item.setForeground(QColor("#856404"))

        self.results_table.setItem(row, 4, status_item)
        self.results_table.setItem(row, 5, QTableWidgetItem(error))
        self.results_table.setItem(row, 6, QTableWidgetItem(duration))

        # 재시도 버튼
        if status == "실패":
            retry_btn = QPushButton("재시도")
            retry_btn.setMaximumSize(60, 25)
            retry_btn.clicked.connect(lambda checked, r=row: self.retry_single_item(r))
            self.results_table.setCellWidget(row, 7, retry_btn)

        # 통계 업데이트
        self.update_statistics()

    def add_log_message(self, level: str, message: str, timestamp: str = None):
        """로그 메시지 추가"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 레벨에 따른 색상 설정
        color_map = {
            "INFO": "#00ff00",
            "WARN": "#ffff00",
            "ERROR": "#ff0000",
            "DEBUG": "#888888",
        }

        color = color_map.get(level, "#ffffff")
        formatted_message = (
            f'<span style="color: {color};">[{timestamp}] [{level}] {message}</span>'
        )

        self.log_text.append(formatted_message)

        # 스크롤을 맨 아래로
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)

    def add_error(
        self, error_type: str, error_message: str, details: str = "", solution: str = ""
    ):
        """오류 추가"""
        row = self.error_table.rowCount()
        self.error_table.insertRow(row)

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.error_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.error_table.setItem(row, 1, QTableWidgetItem(error_type))
        self.error_table.setItem(row, 2, QTableWidgetItem(error_message))
        self.error_table.setItem(row, 3, QTableWidgetItem(details))
        self.error_table.setItem(row, 4, QTableWidgetItem(solution))

    def update_statistics(self):
        """통계 업데이트"""
        total = len(self.results_data)
        success = len([r for r in self.results_data if r.get("status") == "성공"])
        failed = len([r for r in self.results_data if r.get("status") == "실패"])
        skipped = len([r for r in self.results_data if r.get("status") == "건너뜀"])

        success_rate = int((success / total * 100)) if total > 0 else 0

        self.total_label.setText(f"총 처리: {total}건")
        self.success_label.setText(f"성공: {success}건")
        self.failed_label.setText(f"실패: {failed}건")
        self.skipped_label.setText(f"건너뜀: {skipped}건")
        self.success_rate_label.setText(f"성공률: {success_rate}%")
        self.last_run_label.setText(
            f"마지막 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    def export_data(self, format_type: str):
        """데이터 내보내기"""
        if not self.results_data:
            QMessageBox.information(self, "알림", "내보낼 데이터가 없습니다.")
            return

        file_filter = (
            "CSV 파일 (*.csv)" if format_type == "csv" else "JSON 파일 (*.json)"
        )
        file_path, _ = QFileDialog.getSaveFileName(
            self, "결과 내보내기", "", file_filter
        )

        if file_path:
            self.export_requested.emit(format_type)
            # 실제 내보내기는 향후 구현
            QMessageBox.information(
                self, "알림", f"{format_type.upper()} 파일로 내보내기 완료"
            )

    def clear_results(self):
        """결과 지우기"""
        reply = QMessageBox.question(
            self,
            "확인",
            "모든 결과를 지우시겠습니까?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.results_data.clear()
            self.results_table.setRowCount(0)
            self.error_table.setRowCount(0)
            self.update_statistics()

    def retry_selected_items(self):
        """선택한 항목 재시도"""
        selected_rows = []
        for item in self.results_table.selectedItems():
            if item.row() not in selected_rows:
                selected_rows.append(item.row())

        if selected_rows:
            selected_data = [self.results_data[row] for row in selected_rows]
            self.retry_requested.emit(selected_data)

    def retry_failed_items(self):
        """실패한 항목 모두 재시도"""
        failed_data = [r for r in self.results_data if r.get("status") == "실패"]
        if failed_data:
            self.retry_requested.emit(failed_data)
        else:
            QMessageBox.information(self, "알림", "재시도할 실패한 항목이 없습니다.")

    def retry_single_item(self, row: int):
        """단일 항목 재시도"""
        if row < len(self.results_data):
            self.retry_requested.emit([self.results_data[row]])

    def delete_selected_items(self):
        """선택한 항목 삭제"""
        selected_rows = []
        for item in self.results_table.selectedItems():
            if item.row() not in selected_rows:
                selected_rows.append(item.row())

        if selected_rows:
            # 역순으로 삭제 (인덱스 변경 문제 방지)
            for row in sorted(selected_rows, reverse=True):
                self.results_table.removeRow(row)
                if row < len(self.results_data):
                    del self.results_data[row]

            self.update_statistics()

    def clear_log(self):
        """로그 지우기"""
        self.log_text.clear()

    def save_log(self):
        """로그 저장"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "로그 저장", "", "텍스트 파일 (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, "알림", "로그가 저장되었습니다.")
            except Exception as e:
                QMessageBox.critical(
                    self, "오류", f"로그 저장 중 오류가 발생했습니다: {str(e)}"
                )

    def get_results_data(self) -> list:
        """결과 데이터 반환"""
        return self.results_data.copy()
