from flask import Blueprint
produtos_bp = Blueprint('produtos_bp', __name__, url_prefix='/produtos', template_folder='templates')
from . import routes