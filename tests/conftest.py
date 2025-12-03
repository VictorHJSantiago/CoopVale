import pytest
from app import create_app, db
from app.models.core import Usuario, Cliente, Produtor, Categoria, Produto

@pytest.fixture(scope='function')
def app():
    """Criar aplicação Flask para testes."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        db.create_all()
        
        # Seed minimal data for all tests - verificar se já existe antes de criar
        if not Categoria.query.filter_by(nome='Verduras').first():
            cat = Categoria(nome='Verduras', descricao='Verduras orgânicas', valor_minimo=10.0, quantidade_minima=2)
            db.session.add(cat)
            db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Cliente de teste para fazer requisições."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner para comandos CLI."""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Criar usuário administrador."""
    with app.app_context():
        user = Usuario(email='admin@test.com', tipo_usuario='admin', ativo=True)
        user.set_senha('admin123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def cliente_user(app):
    """Criar usuário cliente."""
    with app.app_context():
        user = Usuario(email='cliente@test.com', tipo_usuario='cliente', ativo=True)
        user.set_senha('cliente123')
        db.session.add(user)
        db.session.flush()
        
        cliente = Cliente(usuario=user, nome='Cliente Teste', cpf='12345678900')
        db.session.add(cliente)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def produtor_user(app):
    """Criar usuário produtor."""
    with app.app_context():
        user = Usuario(email='produtor@test.com', tipo_usuario='produtor', ativo=True)
        user.set_senha('produtor123')
        db.session.add(user)
        db.session.flush()
        
        produtor = Produtor(usuario=user, nome='Fazenda Teste', cpf='111.222.333-44', descricao='Produtor de orgânicos')
        db.session.add(produtor)
        db.session.commit()
        db.session.refresh(user)
        return user

@pytest.fixture
def categoria(app):
    """Retornar categoria já criada no app fixture."""
    with app.app_context():
        return Categoria.query.filter_by(nome='Verduras').first()

@pytest.fixture
def produto(app, produtor_user):
    """Criar produto de teste."""
    with app.app_context():
        produtor = Produtor.query.first()
        cat = Categoria.query.filter_by(nome='Verduras').first()
        prod = Produto(
            nome='Alface Orgânica',
            descricao='Alface fresca',
            preco=5.50,
            estoque=50,
            produtor_id=produtor.id,
            categoria_id=cat.id,
            tags='organico'
        )
        db.session.add(prod)
        db.session.commit()
        db.session.refresh(prod)
        return prod
