from flask import Blueprint

produtores_bp = Blueprint('produtores', __name__, template_folder='templates')

from . import routes
from . import dashboard  # Garante que as rotas do dashboard sejam registradas
