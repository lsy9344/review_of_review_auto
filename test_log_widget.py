"""
로그 위젯 테스트 코드
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ui.main_window import MainWindow


def test_log_widget():
    """로그 위젯 테스트"""
    app = QApplication(sys.argv)
    
    # 메인 윈도우 생성
    window = MainWindow()
    window.show()
    
    # 테스트 로그 추가
    def add_test_logs():
        viewmodel = window.viewmodel
        viewmodel.add_log("INFO", "애플리케이션 시작")
        viewmodel.add_log("SUCCESS", "로그인 성공")
        viewmodel.add_log("WARNING", "설정 파일이 없습니다. 기본 설정을 사용합니다.")
        viewmodel.add_log("ERROR", "네트워크 연결 실패")
        viewmodel.add_log("INFO", "재시도 중... (1/3)")
        viewmodel.add_log("INFO", "재시도 중... (2/3)")
        viewmodel.add_log("SUCCESS", "연결 성공")
        
    # 1초 후에 테스트 로그 추가
    QTimer.singleShot(1000, add_test_logs)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_log_widget()