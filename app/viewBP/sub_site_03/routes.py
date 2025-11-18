from . import pagina03BP


@pagina03BP.route("/")
def index():
    return "Página 03 - Índice"


@pagina03BP.route("/cadastro")
def cadastro():
    return "Página 03 - Cadastro"
