"""
메인 윈도우 - 네이버 스마트플레이스 리뷰 자동응답 시스템의 메인 UI
"""

from PySide6.QtCore import QObject, QThread
from PySide6.QtCore import Signal as pyqtSignal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.core.config import CrawlConfig
from app.core.errors import LoginError, StoreEnumerationError
from app.services.login_service import LoginResult, NaverLoginService
from app.services.reply_generator import ReplyConfig, ReplyGenerator
from app.services.review_crawler import CrawlResult, ReviewCrawler
from app.services.stop_signal import StopSignal
from app.services.store_enumerator import StoreEnumerator
from app.services.submitter import ReplySubmitter
from app.utils.auth import get_openai_api_key

import httpx

from .styles import Theme, ThemeManager
from .viewmodel import ViewModel
from .widgets import (
    BusinessListWidget,
    ConfigWidget,
    ControlWidget,
    LoginWidget,
    ResultsWindow,
)
from .widgets.log_widget import LogWidget


class _LoginWorker(QObject):
    """로그인 과정을 처리하는 워커"""

    finished = pyqtSignal()
    success = pyqtSignal(LoginResult)
    failure = pyqtSignal(str)

    def __init__(self, user_id: str, password: str, force_credential_login: bool):
        super().__init__()
        self._user_id = user_id
        self._password = password
        self._force_credential_login = force_credential_login
        self._login_service = NaverLoginService(headless=False)

    def run(self) -> None:
        """로그인 실행"""
        try:
            result = self._login_service.login(
                self._user_id, self._password, self._force_credential_login
            )
            if result.success:
                self.success.emit(result)
            else:
                self.failure.emit(result.message)
        except Exception as e:
            self.failure.emit(f"알 수 없는 오류 발생: {e}")
        finally:
            self.finished.emit()


