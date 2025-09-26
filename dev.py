#!/usr/bin/env python3
"""
개발 모드 실행 스크립트 - 파일 변경 시 자동 재시작
"""

import sys
import os
import argparse

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.utils.dev_watcher import DevWatcher
except ImportError as e:
    print(f"❌ 개발 도구를 불러올 수 없습니다: {e}")
    print("💡 다음 명령어로 의존성을 설치해주세요:")
    print("   pip install watchdog")
    sys.exit(1)


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="네이버 스마트플레이스 리뷰 자동응답 - 개발 모드",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python dev.py                    # 기본 개발 모드 실행
  python dev.py --watch app tests  # app과 tests 디렉토리 감시
  python dev.py --no-ui           # UI 없이 백엔드만 테스트
  python dev.py --command "python -m pytest"  # 커스텀 명령어 실행

파일 변경 감지 시 자동으로 프로그램이 재시작됩니다.
중지하려면 Ctrl+C를 눌러주세요.
        """,
    )

    parser.add_argument(
        "--watch", nargs="+", default=["app"], help="감시할 디렉토리 목록 (기본값: app)"
    )

    parser.add_argument(
        "--command", default=None, help="실행할 명령어 (기본값: python run.py)"
    )

    parser.add_argument(
        "--no-ui", action="store_true", help="UI 없이 백엔드만 실행 (향후 구현)"
    )

    parser.add_argument("--verbose", action="store_true", help="상세 로그 출력")

    args = parser.parse_args()

    # 감시할 디렉토리 확인
    watch_dirs = []
    for watch_dir in args.watch:
        if os.path.exists(watch_dir):
            watch_dirs.append(watch_dir)
        else:
            print(f"⚠️  디렉토리가 존재하지 않습니다: {watch_dir}")

    if not watch_dirs:
        print("❌ 감시할 디렉토리가 없습니다.")
        sys.exit(1)

    # 실행 명령어 설정
    if args.command:
        restart_command = args.command.split()
    elif args.no_ui:
        # 향후 백엔드 전용 모드 구현 시 사용
        restart_command = [
            sys.executable,
            "-c",
            'print("백엔드 모드는 향후 구현 예정")',
        ]
    else:
        restart_command = [sys.executable, "run.py"]

    # 개발 모드 실행
    try:
        watcher = DevWatcher(watch_dirs=watch_dirs, restart_command=restart_command)

        if args.verbose:
            import logging

            logging.getLogger().setLevel(logging.DEBUG)

        watcher.run_dev_mode()

    except KeyboardInterrupt:
        print("\n👋 개발 모드를 종료합니다.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 개발 모드 실행 중 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
