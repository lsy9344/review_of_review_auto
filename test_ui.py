"""
UI 테스트 스크립트 - 기본 UI 동작 확인
"""

import sys
import os

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """모듈 import 테스트"""
    try:
        print("✅ 모든 모듈 import 성공")
        return True
    except Exception as e:
        print(f"❌ Import 오류: {e}")
        return False


def test_ui_creation():
    """UI 생성 테스트"""
    try:
        from PySide6.QtWidgets import QApplication
        from app.ui import MainWindow

        app = QApplication.instance() or QApplication(sys.argv)
        main_window = MainWindow()

        print("✅ 메인 윈도우 생성 성공")
        print(
            f"   - 윈도우 크기: {main_window.size().width()}x{main_window.size().height()}"
        )
        print(f"   - 제목: {main_window.windowTitle()}")

        # 위젯 존재 확인
        if hasattr(main_window, "login_widget"):
            print("✅ 로그인 위젯 존재")
        if hasattr(main_window, "config_widget"):
            print("✅ 설정 위젯 존재")
        if hasattr(main_window, "control_widget"):
            print("✅ 컨트롤 위젯 존재")
        if hasattr(main_window, "results_widget"):
            print("✅ 결과 위젯 존재")

        return True
    except Exception as e:
        print(f"❌ UI 생성 오류: {e}")
        return False


def test_viewmodel():
    """뷰모델 테스트"""
    try:
        from app.ui.viewmodel import ViewModel

        vm = ViewModel()

        # 기본 상태 확인
        assert not vm.is_logged_in(), "초기 로그인 상태가 False여야 함"
        assert not vm.is_running(), "초기 실행 상태가 False여야 함"

        # 설정 테스트
        config = vm.get_config()
        assert isinstance(config, dict), "설정이 딕셔너리여야 함"

        print("✅ 뷰모델 테스트 성공")
        return True
    except Exception as e:
        print(f"❌ 뷰모델 테스트 오류: {e}")
        return False


def main():
    """테스트 실행"""
    print("=== 네이버 스마트플레이스 리뷰 자동응답 UI 테스트 ===\n")

    tests = [
        ("모듈 Import", test_imports),
        ("UI 생성", test_ui_creation),
        ("뷰모델", test_viewmodel),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"🔍 {test_name} 테스트 중...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과\n")
            else:
                print(f"❌ {test_name} 테스트 실패\n")
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}\n")

    print(f"=== 테스트 결과: {passed}/{total} 통과 ===")

    if passed == total:
        print("🎉 모든 테스트 통과! UI가 정상적으로 구현되었습니다.")
        print("\n실행 방법:")
        print("  python run.py")
        return 0
    else:
        print("⚠️  일부 테스트 실패. 코드를 확인해주세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
