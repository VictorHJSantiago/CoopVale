from flask import Blueprint

blog_bp = Blueprint('blog', __name__, template_folder='templates', url_prefix='/blog')

from . import routes
