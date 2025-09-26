"""
개발 모드 기능 테스트 스크립트
"""

import sys
import os
import time
import subprocess

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dev_watcher_import():
    """DevWatcher 모듈 import 테스트"""
    try:
        from app.utils.dev_watcher import DevWatcher
        print("✅ DevWatcher 모듈 import 성공")
        return True
    except ImportError as e:
        print(f"❌ DevWatcher import 실패: {e}")
        return False

def test_dev_watcher_creation():
    """DevWatcher 인스턴스 생성 테스트"""
    try:
        from app.utils.dev_watcher import DevWatcher
        
        watcher = DevWatcher(
            watch_dirs=['app'],
            restart_command=[sys.executable, '--version']
        )
        
        print("✅ DevWatcher 인스턴스 생성 성공")
        print(f"   - 감시 디렉토리: {watcher.watch_dirs}")
        print(f"   - 재시작 명령어: {' '.join(watcher.restart_command)}")
        
        return True
    except Exception as e:
        print(f"❌ DevWatcher 생성 실패: {e}")
        return False

def test_file_change_detection():
    """파일 변경 감지 테스트"""
    try:
        from app.utils.dev_watcher import CodeChangeHandler
        
        restart_called = False
        
        def mock_restart():
            nonlocal restart_called
            restart_called = True
            print("🔄 재시작 콜백 호출됨")
        
        handler = CodeChangeHandler(mock_restart)
        
        # 가상 이벤트 생성
        class MockEvent:
            def __init__(self, src_path, is_directory=False):
                self.src_path = src_path
                self.is_directory = is_directory
        
        # Python 파일 변경 이벤트 시뮬레이션
        test_event = MockEvent("app/test.py")
        handler.on_modified(test_event)
        
        # 잠시 대기
        time.sleep(0.1)
        
        if restart_called:
            print("✅ 파일 변경 감지 및 재시작 콜백 테스트 성공")
            return True
        else:
            print("❌ 재시작 콜백이 호출되지 않음")
            return False
            
    except Exception as e:
        print(f"❌ 파일 변경 감지 테스트 실패: {e}")
        return False

def test_dev_script_help():
    """개발 스크립트 도움말 테스트"""
    try:
        result = subprocess.run(
            [sys.executable, 'dev.py', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and '개발 모드' in result.stdout:
            print("✅ 개발 스크립트 도움말 테스트 성공")
            return True
        else:
            print("❌ 개발 스크립트 도움말 테스트 실패")
            print(f"   Return code: {result.returncode}")
            print(f"   Stdout: {result.stdout[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ 개발 스크립트 테스트 실패: {e}")
        return False

def main():
    """테스트 실행"""
    print("=== 개발 모드 자동 재시작 기능 테스트 ===\n")
    
    tests = [
        ("DevWatcher 모듈 Import", test_dev_watcher_import),
        ("DevWatcher 인스턴스 생성", test_dev_watcher_creation),
        ("파일 변경 감지", test_file_change_detection),
        ("개발 스크립트 도움말", test_dev_script_help),
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
            print(f"❌ {test_name} 테스트 중 예외: {e}\n")
    
    print(f"=== 테스트 결과: {passed}/{total} 통과 ===")
    
    if passed == total:
        print("🎉 모든 테스트 통과! 개발 모드가 정상적으로 구현되었습니다.")
        print("\n사용 방법:")
        print("  python dev.py                 # 기본 개발 모드")
        print("  python dev.py --help          # 도움말 보기")
        print("  python dev.py --watch app ui  # 여러 디렉토리 감시")
        return 0
    else:
        print("⚠️  일부 테스트 실패. 코드를 확인해주세요.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
