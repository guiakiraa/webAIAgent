import json
import re

from src.browser.browser import BrowserManager
from src.browser.actions import BrowserActions
from src.vision.vision import analyze_screenshot
from src.tools.browser_tools import create_browser_tools
from src.agent.prompts import SYSTEM_PROMPT, MAX_ITERATIONS
from dotenv import load_dotenv

load_dotenv()


class WebAgent:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser_manager = BrowserManager(headless=headless)
        self.page = None
        self.actions = None
        self.tools = None

    def _setup(self):
        self.page = self.browser_manager.start()
        self.actions = BrowserActions(self.page)
        self.tools = create_browser_tools(self.actions)

    def _parse_action(self, vision_response: str) -> dict:
        try:
            clean = re.sub(r"```json|```", "", vision_response).strip()
            return json.loads(clean)
        except Exception:
            return {
                "thought": "Erro ao parsear resposta",
                "action": "finish",
                "params": {"result": vision_response}
            }

    def _execute_action(self, action: str, params: dict) -> str:
        tool_map = {tool.name: tool for tool in self.tools}

        if action == "finish":
            return f"FINISH:{params.get('result', 'Tarefa concluída.')}"

        if action not in tool_map:
            return f"Ação desconhecida: {action}"

        tool = tool_map[action]

        if action == "click":
            x = params.get("x", 0)
            y = params.get("y", 0)
            return tool.invoke(f"{x},{y}")

        if action == "scroll":
            direction = params.get("direction", "down")
            return tool.invoke(direction)

        if action == "wait":
            ms = params.get("milliseconds", 1000)
            return tool.invoke(str(ms))

        if action in ["get_current_url", "get_page_title"]:
            return tool.invoke("")

        value = next(iter(params.values()), "") if params else ""
        return tool.invoke(str(value))

    def run(self, task: str, on_step=None) -> str:
        self._setup()
        history = []
        result = None

        try:
            for iteration in range(1, MAX_ITERATIONS + 1):
                if on_step:
                    on_step(iteration, "Capturando screenshot...", None)

                b64 = self.actions.screenshot_as_base64()

                if on_step:
                    on_step(iteration, "Analisando tela com GPT-4o Vision...", b64)

                vision_response = analyze_screenshot(
                    base64_image=b64,
                    task=task,
                    history=history
                )

                parsed = self._parse_action(vision_response)
                thought = parsed.get("thought", "")
                action = parsed.get("action", "finish")
                params = parsed.get("params", {})

                step_log = (
                    f"[Passo {iteration}]\n"
                    f"Raciocínio: {thought}\n"
                    f"Ação: {action} | Params: {params}"
                )
                history.append(step_log)

                if on_step:
                    on_step(iteration, step_log, b64)

                action_result = self._execute_action(action, params)

                if action_result.startswith("FINISH:"):
                    result = action_result.replace("FINISH:", "").strip()
                    break

                history.append(f"Resultado: {action_result}")

            if result is None:
                result = f"Agente atingiu o limite de {MAX_ITERATIONS} iterações sem concluir a tarefa."

        finally:
            self.browser_manager.close()

        return result