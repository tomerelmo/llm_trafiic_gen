from __future__ import annotations

import contextlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from .logging.logger import ActionLogger
from .utils.human import human_delay


@dataclass
class DOMSnapshot:
    url: str
    html_path: Path


class BrowserSession:
    """Thin wrapper around Playwright to simplify scripted navigation."""

    def __init__(
        self,
        headless: bool,
        action_logger: ActionLogger,
        download_dir: Optional[Path] = None,
    ) -> None:
        self.headless = headless
        self.action_logger = action_logger
        self.download_dir = download_dir or Path("data") / "snapshots"
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser page is not initialized. Use within context manager.")
        return self._page

    @contextlib.contextmanager
    def session(self) -> Iterable[Page]:
        with sync_playwright() as p:
            self._playwright = p
            self._browser = p.chromium.launch(headless=self.headless, args=["--start-maximized"])
            self._context = self._browser.new_context()
            self._page = self._context.new_page()
            try:
                yield self._page
            finally:
                self._context.close()
                self._browser.close()

    def goto(self, url: str) -> None:
        self.page.goto(url, wait_until="networkidle")
        self.page.wait_for_timeout(int(human_delay(0.5, 0.5) * 1000))
        self.action_logger.record("navigate", url)

    def click_text(self, text: str) -> None:
        self.page.get_by_text(text, exact=False).first.click(delay=int(human_delay() * 1000))
        self.action_logger.record("click", self.page.url, text=text)

    def fill_form(self, selector: str, value: str) -> None:
        self.page.fill(selector, value)
        self.page.wait_for_timeout(int(human_delay() * 1000))
        self.action_logger.record("fill", self.page.url, selector=selector)

    def snapshot_dom(self, name: str) -> DOMSnapshot:
        self.download_dir.mkdir(parents=True, exist_ok=True)
        html_path = self.download_dir / f"{name}.html"
        html = self.page.content()
        html_path.write_text(html, encoding="utf-8")
        self.action_logger.record("snapshot", self.page.url, path=str(html_path))
        return DOMSnapshot(url=self.page.url, html_path=html_path)

    def save_storage(self, path: Path) -> None:
        if self._context is None:
            raise RuntimeError("No context to save")
        storage = self._context.storage_state()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(storage), encoding="utf-8")
        self.action_logger.record("save_storage", self.page.url, path=str(path))
