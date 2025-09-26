"""
실행 스크립트 - 네이버 스마트플레이스 리뷰 자동응답 시스템 실행
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 메인 애플리케이션 실행
from app.main import main

if __name__ == "__main__":
    sys.exit(main())
