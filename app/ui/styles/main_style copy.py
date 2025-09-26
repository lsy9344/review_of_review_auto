"""
메인 스타일시트 - 전체 애플리케이션에 적용되는 스타일
"""


def get_main_stylesheet() -> str:
    """메인 스타일시트 반환"""
    return """
        /* 기본 애플리케이션 스타일 */
        QMainWindow {
            background-color: #f8f9fa;
            color: #212529;
        }
        
        /* 그룹박스 스타일 */
        QGroupBox {
            font-weight: bold;
            font-size: 18pt;
            color: #495057;
            border: 2px solid #dee2e6;
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: #f8f9fa;
        }
        
        /* 라벨 스타일 */
        QLabel {
            color: #495057;
            font-size: 16pt;
        }
        
        /* 입력 필드 스타일 */
        QLineEdit {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 16pt;
            background-color: white;
            selection-background-color: #007bff;
        }
        
        QLineEdit:focus {
            border-color: #007bff;
            outline: none;
            box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        }
        
        QLineEdit:disabled {
            background-color: #e9ecef;
            color: #6c757d;
        }
        
        /* 텍스트 영역 스타일 */
        QTextEdit {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px;
            font-size: 16pt;
            background-color: white;
            selection-background-color: #007bff;
        }
        
        QTextEdit:focus {
            border-color: #007bff;
        }
        
        /* 콤보박스 스타일 */
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 16pt;
            background-color: white;
            min-width: 6em;
        }
        
        QComboBox:hover {
            border-color: #007bff;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #ced4da;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QComboBox::down-arrow {
            image: url(down_arrow.png);
            width: 12px;
            height: 12px;
        }
        
        QComboBox QAbstractItemView {
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
            selection-background-color: #007bff;
        }
        
        /* 스핀박스 스타일 */
        QSpinBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 16pt;
            background-color: white;
        }
        
        QSpinBox:focus {
            border-color: #007bff;
        }
        
        /* 버튼 기본 스타일 */
        QPushButton {
            border: 1px solid #007bff;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 16pt;
            font-weight: bold;
            background-color: #007bff;
            color: white;
            min-width: 80px;
        }
        
        QPushButton:hover {
            background-color: #0056b3;
            border-color: #0056b3;
        }
        
        QPushButton:pressed {
            background-color: #004085;
            border-color: #004085;
        }
        
        QPushButton:disabled {
            background-color: #6c757d;
            border-color: #6c757d;
            color: #dee2e6;
        }
        
        /* 성공 버튼 스타일 */
        QPushButton.success {
            background-color: #28a745;
            border-color: #28a745;
        }
        
        QPushButton.success:hover {
            background-color: #218838;
            border-color: #218838;
        }
        
        /* 위험 버튼 스타일 */
        QPushButton.danger {
            background-color: #dc3545;
            border-color: #dc3545;
        }
        
        QPushButton.danger:hover {
            background-color: #c82333;
            border-color: #c82333;
        }
        
        /* 경고 버튼 스타일 */
        QPushButton.warning {
            background-color: #ffc107;
            border-color: #ffc107;
            color: #212529;
        }
        
        QPushButton.warning:hover {
            background-color: #e0a800;
            border-color: #e0a800;
        }
        
        /* 보조 버튼 스타일 */
        QPushButton.secondary {
            background-color: #6c757d;
            border-color: #6c757d;
        }
        
        QPushButton.secondary:hover {
            background-color: #545b62;
            border-color: #545b62;
        }
        
        /* 진행률 바 스타일 */
        QProgressBar {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            text-align: center;
            font-weight: bold;
            font-size: 16pt;
            background-color: #f8f9fa;
        }
        
        QProgressBar::chunk {
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                             stop: 0 #007bff, stop: 1 #0056b3);
            border-radius: 3px;
        }
        
        /* 라디오 버튼 스타일 */
        QRadioButton {
            font-size: 16pt;
            color: #495057;
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 16px;
            height: 16px;
        }
        
        QRadioButton::indicator:unchecked {
            border: 2px solid #ced4da;
            border-radius: 8px;
            background-color: white;
        }
        
        QRadioButton::indicator:checked {
            border: 2px solid #007bff;
            border-radius: 8px;
            background-color: #007bff;
        }
        
        /* 테이블 스타일 */
        QTableWidget {
            gridline-color: #dee2e6;
            background-color: white;
            alternate-background-color: #f8f9fa;
            selection-background-color: #e3f2fd;
            border: 1px solid #dee2e6;
            border-radius: 4px;
        }
        
        QTableWidget::item {
            padding: 8px;
            border: none;
        }
        
        QTableWidget::item:selected {
            background-color: #e3f2fd;
            color: #1976d2;
        }
        
        QHeaderView::section {
            background-color: #e9ecef;
            color: #495057;
            padding: 8px;
            border: 1px solid #dee2e6;
            font-weight: bold;
            font-size: 16pt;
        }
        
        QHeaderView::section:hover {
            background-color: #f8f9fa;
        }
        
        /* 탭 위젯 스타일 */
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #f8f9fa;
            color: #495057;
            border: 1px solid #dee2e6;
            padding: 8px 16px;
            margin-right: 2px;
            font-size: 16pt;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            color: #007bff;
            border-bottom-color: white;
            font-weight: bold;
        }
        
        QTabBar::tab:hover {
            background-color: #e9ecef;
        }
        
        /* 스크롤바 스타일 */
        QScrollBar:vertical {
            background-color: #f8f9fa;
            width: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #ced4da;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #adb5bd;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #f8f9fa;
            height: 12px;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #ced4da;
            border-radius: 6px;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #adb5bd;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        /* 메뉴바 스타일 */
        QMenuBar {
            background-color: #ffffff;
            color: #495057;
            border-bottom: 1px solid #dee2e6;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 8px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #e9ecef;
        }
        
        QMenu {
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 4px;
        }
        
        QMenu::item {
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QMenu::item:selected {
            background-color: #e9ecef;
        }
        
        /* 상태바 스타일 */
        QStatusBar {
            background-color: #f8f9fa;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
            font-size: 14pt;
        }
        
        /* 프레임 스타일 */
        QFrame[frameShape="4"] {  /* StyledPanel */
            border: 1px solid #dee2e6;
            border-radius: 4px;
            background-color: white;
        }
        
        /* 툴팁 스타일 */
        QToolTip {
            background-color: #212529;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 14pt;
        }
    """


def get_dark_stylesheet() -> str:
    """다크 테마 스타일시트 반환"""
    return """
        /* 다크 테마 - 향후 확장용 */
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        
        QGroupBox {
            color: #ffffff;
            border: 2px solid #555555;
            background-color: #3c3c3c;
        }
        
        QLineEdit {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #007bff;
            border: 1px solid #007bff;
            color: white;
        }
        
        QTableWidget {
            background-color: #3c3c3c;
            color: #ffffff;
            gridline-color: #555555;
        }
    """
