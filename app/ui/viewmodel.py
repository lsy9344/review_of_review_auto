"""
뷰모델 - UI와 비즈니스 로직 간의 데이터 바인딩 계층
"""

from PySide6.QtCore import QObject, Signal as pyqtSignal
from datetime import datetime


class ViewModel(QObject):
    """메인 뷰모델 - UI 상태 관리 및 데이터 바인딩"""
    
    # UI 상태 시그널
    login_status_changed = pyqtSignal(str, str, str)  # status_type, status_text, detail_text
    execution_status_changed = pyqtSignal(str)  # 실행 상태
    progress_updated = pyqtSignal(int, int)  # current, total
    counts_updated = pyqtSignal(int, int, int)  # processed, success, failed
    result_added = pyqtSignal(dict)  # 결과 데이터
    log_message_added = pyqtSignal(str, str, str)  # level, message, timestamp
    config_updated = pyqtSignal(dict)  # 설정 변경
    
    def __init__(self):
        super().__init__()
        self.init_data()
    
    def init_data(self):
        """데이터 초기화"""
        # 로그인 상태
        self.login_state = {
            "is_logged_in": False,
            "user_id": "",
            "using_cookies": False,
            "last_login": None
        }
        
        # 실행 상태
        self.execution_state = {
            "is_running": False,
            "is_paused": False,
            "current_task": "대기 중...",
            "start_time": None,
            "progress": {"current": 0, "total": 0},
            "counts": {"processed": 0, "success": 0, "failed": 0}
        }
        
        # 설정
        self.config = {
            "prompt_template": "",
            "tone": "친절하고 정중한",
            "length_limit": 350,
            "banned_words": [],
            "mode": "assist",
            "max_reviews": 10,
            "llm_provider": "OpenAI",
            "llm_model": "gpt-4o-mini"
        }
        
        # 결과 데이터
        self.results = []
        self.logs = []
    
    # 로그인 관련 메서드
    def update_login_status(self, status_type: str, status_text: str, detail_text: str):
        """로그인 상태 업데이트"""
        self.login_state["is_logged_in"] = (status_type == "success")
        if status_type == "success":
            self.login_state["last_login"] = datetime.now()
        
        self.login_status_changed.emit(status_type, status_text, detail_text)
    
    def set_login_user(self, user_id: str, using_cookies: bool = False):
        """로그인 사용자 설정"""
        self.login_state["user_id"] = user_id
        self.login_state["using_cookies"] = using_cookies
        self.login_state["is_logged_in"] = True
    
    def logout(self):
        """로그아웃"""
        self.login_state["is_logged_in"] = False
        self.login_state["user_id"] = ""
        self.login_state["using_cookies"] = False
        self.update_login_status("ready", "로그인 필요", "네이버 계정 정보를 입력하고 로그인 테스트를 진행하세요.")
    
    # 실행 상태 관련 메서드
    def start_execution(self):
        """실행 시작"""
        self.execution_state["is_running"] = True
        self.execution_state["is_paused"] = False
        self.execution_state["start_time"] = datetime.now()
        self.execution_state["progress"] = {"current": 0, "total": 0}
        self.execution_state["counts"] = {"processed": 0, "success": 0, "failed": 0}
        
        self.update_execution_status("실행 시작...")
        self.add_log("INFO", "작업을 시작합니다.")
    
    def stop_execution(self):
        """실행 정지"""
        self.execution_state["is_running"] = False
        self.execution_state["is_paused"] = False
        
        self.update_execution_status("실행 정지됨")
        self.add_log("INFO", "작업이 정지되었습니다.")

    def complete_execution(self, message: str, level: str = "SUCCESS"):
        """실행 완료"""
        self.execution_state["is_running"] = False
        self.execution_state["is_paused"] = False
        self.execution_state["current_task"] = message
        self.execution_status_changed.emit(message)
        self.add_log(level, message)
    
    def pause_execution(self):
        """실행 일시정지"""
        self.execution_state["is_paused"] = True
        self.update_execution_status("일시정지됨")
        self.add_log("INFO", "작업이 일시정지되었습니다.")
    
    def resume_execution(self):
        """실행 재개"""
        self.execution_state["is_paused"] = False
        self.update_execution_status("실행 재개됨")
        self.add_log("INFO", "작업을 재개합니다.")
    
    def update_execution_status(self, status: str):
        """실행 상태 업데이트"""
        self.execution_state["current_task"] = status
        self.execution_status_changed.emit(status)
    
    def update_progress(self, current: int, total: int):
        """진행률 업데이트"""
        self.execution_state["progress"]["current"] = current
        self.execution_state["progress"]["total"] = total
        self.progress_updated.emit(current, total)
    
    def update_counts(self, processed: int, success: int, failed: int):
        """처리 건수 업데이트"""
        counts = self.execution_state["counts"]
        counts["processed"] = processed
        counts["success"] = success
        counts["failed"] = failed
        self.counts_updated.emit(processed, success, failed)
    
    # 결과 관련 메서드
    def add_result(self, result_data: dict):
        """결과 추가"""
        # 타임스탬프 추가
        result_data["timestamp"] = datetime.now().strftime("%H:%M:%S")
        
        self.results.append(result_data)
        self.result_added.emit(result_data)
        
        # 통계 업데이트
        self._update_statistics()
    
    def clear_results(self):
        """결과 지우기"""
        self.results.clear()
        self._update_statistics()
    
    def _update_statistics(self):
        """통계 자동 업데이트"""
        total = len(self.results)
        success = len([r for r in self.results if r.get("status") == "성공"])
        failed = len([r for r in self.results if r.get("status") == "실패"])
        
        self.update_counts(total, success, failed)
    
    # 로그 관련 메서드
    def add_log(self, level: str, message: str, timestamp: str = None):
        """로그 메시지 추가"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = {
            "level": level,
            "message": message,
            "timestamp": timestamp
        }
        
        self.logs.append(log_entry)
        self.log_message_added.emit(level, message, timestamp)
    
    def clear_logs(self):
        """로그 지우기"""
        self.logs.clear()
    
    # 설정 관련 메서드
    def update_config(self, config_dict: dict):
        """설정 업데이트"""
        self.config.update(config_dict)
        self.config_updated.emit(self.config.copy())
        self.add_log("INFO", f"설정이 업데이트되었습니다: {list(config_dict.keys())}")
    
    def get_config(self) -> dict:
        """현재 설정 반환"""
        return self.config.copy()
    
    def reset_config(self):
        """설정 초기화"""
        self.init_data()
        self.config_updated.emit(self.config.copy())
        self.add_log("INFO", "설정이 초기화되었습니다.")
    
    # 상태 조회 메서드
    def is_logged_in(self) -> bool:
        """로그인 상태 확인"""
        return self.login_state["is_logged_in"]
    
    def is_running(self) -> bool:
        """실행 중 여부 확인"""
        return self.execution_state["is_running"]
    
    def is_paused(self) -> bool:
        """일시정지 여부 확인"""
        return self.execution_state["is_paused"]
    
    def get_execution_summary(self) -> dict:
        """실행 요약 정보 반환"""
        return {
            "is_running": self.is_running(),
            "is_paused": self.is_paused(),
            "current_task": self.execution_state["current_task"],
            "progress": self.execution_state["progress"].copy(),
            "counts": self.execution_state["counts"].copy(),
            "start_time": self.execution_state["start_time"]
        }
    
    def get_results_summary(self) -> dict:
        """결과 요약 정보 반환"""
        total = len(self.results)
        success = len([r for r in self.results if r.get("status") == "성공"])
        failed = len([r for r in self.results if r.get("status") == "실패"])
        skipped = len([r for r in self.results if r.get("status") == "건너뜀"])
        
        return {
            "total": total,
            "success": success,
            "failed": failed,
            "skipped": skipped,
            "success_rate": int((success / total * 100)) if total > 0 else 0,
            "results": self.results.copy()
        }
    
    # 데이터 내보내기/불러오기
    def export_results(self, format_type: str) -> dict:
        """결과 내보내기 데이터 준비"""
        return {
            "export_format": format_type,
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_results_summary(),
            "config": self.config.copy(),
            "logs": self.logs.copy()
        }
    
    def import_config(self, config_data: dict):
        """설정 불러오기"""
        # 안전하게 설정 병합
        safe_keys = {
            "prompt_template", "tone", "length_limit", "banned_words",
            "mode", "max_reviews", "llm_provider", "llm_model"
        }
        
        filtered_config = {k: v for k, v in config_data.items() if k in safe_keys}
        self.update_config(filtered_config)
    
    # 유틸리티 메서드
    def reset_all(self):
        """전체 초기화"""
        self.init_data()
        self.update_login_status("ready", "로그인 필요", "네이버 계정 정보를 입력하고 로그인 테스트를 진행하세요.")
        self.update_execution_status("대기 중...")
        self.config_updated.emit(self.config.copy())
        self.add_log("INFO", "시스템이 초기화되었습니다.")
    
    def validate_config(self) -> tuple[bool, str]:
        """설정 유효성 검사"""
        if not self.config.get("prompt_template", "").strip():
            return False, "프롬프트 템플릿이 비어있습니다."
        
        if self.config.get("length_limit", 0) < 50:
            return False, "글자수 제한이 너무 낮습니다. (최소 50자)"
        
        if self.config.get("max_reviews", 0) < 1:
            return False, "최대 리뷰 수가 1보다 작습니다."
        
        return True, "설정이 유효합니다."
