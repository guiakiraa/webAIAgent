# Web AI Agent

> Agente autônomo que navega na web e executa tarefas descritas em linguagem natural.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![Playwright](https://img.shields.io/badge/Playwright-automation-green?style=flat)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-black?style=flat&logo=openai)

## Como funciona

O agente opera em um loop ReAct (Reason + Act) com até 15 iterações:

1. **Observa** — extrai o DOM simplificado da página atual (elementos visíveis e interativos com seus seletores CSS)
2. **Pensa** — envia o DOM, a tarefa e o histórico de ações para o GPT-4o, que decide a próxima ação
3. **Age** — executa a ação via Playwright (navegar, clicar, digitar, rolar, pressionar tecla)
4. **Repete** — até a tarefa ser concluída ou o limite de iterações ser atingido

```
Tarefa → [DOM + Histórico] → GPT-4o → Ação → Playwright → [nova página] → ...
```

## Ações disponíveis

| Ação | Descrição |
|---|---|
| `navigate(url)` | Navega para uma URL |
| `click(selector)` | Clica em um elemento pelo seletor CSS |
| `click_text(text)` | Clica em um elemento pelo texto visível |
| `type_text(selector, text)` | Digita texto em um campo |
| `press_key(key)` | Pressiona uma tecla (Enter, Escape, Tab) |
| `scroll(direction)` | Rola a página (up/down) |
| `wait(milliseconds)` | Aguarda antes da próxima ação |
| `finish(result)` | Conclui a tarefa com o resultado final |

## Estrutura do projeto

```
web-ai-agent/
├── app.py                   # Ponto de entrada (CLI)
├── src/
│   ├── agent/
│   │   ├── agent.py         # Loop ReAct principal
│   │   └── prompts.py       # System prompt e configurações
│   ├── browser/
│   │   ├── browser.py       # Inicialização do Playwright + stealth
│   │   └── actions.py       # Ações do browser (click, type, DOM, etc.)
│   └── vision/
│       └── vision.py        # Integração com GPT-4o
└── screenshots/             # Screenshots capturados durante a execução
```

## Pré-requisitos

- Python 3.11+
- Chave de API da OpenAI

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd web-ai-agent

# Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Instale os browsers do Playwright
playwright install chromium
```

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua-chave-aqui
```

## Uso

```bash
python app.py
```

O agente vai pedir a tarefa e se deve rodar com o browser visível ou em modo headless.

### Exemplos de tarefas

```
Pesquise por 'LangChain agents' e retorne os 3 primeiros resultados
Entre em wikipedia.org e pesquise por 'Inteligência Artificial'
Vá para github.com/trending e me diga quais são os 5 repositórios em alta hoje
Entre em quotes.toscrape.com e me retorne as 3 primeiras citações
```

> **Nota:** Para buscas na web, o agente usa o DuckDuckGo por padrão, navegando diretamente para `duckduckgo.com/?q=termo` para evitar bloqueios por detecção de bot.

## Detalhes técnicos

- **Extração de DOM:** seleciona até 80 elementos visíveis e interativos da página, gerando seletores CSS automaticamente (prioridade: `#id` → `[name]` → `[aria-label]` → `.class`)
- **Anti-detecção:** usa `playwright-stealth` para ocultar sinais de automação do browser
- **Decisão:** GPT-4o recebe o DOM estruturado, o histórico de ações e a URL atual para decidir cada passo
- **Screenshots:** capturados a cada iteração e salvos em `screenshots/current.png` para inspeção visual (não são enviados ao modelo)
