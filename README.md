# Web AI Agent

> Projeto de estudo: um agente que navega na web e executa tarefas descritas em linguagem natural, usando Playwright + GPT-4o num loop ReAct.

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=flat&logo=python)
![Playwright](https://img.shields.io/badge/Playwright-automation-green?style=flat)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-black?style=flat&logo=openai)

> [!NOTE]
> **Este é um projeto de aprendizado.** Construí ele para praticar Playwright na prática — extração de DOM, seletores, esperas, ciclo de vida do browser — usando um agente LLM como desculpa para explorar a biblioteca a fundo.
>
> **Não é um produto.** Não tem testes, não tem tratamento de erro robusto e não foi pensado para rodar em produção. As [limitações conhecidas](#limitações-conhecidas) estão documentadas no final, sem maquiagem.

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
│   │   └── prompts.py       # Configurações do agente (MAX_ITERATIONS)
│   ├── browser/
│   │   ├── browser.py       # Inicialização do Playwright + stealth
│   │   └── actions.py       # Ações do browser (click, type, DOM, etc.)
│   └── vision/
│       └── vision.py        # System prompt do agente + chamada ao GPT-4o
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

## O que eu aprendi de Playwright

Cada item abaixo é algo que o código exercita de verdade — foi o motivo de o projeto existir:

- **`page.evaluate()` para rodar JS no contexto da página.** A extração do DOM é uma função JavaScript executada dentro do browser ([actions.py:59-103](src/browser/actions.py#L59-L103)), não uma travessia feita do lado do Python. Só o JSON final atravessa a ponte.
- **Visível ≠ existente no DOM.** Filtrar por `getBoundingClientRect()` (largura, altura e posição em relação ao `window.innerHeight`) foi a forma de mandar para o modelo só o que está de fato no viewport.
- **Gerar seletores é um problema em cascata.** A regra `#id` → `[name]` → `[aria-label]` → `tag.class` existe porque cada nível é mais frágil que o anterior, e muita página não oferece o nível bom.
- **Seletor CSS vs. localizador semântico.** `page.click(selector)` quebra quando o markup muda; `page.get_by_text()` sobrevive. Por isso o agente tem as duas ações (`click` e `click_text`) e o prompt orienta a preferir a segunda quando o texto é único.
- **Esperas.** `wait_for_selector` (espera uma condição), `wait_for_load_state("domcontentloaded")` (espera o ciclo de vida) e `wait_for_timeout` (dorme). O terceiro é o pior dos três — e ainda está no código em alguns pontos, justamente como lembrete de onde faltou uma condição melhor.
- **Ciclo de vida `sync_playwright() → browser → context → page`.** Foi aqui que ficou claro que viewport e user-agent pertencem ao **context**, não ao browser nem à page ([browser.py:11-27](src/browser/browser.py#L11-L27)) — e que esquecer de fechar os dois vaza processo.
- **Detecção de automação.** `playwright-stealth`, user-agent customizado e viewport fixo: o suficiente para não levar bloqueio imediato em sites simples, longe do suficiente para sites que levam isso a sério.

## Limitações conhecidas

- **DOM truncado em 80 elementos** do viewport atual — páginas longas ou densas ficam mal representadas para o modelo
- **Seletores por classe quebram em SPAs** com classes geradas (CSS-in-JS, Tailwind JIT)
- **Sem testes automatizados**
- **Sem retry estruturado.** Erro de ação vira uma string no histórico e o modelo precisa se recuperar sozinho
- **Teto de 15 iterações** — tarefas mais longas simplesmente não terminam
- **Não lida com iframes, shadow DOM, captcha ou fluxos de login**
- **Custa dinheiro:** uma chamada ao GPT-4o por iteração
- **API síncrona do Playwright**, sem paralelismo
