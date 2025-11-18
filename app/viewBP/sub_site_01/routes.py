from . import pagina01BP


@pagina01BP.route("/")
def index():
    return "Exemplo de site com BP - 01 - Home"


@pagina01BP.route("/cadastro")
def cadastro():
    return "Exemplo de site com BP - 01 - Cadastro"


@pagina01BP.route("/login")
def login():
    return "Exemplo de site com BP - 01 - Login"