class _OrchestrationWorker(QObject):
    """전체 실행 흐름(열거->크롤링->답변생성->제출)을 관리하는 워커"""

    finished = pyqtSignal()
    success = pyqtSignal(CrawlResult)
    failure = pyqtSignal(str)
    log_emitted = pyqtSignal(str, str)
    progress = pyqtSignal(int, int)
    counts = pyqtSignal(int, int, int)
    reply_generation_started = pyqtSignal()
    reply_submission_started = pyqtSignal()

    def __init__(self, config: CrawlConfig, stop_signal: StopSignal | None = None) -> None:
        super().__init__()
        self._config = config
        self._stop_signal = stop_signal
        self._login_service = NaverLoginService(headless=not config.browser_visible)

    def run(self) -> None:
        """실행의 메인 로직"""
        try:
            # 1. 인증된 HTTP 클라이언트 생성 (로그인은 이미 완료되었다고 가정)
            self.log_emitted.emit(
                "INFO", "저장된 인증 정보로 API 클라이언트를 생성합니다."
            )
            client = self._login_service.get_authenticated_client()

            try:
                # 2. 가게 ID 매핑
                enumerator = StoreEnumerator(client)
                store_mappings = []
                total_stores = len(self._config.business_ids)
                self.log_emitted.emit(
                    "INFO", f"{total_stores}개 사업장의 ID를 확인합니다."
                )
                for i, booking_id in enumerate(self._config.business_ids):
                    self.progress.emit(i, total_stores)
                    try:
                        id_map = enumerator.get_store_ids(
                            booking_business_id=booking_id, user_id=self._config.user_id
                        )
                        store_mappings.append({"booking_id": booking_id, **id_map})
                    except StoreEnumerationError as e:
                        self.log_emitted.emit(
                            "ERROR", f"사업장 ID '{booking_id}' 확인 실패: {e}"
                        )
                        continue

                self.progress.emit(total_stores, total_stores)
                if not store_mappings:
                    raise ValueError("리뷰를 수집할 유효한 사업장이 없습니다.")

                # 3. 리뷰 크롤링
                crawler = ReviewCrawler(client, self._stop_signal)
                crawl_result = crawler.fetch_reviews(
                    stores=store_mappings, log=self.log_emitted.emit
                )

                # 4. 답변 생성 (활성화된 경우)
                if self._config.enable_reply_generation and self._config.openai_api_key:
                    self.reply_generation_started.emit()
                    crawl_result = self._generate_replies(crawl_result)

                # 5. 답변 제출 (활성화된 경우)
                if self._config.auto_submit_replies and crawl_result:
                    self.reply_submission_started.emit()
                    self._submit_replies(crawl_result, client)

                # 6. 결과 처리
                self.success.emit(crawl_result)

            finally:
                # HTTP 클라이언트 세션 종료
                client.close()

        except LoginError as exc:
            self.log_emitted.emit(
                "ERROR", "로그인 정보가 유효하지 않습니다. 다시 로그인해주세요."
            )
            self.failure.emit(str(exc))
        except Exception as exc:
            self.failure.emit(str(exc))
        finally:
            self.finished.emit()

    def _generate_replies(self, crawl_result: CrawlResult) -> CrawlResult:
        """크롤링된 리뷰에 대한 답변을 생성합니다."""
        self.log_emitted.emit("INFO", "리뷰 답변 생성을 시작합니다.")

        try:
            # 답변 생성 설정
            reply_config = ReplyConfig(
                tone=self._config.tone,
                business_type=self._config.business_type,
                openai_api_key=self._config.openai_api_key,
                custom_prompt=self._config.custom_prompt,
            )

            # 답변 생성기 초기화
            reply_generator = ReplyGenerator(reply_config)

            # 각 매장별로 답변 생성
            for store in crawl_result.stores:
                if store.error or not store.reviews:
                    continue

                self.log_emitted.emit(
                    "INFO", f"매장 '{store.booking_id}' 리뷰 답변 생성 중..."
                )

                # 답변 생성
                reply_pairs = reply_generator.generate_batch(
                    reviews=store.reviews, log=self.log_emitted.emit
                )

                # 생성된 답변을 매장 데이터에 추가
                store.generated_replies = reply_pairs

            self.log_emitted.emit("SUCCESS", "리뷰 답변 생성이 완료되었습니다.")
            return crawl_result

        except Exception as e:
            self.log_emitted.emit("ERROR", f"답변 생성 중 오류 발생: {e}")
            return crawl_result

    def _submit_replies(self, crawl_result: CrawlResult, client: httpx.Client) -> None:
        """생성된 답변을 네이버 스마트플레이스에 제출합니다."""
        self.log_emitted.emit("INFO", "리뷰 답변 제출을 시작합니다.")

        try:
            # 답변 제출기 초기화 (API 클라이언트 사용)
            submitter = ReplySubmitter(client)

            for store in crawl_result.stores:
                if not hasattr(store, "generated_replies") or store.error:
                    continue

                # 제출할 답변이 있는 경우만 처리
                valid_replies = [
                    {"review_id": reply.review_id, "reply_text": reply.generated_reply}
                    for reply in store.generated_replies
                    if reply.generated_reply and not reply.error
                ]

                if not valid_replies:
                    continue

                self.log_emitted.emit(
                    "INFO", f"매장 '{store.booking_id}' 답변 API 제출 중..."
                )

                # 답변 일괄 제출
                submission_results = submitter.submit_batch(
                    reply_pairs=valid_replies,
                    place_seq=store.place_seq,
                    booking_id=store.booking_id,
                    log=self.log_emitted.emit,
                )

                # 제출 결과를 매장 데이터에 추가
                store.submission_results = submission_results

            self.log_emitted.emit("SUCCESS", "리뷰 답변 제출이 완료되었습니다.")

        except Exception as e:
            self.log_emitted.emit("ERROR", f"답변 제출 중 오류 발생: {e}")


