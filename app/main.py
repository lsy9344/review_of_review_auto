"""
메인 애플리케이션 진입점 - 네이버 스마트플레이스 리뷰 자동응답 시스템
"""

import sys
import os
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QFont

from app.ui import MainWindow


def setup_logging():
    """로깅 설정"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def check_dependencies():
    """필수 의존성 확인"""
    required_modules = [
        'PySide6',
        'pathlib'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"다음 필수 모듈이 설치되지 않았습니다:\n{', '.join(missing_modules)}\n\n"
        error_msg += "pip install PySide6 명령어로 설치해주세요."
        
        # GUI가 가능하면 메시지박스로, 아니면 콘솔로
        try:
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "의존성 오류", error_msg)
        except:
            print(error_msg)
        
        return False
    
    return True


def check_environment():
    """환경 설정 확인"""
    warnings = []
    
    # OpenAI API 키 확인
    if not os.getenv('OPENAI_API_KEY'):
        warnings.append("환경변수 OPENAI_API_KEY가 설정되지 않았습니다.")
    
    # 작업 디렉토리 확인
    required_dirs = ['configs', 'logs', 'runs', '.auth']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            warnings.append(f"작업 디렉토리 '{dir_name}'을 생성했습니다.")
    
    return warnings


def create_splash_screen():
    """시작 화면 생성"""
    # 간단한 텍스트 기반 스플래시 스크린
    pixmap = QPixmap(400, 300)
    pixmap.fill(Qt.GlobalColor.white)
    
    splash = QSplashScreen(pixmap)
    splash.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.WindowStaysOnTopHint)
    
    # 메시지 표시
    splash.showMessage(
        "네이버 스마트플레이스 리뷰 자동응답 시스템\n시작 중...",
        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom,
        Qt.GlobalColor.black
    )
    
    return splash


def main():
    """메인 함수"""
    # 의존성 확인
    if not check_dependencies():
        sys.exit(1)
    
    # 로깅 설정
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # QApplication 생성
        app = QApplication(sys.argv)
        
        # 애플리케이션 정보 설정
        app.setApplicationName("네이버 스마트플레이스 리뷰 자동응답")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Review Reply Automation")
        
        # 한글 폰트 설정
        korean_font = QFont("맑은 고딕", 9)
        app.setFont(korean_font)
        
        # 스플래시 스크린 표시
        splash = create_splash_screen()
        splash.show()
        app.processEvents()
        
        logger.info("애플리케이션 시작")
        
        # 환경 설정 확인
        warnings = check_environment()
        if warnings:
            for warning in warnings:
                logger.warning(warning)
        
        # 메인 윈도우 생성
        splash.showMessage("메인 윈도우 초기화 중...", Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        app.processEvents()
        
        main_window = MainWindow()
        
        # 스플래시 스크린 종료 및 메인 윈도우 표시
        def show_main_window():
            splash.finish(main_window)
            main_window.show()
            
            # 환경 설정 경고가 있으면 표시
            if warnings:
                warning_msg = "다음 설정을 확인해주세요:\n\n" + "\n".join(warnings)
                warning_msg += "\n\n계속 진행하시겠습니까?"
                
                reply = QMessageBox.question(
                    main_window, 
                    "환경 설정 확인", 
                    warning_msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    main_window.close()
                    return
            
            logger.info("메인 윈도우 표시 완료")
        
        # 2초 후 메인 윈도우 표시
        QTimer.singleShot(2000, show_main_window)
        
        # 이벤트 루프 실행
        exit_code = app.exec()
        
        logger.info(f"애플리케이션 종료 (exit_code: {exit_code})")
        return exit_code
        
    except Exception as e:
        error_msg = f"애플리케이션 실행 중 오류가 발생했습니다:\n{str(e)}"
        logger.error(error_msg, exc_info=True)
        
        try:
            QMessageBox.critical(None, "시스템 오류", error_msg)
        except:
            print(error_msg)
        
        return 1


def console_main():
    """콘솔 모드 진입점 (향후 CLI 지원용)"""
    print("네이버 스마트플레이스 리뷰 자동응답 시스템")
    print("GUI 모드로 실행하려면 python -m app.main을 사용하세요.")
    print("콘솔 모드는 향후 지원 예정입니다.")


if __name__ == "__main__":
    # 직접 실행 시 GUI 모드
    sys.exit(main())
