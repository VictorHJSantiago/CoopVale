from flask import Blueprint

pagina02BP = Blueprint(
    "site_02",
    __name__,
    template_folder="templates",  # onde estão os HTMLs
    static_folder="static",  # onde estão css/js/imagens específicos
    url_prefix="/site_02",  # prefixo das rotas deste blueprint
)

# importa as rotas após criar o blueprint
from . import (
    routes,
)
