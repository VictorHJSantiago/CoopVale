from . import pagina02BP


@pagina02BP.route("/")
def index():
    return "Página 02 - Índice"
