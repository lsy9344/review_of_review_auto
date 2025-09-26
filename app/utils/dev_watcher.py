"""
개발 모드 파일 감시자 - 코드 변경 시 자동 재시작
"""

import os
import sys
import time
import subprocess
import threading
import logging
from pathlib import Path
from typing import List, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)


class CodeChangeHandler(FileSystemEventHandler):
    """파일 변경 이벤트 핸들러"""
    
    def __init__(self, restart_callback, watch_extensions: Set[str] = None, ignore_patterns: List[str] = None):
        super().__init__()
        self.restart_callback = restart_callback
        self.watch_extensions = watch_extensions or {'.py', '.ui', '.qss', '.yaml', '.yml', '.json'}
        self.ignore_patterns = ignore_patterns or [
            '__pycache__', '.git', '.venv', 'venv', 'logs', 'runs', '.auth',
            '.pytest_cache', '.coverage', 'dist', 'build'
        ]
        self.last_restart = 0
        self.restart_delay = 1.0  # 1초 내 중복 재시작 방지
        
    def should_ignore(self, path: str) -> bool:
        """파일이 무시 대상인지 확인"""
        path_str = str(path)
        
        # 확장자 체크
        if Path(path).suffix not in self.watch_extensions:
            return True
            
        # 무시 패턴 체크
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
                
        return False
    
    def on_modified(self, event):
        """파일 수정 이벤트"""
        if event.is_directory:
            return
            
        if self.should_ignore(event.src_path):
            return
            
        self.trigger_restart(event.src_path, "수정됨")
    
    def on_created(self, event):
        """파일 생성 이벤트"""
        if event.is_directory:
            return
            
        if self.should_ignore(event.src_path):
            return
            
        self.trigger_restart(event.src_path, "생성됨")
    
    def on_deleted(self, event):
        """파일 삭제 이벤트"""
        if event.is_directory:
            return
            
        if self.should_ignore(event.src_path):
            return
            
        self.trigger_restart(event.src_path, "삭제됨")
    
    def trigger_restart(self, file_path: str, action: str):
        """재시작 트리거"""
        current_time = time.time()
        
        # 중복 재시작 방지
        if current_time - self.last_restart < self.restart_delay:
            return
            
        self.last_restart = current_time
        
        relative_path = os.path.relpath(file_path)
        logger.info(f"파일 변경 감지: {relative_path} ({action})")
        print(f"🔄 파일 변경 감지: {relative_path} ({action})")
        print("   프로그램을 재시작합니다...")
        
        # 재시작 콜백 호출
        if self.restart_callback:
            self.restart_callback()


class DevWatcher:
    """개발 모드 파일 감시자"""
    
    def __init__(self, watch_dirs: List[str] = None, restart_command: List[str] = None):
        self.watch_dirs = watch_dirs or ['app', 'configs']
        self.restart_command = restart_command or [sys.executable, 'run.py']
        self.observer = None
        self.process = None
        self.running = False
        
        # 로거 설정
        self.setup_logging()
        
    def setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
    
    def start_process(self):
        """프로세스 시작"""
        if self.process:
            self.stop_process()
            
        try:
            logger.info(f"프로세스 시작: {' '.join(self.restart_command)}")
            self.process = subprocess.Popen(
                self.restart_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # 출력 모니터링 스레드 시작
            threading.Thread(target=self.monitor_output, daemon=True).start()
            
        except Exception as e:
            logger.error(f"프로세스 시작 실패: {e}")
    
    def stop_process(self):
        """프로세스 중지"""
        if self.process:
            try:
                logger.info("프로세스 종료 중...")
                self.process.terminate()
                
                # 2초 대기 후 강제 종료
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    logger.warning("프로세스 강제 종료")
                    self.process.kill()
                    self.process.wait()
                    
                self.process = None
                logger.info("프로세스 종료 완료")
                
            except Exception as e:
                logger.error(f"프로세스 종료 실패: {e}")
    
    def monitor_output(self):
        """프로세스 출력 모니터링"""
        if not self.process:
            return
            
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    print(line.rstrip())
                    
            # 프로세스 종료 시 리턴 코드 확인
            return_code = self.process.wait()
            if return_code != 0:
                logger.warning(f"프로세스가 오류로 종료됨 (코드: {return_code})")
                
        except Exception as e:
            logger.error(f"출력 모니터링 오류: {e}")
    
    def restart_process(self):
        """프로세스 재시작"""
        self.stop_process()
        time.sleep(0.5)  # 잠시 대기
        self.start_process()
    
    def start_watching(self):
        """파일 감시 시작"""
        if self.running:
            logger.warning("이미 감시 중입니다")
            return
            
        self.running = True
        
        # 이벤트 핸들러 생성
        handler = CodeChangeHandler(self.restart_process)
        
        # Observer 생성 및 설정
        self.observer = Observer()
        
        # 감시할 디렉토리 추가
        for watch_dir in self.watch_dirs:
            if os.path.exists(watch_dir):
                self.observer.schedule(handler, watch_dir, recursive=True)
                logger.info(f"감시 디렉토리 추가: {watch_dir}")
            else:
                logger.warning(f"감시 디렉토리 없음: {watch_dir}")
        
        # 감시 시작
        self.observer.start()
        logger.info("파일 감시 시작")
        
        # 초기 프로세스 시작
        self.start_process()
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("사용자 중단 요청")
        finally:
            self.stop()
    
    def stop(self):
        """감시 중지"""
        if not self.running:
            return
            
        self.running = False
        
        # 프로세스 중지
        self.stop_process()
        
        # Observer 중지
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("파일 감시 중지")
    
    def run_dev_mode(self):
        """개발 모드 실행"""
        print("🚀 네이버 스마트플레이스 리뷰 자동응답 - 개발 모드")
        print("=" * 60)
        print("📁 감시 중인 디렉토리:", ", ".join(self.watch_dirs))
        print("🔄 파일 변경 시 자동 재시작됩니다")
        print("⏹️  중지하려면 Ctrl+C를 눌러주세요")
        print("=" * 60)
        
        try:
            self.start_watching()
        except KeyboardInterrupt:
            print("\n👋 개발 모드를 종료합니다")
        except Exception as e:
            logger.error(f"개발 모드 실행 오류: {e}")
            print(f"❌ 오류 발생: {e}")
        finally:
            self.stop()


def create_dev_watcher(watch_dirs: List[str] = None, restart_command: List[str] = None) -> DevWatcher:
    """개발 모드 감시자 생성"""
    return DevWatcher(watch_dirs, restart_command)
