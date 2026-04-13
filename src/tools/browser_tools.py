from langchain.tools import tool
from src.browser.actions import BrowserActions

def create_browser_tools(actions: BrowserActions):

    @tool
    def navigate(url: str) -> str:
        """Navega para uma URL. Use quando precisar ir para um site específico."""
        return actions.navigate(url)

    @tool
    def click(coordinates: str) -> str:
        """Clica em uma coordenada da tela no formato 'x,y'. 
        Exemplo: '640,360' para clicar no centro da tela 1280x720."""
        try:
            x, y = map(int, coordinates.split(","))
            return actions.click(x, y)
        except ValueError:
            return "Erro: coordenadas inválidas. Use o formato 'x,y'. Exemplo: '640,360'"

    @tool
    def type_text(text: str) -> str:
        """Digita um texto na posição atual do cursor.
        Use após clicar em um campo de input."""
        return actions.type_text(text)

    @tool
    def press_key(key: str) -> str:
        """Pressiona uma tecla do teclado.
        Teclas disponíveis: Enter, Escape, Tab, Backspace, ArrowUp, ArrowDown."""
        return actions.press_key(key)

    @tool
    def scroll(direction: str) -> str:
        """Rola a página para cima ou para baixo.
        Use 'down' para rolar para baixo e 'up' para rolar para cima."""
        return actions.scroll(direction)

    @tool
    def wait(milliseconds: str) -> str:
        """Aguarda um tempo em milissegundos antes da próxima ação.
        Use quando precisar esperar um elemento carregar."""
        return actions.wait(int(milliseconds))

    @tool
    def get_current_url(placeholder: str = "") -> str:
        """Retorna a URL atual da página."""
        return actions.get_current_url()

    @tool
    def get_page_title(placeholder: str = "") -> str:
        """Retorna o título da página atual."""
        return actions.get_page_title()

    return [
        navigate,
        click,
        type_text,
        press_key,
        scroll,
        wait,
        get_current_url,
        get_page_title,
    ]