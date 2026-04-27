import json
import re
from src.browser.browser import BrowserManager
from src.browser.actions import BrowserActions
from src.vision.vision import analyze_page
from src.agent.prompts import MAX_ITERATIONS
from dotenv import load_dotenv

load_dotenv()


class WebAgent:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser_manager = BrowserManager(headless=headless)
        self.page = None
        self.actions = None

    def _setup(self):
        self.page = self.browser_manager.start()
        self.actions = BrowserActions(self.page)

    def _parse_action(self, response: str) -> dict:
        try:
            clean = re.sub(r"```json|```", "", response).strip()
            return json.loads(clean)
        except Exception:
            return {
                "thought": "Erro ao parsear resposta",
                "action": "finish",
                "params": {"result": response}
            }

    def _execute_action(self, action: str, params: dict) -> str:
        if action == "finish":
            return f"FINISH:{params.get('result', 'Tarefa concluída.')}"

        if action == "navigate":
            return self.actions.navigate(params.get("url", ""))

        if action == "click":
            return self.actions.click(params.get("selector", ""))

        if action == "click_text":
            return self.actions.click_text(params.get("text", ""))

        if action == "type_text":
            return self.actions.type_text(
                params.get("selector", ""),
                params.get("text", "")
            )

        if action == "press_key":
            return self.actions.press_key(params.get("key", "Enter"))

        if action == "scroll":
            return self.actions.scroll(params.get("direction", "down"))

        if action == "wait":
            return self.actions.wait(params.get("milliseconds", 1000))

        return f"Ação desconhecida: {action}"

    def run(self, task: str, on_step=None) -> str:
        self._setup()
        history = []
        result = None

        try:
            for iteration in range(1, MAX_ITERATIONS + 1):
                if on_step:
                    on_step(iteration, "Extraindo DOM da página...", None)

                dom = self.actions.get_simplified_dom()
                current_url = self.actions.get_current_url()
                screenshot = self.actions.screenshot_as_base64()

                if on_step:
                    on_step(iteration, "Analisando página com GPT-4o...", screenshot)

                response = analyze_page(
                    dom=dom,
                    task=task,
                    history=history,
                    current_url=current_url
                )

                parsed = self._parse_action(response)
                thought = parsed.get("thought", "")
                action = parsed.get("action", "finish")
                params = parsed.get("params", {})

                step_log = (
                    f"**Passo {iteration}**\n"
                    f"🧠 Raciocínio: {thought}\n"
                    f"⚡ Ação: `{action}` | Params: `{params}`"
                )
                history.append(step_log)

                if on_step:
                    on_step(iteration, step_log, screenshot)

                action_result = self._execute_action(action, params)

                if action_result.startswith("FINISH:"):
                    result = action_result.replace("FINISH:", "").strip()
                    break

                history.append(f"Resultado: {action_result}")

        finally:
            self.browser_manager.close()

        if result is None:
            result = f"Agente atingiu o limite de {MAX_ITERATIONS} iterações sem concluir a tarefa."

        return result