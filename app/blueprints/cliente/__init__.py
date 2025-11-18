from flask import Blueprint

cliente_bp = Blueprint('cliente_bp', __name__, template_folder='templates')

from . import routes
