"""
결과 표시창 위젯
"""

from PySide6.QtWidgets import (
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QDialog,
)
from PySide6.QtCore import Qt

from app.services.review_crawler import CrawlResult


class ResultsWindow(QDialog):
    """수집된 리뷰 결과를 테이블 형태로 보여주는 별도의 창"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("리뷰 수집 결과")
        self.setMinimumSize(800, 600)
        self.init_ui()

    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["작성자", "별점", "리뷰 내용", "생성된 답변", "작성일"]
        )
        self.table_widget.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )  # 편집 불가
        self.table_widget.setAlternatingRowColors(True)

        # 폰트 크기 1.5배 조절
        font = self.table_widget.font()
        font.setPointSize(int(font.pointSize() * 1.5))
        self.table_widget.setFont(font)

        # 행 높이도 조정
        self.table_widget.verticalHeader().setDefaultSectionSize(50)

        # 컬럼 너비 설정
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)  # 작성자
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # 별점
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 리뷰 내용
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 생성된 답변
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Interactive)  # 작성일

        # 컬럼 너비 조정 - 별점은 기존 너비의 1.5배
        self.table_widget.setColumnWidth(1, 90)

        layout.addWidget(self.table_widget)

    def populate_data(self, crawl_result: CrawlResult):
        """테이블에 리뷰 데이터를 채웁니다."""
        self.table_widget.setRowCount(0)  # 기존 데이터 초기화

        # 모든 매장의 리뷰와 생성된 답변을 수집
        all_data = []
        for store_result in crawl_result.stores:
            if store_result.reviews:
                # 생성된 답변이 있는지 확인
                reply_dict = {}
                if hasattr(store_result, "generated_replies"):
                    for reply_pair in store_result.generated_replies:
                        reply_dict[reply_pair.review_id] = reply_pair.generated_reply

                for review in store_result.reviews:
                    review_id = review.get("id", "")
                    generated_reply = reply_dict.get(review_id, "")

                    all_data.append(
                        {"review": review, "generated_reply": generated_reply}
                    )

        self.table_widget.setRowCount(len(all_data))

        for row, data in enumerate(all_data):
            review = data["review"]
            generated_reply = data["generated_reply"]

            author = review.get("author", {}).get("displayName", "알 수 없음")
            rating = review.get("rating", 0)
            content = review.get("content", {}).get("text", "")
            created_date = review.get("createdDateTime", "").split("T")[0]

            # 테이블 아이템 생성 및 검정색 폰트 설정
            author_item = QTableWidgetItem(author)
            author_item.setForeground(Qt.GlobalColor.black)
            self.table_widget.setItem(row, 0, author_item)

            rating_item = QTableWidgetItem(str(rating))
            rating_item.setForeground(Qt.GlobalColor.black)
            self.table_widget.setItem(row, 1, rating_item)

            content_item = QTableWidgetItem(content)
            content_item.setForeground(Qt.GlobalColor.black)
            self.table_widget.setItem(row, 2, content_item)

            reply_item = QTableWidgetItem(generated_reply or "답변 없음")
            reply_item.setForeground(Qt.GlobalColor.black)
            self.table_widget.setItem(row, 3, reply_item)

            date_item = QTableWidgetItem(created_date)
            date_item.setForeground(Qt.GlobalColor.black)
            self.table_widget.setItem(row, 4, date_item)

        # 행 높이를 1.5배로 조정
        for row in range(self.table_widget.rowCount()):
            self.table_widget.setRowHeight(row, 75)  # 기존 50의 1.5배

        self.table_widget.resizeRowsToContents()
