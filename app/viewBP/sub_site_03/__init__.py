from flask import Blueprint

pagina03BP = Blueprint(
    "site_03",
    __name__,
    template_folder="templates",  # onde estão os HTMLs
    static_folder="static",  # onde estão css/js/imagens específicos
    url_prefix="/site_03",
)

# importa as rotas após criar o blueprint
from . import (
    routes,
)
