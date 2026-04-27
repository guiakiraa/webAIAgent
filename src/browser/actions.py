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

    def click(self, selector: str) -> str:
        try:
            self.page.wait_for_selector(selector, timeout=5000)
            self.page.click(selector)
            self.page.wait_for_timeout(1000)
            return f"Clicou no elemento: {selector}"
        except Exception as e:
            return f"Erro ao clicar em '{selector}': {str(e)}"

    def click_text(self, text: str) -> str:
        try:
            self.page.get_by_text(text, exact=False).first.click()
            self.page.wait_for_timeout(1000)
            return f"Clicou no elemento com texto: '{text}'"
        except Exception as e:
            return f"Erro ao clicar no texto '{text}': {str(e)}"

    def type_text(self, selector: str, text: str) -> str:
        try:
            self.page.wait_for_selector(selector, timeout=5000)
            self.page.click(selector)
            self.page.wait_for_timeout(300)
            self.page.fill(selector, text)
            return f"Digitou '{text}' em: {selector}"
        except Exception as e:
            return f"Erro ao digitar em '{selector}': {str(e)}"

    def press_key(self, key: str) -> str:
        self.page.keyboard.press(key)
        self.page.wait_for_timeout(500)
        return f"Pressionou tecla: {key}"

    def scroll(self, direction: str, amount: int = 300) -> str:
        if direction == "down":
            self.page.mouse.wheel(0, amount)
        elif direction == "up":
            self.page.mouse.wheel(0, -amount)
        self.page.wait_for_timeout(500)
        return f"Rolou a página para {direction}"

    def get_simplified_dom(self) -> str:
        self.page.wait_for_load_state("domcontentloaded")
        dom = self.page.evaluate("""() => {
            const TAGS = ['a', 'button', 'input', 'textarea', 'select',
                          'h1', 'h2', 'h3', 'p', 'span', 'li', 'label'];

            function getSelector(el) {
                if (el.id) return `#${el.id}`;
                if (el.name) return `[name="${el.name}"]`;
                if (el.getAttribute('aria-label'))
                    return `[aria-label="${el.getAttribute('aria-label')}"]`;
                if (el.className && typeof el.className === 'string') {
                    const cls = el.className.trim().split(/\s+/)[0];
                    if (cls) return `${el.tagName.toLowerCase()}.${cls}`;
                }
                return el.tagName.toLowerCase();
            }

            function getText(el) {
                return (el.innerText || el.value || el.placeholder ||
                        el.getAttribute('title') || el.getAttribute('aria-label') || '')
                    .trim()
                    .slice(0, 80);
            }

            const elements = [];
            document.querySelectorAll(TAGS.join(',')).forEach(el => {
                const rect = el.getBoundingClientRect();
                if (rect.width === 0 || rect.height === 0) return;
                if (rect.top < 0 || rect.top > window.innerHeight) return;

                const text = getText(el);
                if (!text) return;

                elements.push({
                    tag: el.tagName.toLowerCase(),
                    selector: getSelector(el),
                    text: text,
                    type: el.type || null
                });
            });

            return JSON.stringify(elements.slice(0, 80), null, 2);
        }""")
        return dom

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