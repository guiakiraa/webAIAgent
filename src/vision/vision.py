from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

def analyze_page(dom: str, task: str, history: list[str], current_url: str) -> str:
    history_text = "\n".join(history) if history else "Nenhuma ação realizada ainda."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um agente autônomo que navega na web para executar tarefas.\n"
                    "Você recebe o DOM simplificado da página atual com os elementos visíveis e interativos.\n"
                    "Cada elemento tem: tag, selector, text e type.\n\n"
                    "Ações disponíveis:\n"
                    "- navigate(url) → vai para uma URL\n"
                    "- click(selector) → clica em um elemento pelo seletor CSS\n"
                    "- click_text(text) → clica em um elemento pelo texto visível\n"
                    "- type_text(selector, text) → digita texto em um campo\n"
                    "- press_key(key) → pressiona uma tecla (Enter, Escape, Tab)\n"
                    "- scroll(direction) → rola a página (up/down)\n"
                    "- wait(milliseconds) → aguarda antes da próxima ação\n"
                    "- finish(result) → conclui a tarefa com o resultado final\n\n"
                    "Regras:\n"
                    "1. Responda SEMPRE em JSON com os campos: 'thought', 'action', 'params'\n"
                    "2. 'thought' → seu raciocínio sobre o que você vê e o que deve fazer\n"
                    "3. 'action' → o nome exato da ação a executar\n"
                    "4. 'params' → dicionário com os parâmetros da ação\n"
                    "5. Prefira click_text quando o texto do elemento for único na página\n"
                    "6. Prefira click(selector) com seletores de id (#id) quando disponíveis\n"
                    "7. Quando a tarefa estiver concluída, use finish() com o resultado\n"
                    "8. Responda APENAS com o JSON, sem markdown ou explicações extras\n"
                )
            },
            {
                "role": "user",
                "content": (
                    f"Tarefa: {task}\n\n"
                    f"URL atual: {current_url}\n\n"
                    f"Histórico de ações:\n{history_text}\n\n"
                    f"DOM simplificado da página:\n{dom}\n\n"
                    "Decida a próxima ação."
                )
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
                            "description": "Raciocínio sobre o que está na página e o que deve ser feito"
                        },
                        "action": {
                            "type": "string",
                            "enum": [
                                "navigate",
                                "click",
                                "click_text",
                                "type_text",
                                "press_key",
                                "scroll",
                                "wait",
                                "finish"
                            ],
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