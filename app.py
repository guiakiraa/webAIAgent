import sys
from src.agent.agent import WebAgent

EXAMPLES = [
    "Pesquise por 'LangChain agents' no Google e retorne os 3 primeiros títulos",
    "Entre em wikipedia.org e pesquise por 'Inteligência Artificial'",
    "Vá para github.com/trending e me diga quais são os 5 repositórios em alta hoje",
    "Entre em quotes.toscrape.com e me retorne as 3 primeiras citações",
]


def on_step(iteration, message, screenshot):
    clean = message.replace("**", "").replace("`", "")
    print(f"\n[Passo {iteration}] {clean}")
    if screenshot:
        print("  >> Screenshot salvo em screenshots/current.png")


def main():
    print("=" * 60)
    print("  Web AI Agent")
    print("  Agente autônomo que navega na web via terminal.")
    print("=" * 60)
    print("\nExemplos de tarefas:")
    for i, ex in enumerate(EXAMPLES, 1):
        print(f"  {i}. {ex}")

    print()
    task = input("Descreva a tarefa para o agente: ").strip()
    if not task:
        print("Nenhuma tarefa fornecida.")
        sys.exit(1)

    headless_input = input("Rodar sem abrir o browser? (s/N): ").strip().lower()
    headless = headless_input in ("s", "sim", "y", "yes")

    print("\n" + "=" * 60)
    print("Agente iniciando...")
    print("=" * 60)

    try:
        agent = WebAgent(headless=headless)
        result = agent.run(task=task, on_step=on_step)
        print("\n" + "=" * 60)
        print("RESULTADO FINAL:")
        print(result)
        print("=" * 60)
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nErro durante a execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
