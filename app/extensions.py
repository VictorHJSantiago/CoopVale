from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Inicialização do Banco de Dados
db = SQLAlchemy()

# Inicialização do Gerenciador de Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'