class MainWindow(QMainWindow):
    """네이버 스마트플레이스 리뷰 자동응답 메인 윈도우"""

    def __init__(self):
        super().__init__()

        # 뷰모델 및 테마 매니저 초기화
        self.viewmodel = ViewModel()
        self.theme_manager = ThemeManager()

        self.init_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_styles()
        self.connect_viewmodel()

        # 서비스 초기화
        self._login_thread = None
        self._login_worker = None
        self._stop_signal = StopSignal()

        # 실행 관련 상태
        self._execution_thread = None
        self._execution_worker = None
        self._last_crawl_result: CrawlResult | None = None
        self._results_window = None  # 결과창 인스턴스

    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("네이버 스마트플레이스 리뷰 자동응답 시스템")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # 중앙 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # 상단 영역 (로그인 + 사업장 리스트 + 설정)
        top_layout = QHBoxLayout()

        # 왼쪽 패널 (로그인)
        self.login_widget = LoginWidget()
        self.login_widget.setMaximumWidth(400)

        # 중간 패널 (사업장 리스트)
        self.business_list_widget = BusinessListWidget()
        self.business_list_widget.setMaximumWidth(400)

        # 오른쪽 패널 (설정)
        self.config_widget = ConfigWidget()

        top_layout.addWidget(self.login_widget)
        top_layout.addWidget(self.business_list_widget)
        top_layout.addWidget(self.config_widget, 1)

        # 중앙 영역 (실행 컨트롤)
        self.control_widget = ControlWidget()

        # 하단 영역 (로그)
        self.log_widget = LogWidget()

        # 레이아웃에 위젯 추가
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.control_widget)
        main_layout.addWidget(self.log_widget)
        main_layout.addStretch()  # 여백 추가

        # 폰트 설정
        self.set_korean_font()

    def setup_menu(self):
        """메뉴바 설정"""
        menubar = self.menuBar()

        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")
        file_menu.addAction("설정 불러오기", self.load_config)
        file_menu.addAction("설정 저장", self.save_config)
        file_menu.addSeparator()
        file_menu.addAction("종료", self.close)

        # 도구 메뉴
        tools_menu = menubar.addMenu("도구(&T)")
        tools_menu.addAction("로그 폴더 열기", self.open_log_folder)
        tools_menu.addAction("데이터베이스 초기화", self.reset_database)
        tools_menu.addAction("셀렉터 테스트", self.test_selectors)

        # 도움말 메뉴
        help_menu = menubar.addMenu("도움말(&H)")
        help_menu.addAction("사용법", self.show_help)
        help_menu.addAction("정보", self.show_about)

    def setup_status_bar(self):
        """상태바 설정"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("시스템 준비 완료")

    def set_korean_font(self):
        """한글 폰트 설정"""
        korean_font = QFont("맑은 고딕", 9)
        korean_font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(korean_font)

    def update_status(self, message: str):
        """상태바 메시지 업데이트"""
        self.status_bar.showMessage(message)

    def load_config(self):
        """설정 불러오기 (향후 구현)"""
        self.update_status("설정 불러오기 - 구현 예정")

    def save_config(self):
        """설정 저장 (향후 구현)"""
        self.update_status("설정 저장 - 구현 예정")

    def open_log_folder(self):
        """로그 폴더 열기 (향후 구현)"""
        self.update_status("로그 폴더 열기 - 구현 예정")

    def reset_database(self):
        """데이터베이스 초기화 (향후 구현)"""
        self.update_status("데이터베이스 초기화 - 구현 예정")

    def test_selectors(self):
        """셀렉터 테스트 (향후 구현)"""
        self.update_status("셀렉터 테스트 - 구현 예정")

    def show_help(self):
        """사용법 표시 (향후 구현)"""
        self.update_status("사용법 표시 - 구현 예정")

    def show_about(self):
        """정보 표시 (향후 구현)"""
        self.update_status("정보 표시 - 구현 예정")

    def apply_styles(self):
        """스타일 적용"""
        stylesheet = self.theme_manager.get_stylesheet()
        self.setStyleSheet(stylesheet)

        # 위젯별 추가 스타일 적용
        self.control_widget.start_button.setProperty("class", "success")
        self.control_widget.stop_button.setProperty("class", "danger")

    def connect_viewmodel(self):
        """뷰모델 시그널 연결"""
        # 로그인 상태 연결
        self.viewmodel.login_status_changed.connect(self.login_widget.set_status)
        self.login_widget.login_requested.connect(self.on_login_requested)

        # 실행 상태 연결
        self.viewmodel.execution_status_changed.connect(
            self.control_widget.update_status
        )
        self.viewmodel.progress_updated.connect(self.control_widget.update_progress)
        self.viewmodel.counts_updated.connect(self.control_widget.update_counts)

        self.control_widget.start_requested.connect(self.on_start_requested)
        self.control_widget.stop_requested.connect(self.on_stop_requested)
        self.control_widget.view_results_requested.connect(self._show_results_window)
        self.control_widget.generate_replies_requested.connect(
            self.on_generate_replies_requested
        )

        # 로그 연결
        self.viewmodel.log_message_added.connect(self.log_widget.add_log_message)

        # 테마 변경 연결
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        # 사업장 리스트 연결
        self.business_list_widget.business_list_changed.connect(
            self.on_business_list_changed
        )

    def on_login_requested(self, user_id: str, password: str):
        """로그인 요청 처리"""
        if self._login_thread and self._login_thread.isRunning():
            self.viewmodel.add_log("WARNING", "이미 로그인 프로세스가 진행 중입니다.")
            return

        self.viewmodel.update_login_status(
            "testing", "로그인 테스트 중...", f"{user_id} 계정으로 로그인을 시도합니다."
        )

        self._login_thread = QThread()
        self._login_worker = _LoginWorker(
            user_id, password, force_credential_login=False
        )
        self._login_worker.moveToThread(self._login_thread)

        self._login_thread.started.connect(self._login_worker.run)
        self._login_worker.finished.connect(self._login_thread.quit)
        self._login_worker.finished.connect(self._login_worker.deleteLater)
        self._login_worker.success.connect(self._on_login_success)
        self._login_worker.failure.connect(self._on_login_failure)
        self._login_thread.finished.connect(self._cleanup_login_thread)
        self._login_thread.finished.connect(self._login_thread.deleteLater)

        self._login_thread.start()

    def _on_login_success(self, result: LoginResult):
        """로그인 성공 처리"""
        self.viewmodel.set_login_user(
            self.login_widget.get_credentials()[0], result.used_cookies
        )
        self.viewmodel.update_login_status("success", "로그인 성공", result.message)
        self.viewmodel.add_log("SUCCESS", result.message)
        self.login_widget.login_success(result.message)

    def _on_login_failure(self, error_message: str):
        """로그인 실패 처리"""
        self.viewmodel.update_login_status("error", "로그인 실패", error_message)
        self.viewmodel.add_log("ERROR", f"로그인 실패: {error_message}")
        self.login_widget.login_failed(error_message)

    def _cleanup_login_thread(self):
        """로그인 스레드 정리"""
        self._login_worker = None
        self._login_thread = None

    def on_start_requested(self):
        """실행 시작 요청"""
        if self._execution_thread and self._execution_thread.isRunning():
            self.viewmodel.add_log("WARNING", "리뷰 수집이 이미 진행 중입니다.")
            return

        config = self._build_crawl_config()
        if not config:
            return

        self.viewmodel.add_log(
            "DEBUG", f"CrawlConfig.auto_submit_replies = {config.auto_submit_replies}"
        )

        # 새 작업을 위한 정지 신호 초기화
        self._stop_signal = StopSignal()

        self.viewmodel.clear_results()
        self.viewmodel.start_execution()
        self.viewmodel.update_progress(0, len(config.business_ids))
        self.update_status("리뷰 수집을 시작합니다.")

        self._execution_thread = QThread()
        self._execution_worker = _OrchestrationWorker(config, self._stop_signal)
        self._execution_worker.moveToThread(self._execution_thread)

        self._execution_thread.started.connect(self._execution_worker.run)
        self._execution_worker.finished.connect(self._execution_thread.quit)
        self._execution_worker.finished.connect(self._execution_worker.deleteLater)
        self._execution_worker.log_emitted.connect(self._handle_execution_log)
        self._execution_worker.progress.connect(self.viewmodel.update_progress)
        self._execution_worker.counts.connect(self.viewmodel.update_counts)
        self._execution_worker.success.connect(self._handle_execution_success)
        self._execution_worker.failure.connect(self._handle_execution_failure)
        self._execution_thread.finished.connect(self._cleanup_execution_thread)
        self._execution_thread.finished.connect(self._execution_thread.deleteLater)

        self._execution_thread.start()

    def _build_crawl_config(self) -> CrawlConfig | None:
        """UI에서 모든 설정을 수집하여 CrawlConfig 객체를 생성합니다."""
        business_ids = self.business_list_widget.get_business_list()
        if not business_ids:
            self.viewmodel.add_log("ERROR", "사업장 ID를 한 개 이상 입력하세요.")
            QMessageBox.warning(self, "입력 오류", "사업장 ID를 한 개 이상 입력하세요.")
            return None

        user_id, password = self.login_widget.get_credentials()
        if not user_id or not password:
            self.viewmodel.add_log("ERROR", "로그인 정보를 입력한 뒤 다시 시도하세요.")
            QMessageBox.warning(self, "로그인 필요", "아이디와 비밀번호를 입력하세요.")
            return None

        # API 키 자동 로드
        openai_api_key = get_openai_api_key()

        return CrawlConfig(
            user_id=user_id,
            password=password,
            business_ids=business_ids,
            browser_visible=False,  # 실행 시에는 브라우저 숨김
            # 답변 생성 설정
            openai_api_key=openai_api_key or "",
            business_type=self.config_widget.get_config()["business_type"],
            tone=self.config_widget.get_config()["tone"],
            custom_prompt=self.config_widget.get_config()["custom_prompt"],
            # 답변 생성 활성화 (API 키가 있을 때만)
            enable_reply_generation=bool(openai_api_key),
            auto_submit_replies=self.control_widget.is_auto_submit_enabled(),
        )

    def on_stop_requested(self):
        """실행 정지 요청"""
        if self._execution_thread and self._execution_thread.isRunning():
            # 정지 신호 설정
            self._stop_signal.stop()
            self.viewmodel.add_log(
                "INFO",
                "정지 신호를 전송했습니다. 현재 작업이 완료되는 대로 중단됩니다.",
            )
        self.viewmodel.stop_execution()
        self.update_status("실행 정지 요청됨")

    def on_generate_replies_requested(self):
        """답변만 생성 요청 (기존 크롤링 결과에 대해)"""
        if not self._last_crawl_result:
            QMessageBox.information(self, "알림", "먼저 리뷰를 수집해주세요.")
            return

        # OpenAI API 키 확인
        openai_api_key = get_openai_api_key()
        if not openai_api_key:
            QMessageBox.warning(
                self,
                "API 키 필요",
                "OpenAI API Key가 설정되지 않았습니다.\n.auth/openai_api.json 파일을 확인해주세요.",
            )
            return

        self.viewmodel.add_log("INFO", "기존 리뷰에 대한 답변 생성을 시작합니다.")

        try:
            # 답변 생성 설정
            config = self.config_widget.get_config()
            reply_config = ReplyConfig(
                tone=config["tone"],
                business_type=config["business_type"],
                openai_api_key=openai_api_key,
                custom_prompt=config["custom_prompt"],
            )

            # 답변 생성기 초기화
            reply_generator = ReplyGenerator(reply_config)

            # 각 매장별로 답변 생성
            total_replies_generated = 0
            for store in self._last_crawl_result.stores:
                if store.error or not store.reviews:
                    continue

                self.viewmodel.add_log(
                    "INFO", f"매장 '{store.booking_id}' 리뷰 답변 생성 중..."
                )

                # 답변 생성
                reply_pairs = reply_generator.generate_batch(
                    reviews=store.reviews, log=self.viewmodel.add_log
                )

                # 생성된 답변을 매장 데이터에 추가
                store.generated_replies = reply_pairs
                total_replies_generated += len(
                    [r for r in reply_pairs if r.generated_reply and not r.error]
                )

            self.viewmodel.add_log(
                "SUCCESS",
                f"답변 생성 완료: 총 {total_replies_generated}개 답변이 생성되었습니다.",
            )
            QMessageBox.information(
                self,
                "완료",
                f"답변 생성이 완료되었습니다.\n생성된 답변: {total_replies_generated}개",
            )

        except Exception as e:
            error_msg = f"답변 생성 중 오류 발생: {e}"
            self.viewmodel.add_log("ERROR", error_msg)
            QMessageBox.critical(self, "오류", error_msg)

    def _handle_execution_log(self, level: str, message: str) -> None:
        self.viewmodel.add_log(level, message)

    def _handle_execution_success(self, result: CrawlResult) -> None:
        self._last_crawl_result = result
        stores = result.stores or []
        success_count = len([store for store in stores if store.error is None])
        failure_count = len(stores) - success_count
        total_reviews = sum(store.review_count for store in stores)

        for store in stores:
            status = "성공" if store.error is None else "실패"
            result_entry = {
                "status": status,
                "identifier": store.booking_id,
                "identifier_type": "booking",
                "review_count": store.review_count,
                "review_url": store.review_url,
            }
            if store.error:
                result_entry["error"] = store.error
            else:
                result_entry["reviews"] = store.reviews
            self.viewmodel.add_result(result_entry)

        summary = (
            f"리뷰 수집 완료: {len(stores)}개 대상에서 {total_reviews}건 리뷰 확보"
        )
        self.viewmodel.add_log("INFO", "인증 후 리뷰 수집을 완료했습니다.")
        self.viewmodel.complete_execution(summary)
        self.control_widget.execution_completed(success_count, failure_count)
        self.update_status(summary)

    def _handle_execution_failure(self, error_message: str) -> None:
        failure_message = f"리뷰 수집 실패: {error_message}"
        self.viewmodel.complete_execution(failure_message, level="ERROR")
        self.control_widget.execution_completed(0, 0)
        self.update_status(failure_message)
        QMessageBox.critical(self, "실행 실패", failure_message)

    def _cleanup_execution_thread(self) -> None:
        self._execution_worker = None
        self._execution_thread = None

    def _show_results_window(self):
        """결과 보기 창을 띄웁니다."""
        if not self._last_crawl_result:
            QMessageBox.information(self, "알림", "먼저 리뷰를 수집해주세요.")
            return

        if not self._results_window:
            self._results_window = ResultsWindow(self)

        self._results_window.populate_data(self._last_crawl_result)
        self._results_window.show()
        self._results_window.activateWindow()

    def on_theme_changed(self, theme: Theme):
        """테마 변경 처리"""
        self.apply_styles()
        self.update_status(f"테마가 {theme.value}로 변경되었습니다.")

    def on_business_list_changed(self, business_list: list):
        """사업장 리스트 변경 처리"""
        self.viewmodel.add_log(
            "INFO", f"사업장 리스트 업데이트: {len(business_list)}개 사업장"
        )
        # 사업장 리스트를 뷰모델에 저장 (향후 자동 순회 기능에 사용)

    def closeEvent(self, event):
        """윈도우 종료 이벤트"""
        if self.viewmodel.is_running():
            reply = QMessageBox.question(
                self,
                "확인",
                "실행 중입니다. 정말 종료하시겠습니까?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

        self.viewmodel.stop_execution()
        self.update_status("시스템 종료 중...")
        event.accept()
