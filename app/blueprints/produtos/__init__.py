from flask import Blueprint

produtos_bp = Blueprint('produtos', __name__, url_prefix='/produtos', template_folder='templates')

from . import routes