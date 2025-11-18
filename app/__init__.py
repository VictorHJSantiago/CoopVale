from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Inicializa as extensões
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)

    # Importa e registra os Blueprints
    # Certifique-se que as pastas 'main' e 'auth' existem em app/blueprints/
    # Se ainda não criou as pastas, comente as linhas abaixo temporariamente
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Configura o carregamento do usuário
    # Certifique-se que app/models.py existe
    from app.models import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Cria tabelas no banco (apenas para desenvolvimento)
    with app.app_context():
        db.create_all()

    return app