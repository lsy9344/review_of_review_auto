"""
개발 모드 데모용 파일 - 이 파일을 수정하면 프로그램이 재시작됩니다
"""

from datetime import datetime

def demo_function():
    """데모 함수"""
    print(f"📅 현재 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 이 파일을 수정하면 프로그램이 자동으로 재시작됩니다!")
    print("✏️  이 메시지를 변경해보세요!")
    
    # 이 값을 변경해보세요!
    demo_value = "Hello, Development Mode!"
    print(f"💬 메시지: {demo_value}")
    
    return True

if __name__ == "__main__":
    demo_function()
