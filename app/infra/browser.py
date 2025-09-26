"""Playwright browser launcher and utilities.

This module provides a thin synchronous wrapper around Playwright for use by
services that need to interact with a headed browser (login, navigation).
"""

from __future__ import annotations

import os

from pathlib import Path
from typing import Optional


class BrowserClient:
    """Synchronous Playwright browser client.

    The client owns the Playwright lifecycle. Call ``initialize`` before use and
    ``close`` when finished. Consumers can create new isolated contexts, load
    existing storage state (cookies) and persist storage state back to disk.
    """

    def __init__(self) -> None:
        self._playwright = None
        self.browser = None

    def initialize(
        self,
        headless: bool = False,
        slow_mo_ms: int = 0,
        browser_type: Optional[str] = None,
    ) -> None:
        """Start Playwright and launch a browser.

        Parameters
        - headless: Run browser headless or headed (default: headed)
        - slow_mo_ms: Slow down Playwright operations by the given milliseconds
        - browser_type: Optional Playwright browser name (chromium/firefox/webkit)
        """
        # Import locally to keep import time low when Playwright is unused.
        from playwright.sync_api import sync_playwright

        resolved_browser = browser_type or os.getenv("PLAYWRIGHT_BROWSER", "chromium")

        self._playwright = sync_playwright().start()
        try:
            launcher = getattr(self._playwright, resolved_browser)
        except AttributeError as exc:  # noqa: B902 - map to ValueError
            self._playwright.stop()
            raise ValueError(
                f"지원하지 않는 Playwright 브라우저 타입: {resolved_browser}"
            ) from exc

        self.browser = launcher.launch(headless=headless, slow_mo=slow_mo_ms)

    def new_context(self, storage_state_path: Optional[Path] = None):
        """Create a new browser context, optionally loading storage state.

        Returns a Playwright BrowserContext. The caller is responsible for
        closing the returned context.
        """
        if self.browser is None:
            raise RuntimeError(
                "BrowserClient not initialized. Call initialize() first."
            )

        storage_state = str(storage_state_path) if storage_state_path else None
        context = self.browser.new_context(
            storage_state=storage_state,
            locale="ko-KR",
        )
        return context

    def save_storage_state(self, context, path: Path) -> None:
        """Persist the given context's storage (cookies/localStorage) to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(path))

    def close(self) -> None:
        """Close the browser and stop Playwright."""
        try:
            if self.browser is not None:
                self.browser.close()
        finally:
            if self._playwright is not None:
                self._playwright.stop()
