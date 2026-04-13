import os
import base64
from pathlib import Path
from playwright.sync_api import Page

SCREENSHOTS_DIR = Path("screenshots")
SCREENSHOTS_DIR.mkdir(exist_ok=True)


class BrowserActions:
    def __init__(self, page: Page):
        self.page = page

    def navigate(self, url: str) -> str:
        if not url.startswith("http"):
            url = f"https://{url}"
        self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return f"Navegou para: {url} | Título: {self.page.title()}"

    def click(self, x: int, y: int) -> str:
        self.page.mouse.click(x, y)
        self.page.wait_for_timeout(1000)
        return f"Clicou na posição ({x}, {y})"

    def type_text(self, text: str) -> str:
        self.page.keyboard.type(text, delay=50)
        return f"Digitou: {text}"

    def press_key(self, key: str) -> str:
        self.page.keyboard.press(key)
        return f"Pressionou tecla: {key}"

    def scroll(self, direction: str, amount: int = 300) -> str:
        if direction == "down":
            self.page.mouse.wheel(0, amount)
        elif direction == "up":
            self.page.mouse.wheel(0, -amount)
        self.page.wait_for_timeout(500)
        return f"Rolou a página para {direction}"

    def screenshot(self, filename: str = "current.png") -> str:
        path = SCREENSHOTS_DIR / filename
        self.page.screenshot(path=str(path))
        return str(path)

    def screenshot_as_base64(self) -> str:
        path = self.screenshot()
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_page_title(self) -> str:
        return self.page.title()

    def get_current_url(self) -> str:
        return self.page.url

    def wait(self, milliseconds: int = 1000):
        self.page.wait_for_timeout(milliseconds)
        return f"Aguardou {milliseconds}ms"