from flask import Flask
from config import Config
from app.extensions import db, login_manager, migrate, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from app.models.core import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    from app.blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.blueprints.produtos import produtos_bp
    app.register_blueprint(produtos_bp, url_prefix='/produtos')

    from app.blueprints.produtores import produtores_bp
    app.register_blueprint(produtores_bp, url_prefix='/produtores')

    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.blueprints.cliente import cliente_bp
    app.register_blueprint(cliente_bp, url_prefix='/cliente')

    from app.blueprints.pedidos import pedidos_bp
    app.register_blueprint(pedidos_bp, url_prefix='/pedidos')

    # Remover db.create_all() para usar migrações

    return app