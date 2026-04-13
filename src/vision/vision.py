from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def analyze_screenshot(base64_image: str, task: str, history: list[str]) -> str:
    history_text = "\n".join(history) if history else "Nenhuma ação realizada ainda."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um agente autônomo que navega na web para executar tarefas.\n"
                    "Você recebe um screenshot da tela atual e decide qual é a próxima ação.\n\n"
                    "Ações disponíveis:\n"
                    "- navigate(url) → vai para uma URL\n"
                    "- click(x, y) → clica em uma coordenada\n"
                    "- type_text(text) → digita um texto\n"
                    "- press_key(key) → pressiona uma tecla (Enter, Escape, Tab, etc)\n"
                    "- scroll(direction, amount) → rola a página (up/down)\n"
                    "- wait(milliseconds) → aguarda antes da próxima ação\n"
                    "- finish(result) → conclui a tarefa com o resultado final\n\n"
                    "Regras:\n"
                    "1. Retorne SEMPRE os campos: 'thought', 'action', 'params'\n"
                    "2. 'thought' → seu raciocínio sobre o que você vê e o que deve fazer\n"
                    "3. 'action' → o nome exato da ação a executar\n"
                    "4. 'params' → dicionário com os parâmetros da ação\n"
                    "5. Analise o screenshot com atenção antes de decidir\n"
                    "6. Se a tarefa estiver concluída, use finish() com o resultado\n"
                    "7. Coordenadas x, y são relativas à resolução 1280x720\n"
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Tarefa: {task}\n\n"
                            f"Histórico de ações:\n{history_text}\n\n"
                            "Analise o screenshot e decida a próxima ação."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ],
        max_tokens=1000,
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "agent_action",
                "strict": False,
                "schema": {
                    "type": "object",
                    "properties": {
                        "thought": {
                            "type": "string",
                            "description": "Raciocínio sobre o que está na tela e o que deve ser feito"
                        },
                        "action": {
                            "type": "string",
                            "enum": ["navigate", "click", "type_text", "press_key", "scroll", "wait", "finish"],
                            "description": "Nome exato da ação a executar"
                        },
                        "params": {
                            "type": "object",
                            "description": "Parâmetros da ação (chaves variam conforme a action)"
                        }
                    },
                    "required": ["thought", "action", "params"],
                    "additionalProperties": False
                }
            }
        },
    )

    return response.choices[0].message.content