from flask import Flask
from config import Config
from app.extensions import db, login_manager # Importa as instâncias

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializa as extensões com a aplicação
    db.init_app(app)
    login_manager.init_app(app)

    # --- Configuração do Usuário ---
    from app.models.core import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        # RF01.4: Retorna o objeto Usuario a partir do ID da sessão
        return Usuario.query.get(int(user_id))

    # --- Importa e Registra os Blueprints (MVC Modules) ---
    
    # Global/Institucional (RF10)
    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    # Autenticação (RF01)
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Catálogo e Produtos (RF03)
    from app.blueprints.produtos import produtos_bp
    app.register_blueprint(produtos_bp, url_prefix='/produtos')

    # Gestão de Produtores (RF02)
    from app.blueprints.produtores import produtores_bp
    app.register_blueprint(produtores_bp, url_prefix='/produtores')
    
    # Dashboard Administrativo (RF07)
    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Área do Cliente (RF09)
    from app.blueprints.cliente import cliente_bp
    app.register_blueprint(cliente_bp, url_prefix='/cliente')

    # Cria tabelas no banco (apenas para desenvolvimento)
    with app.app_context():
        db.create_all()

    return app