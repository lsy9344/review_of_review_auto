"""
테마 관리 모듈 - 라이트/다크 테마 전환 및 테마 설정 관리
"""

from enum import Enum
from PySide6.QtCore import QObject, Signal as pyqtSignal
from .main_style import get_main_stylesheet, get_dark_stylesheet


class Theme(Enum):
    """테마 타입"""

    LIGHT = "light"
    DARK = "dark"
    AUTO = "auto"  # 시스템 설정에 따라 자동


class ThemeManager(QObject):
    """테마 관리자"""

    # 시그널
    theme_changed = pyqtSignal(Theme)

    def __init__(self):
        super().__init__()
        self._current_theme = Theme.LIGHT
        self._stylesheets = {
            Theme.LIGHT: get_main_stylesheet(),
            Theme.DARK: get_dark_stylesheet(),
        }

    @property
    def current_theme(self) -> Theme:
        """현재 테마 반환"""
        return self._current_theme

    def set_theme(self, theme: Theme):
        """테마 설정"""
        if theme != self._current_theme:
            self._current_theme = theme
            self.theme_changed.emit(theme)

    def get_stylesheet(self, theme: Theme = None) -> str:
        """테마에 해당하는 스타일시트 반환"""
        if theme is None:
            theme = self._current_theme

        if theme == Theme.AUTO:
            # 시스템 테마 감지 로직 (향후 구현)
            theme = Theme.LIGHT

        return self._stylesheets.get(theme, self._stylesheets[Theme.LIGHT])

    def toggle_theme(self):
        """테마 토글 (라이트 ↔ 다크)"""
        if self._current_theme == Theme.LIGHT:
            self.set_theme(Theme.DARK)
        else:
            self.set_theme(Theme.LIGHT)

    def apply_custom_colors(self, colors: dict):
        """커스텀 색상 적용 (향후 확장)"""
        # 사용자 정의 색상 스키마 적용
        pass
