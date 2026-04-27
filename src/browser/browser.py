from playwright.sync_api import sync_playwright, Browser, Page
from playwright_stealth import Stealth

class BrowserManager:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self._playwright = None
        self._browser: Browser = None
        self._page: Page = None

    def start(self) -> Page:
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self.headless,
            args=["--start-maximized"]
        )
        context = self._browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        self._page = context.new_page()
        Stealth().apply_stealth_sync(self._page)
        return self._page

    def get_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser não iniciado. Chame start() primeiro.")
        return self._page

    def close(self):
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self._page = None
        self._browser = None
        self._playwright = None