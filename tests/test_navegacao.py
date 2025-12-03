import pytest
from app import create_app
from app.extensions import db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


@pytest.fixture()
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def seed_minimo(app):
    from app.models.core import Usuario, Produtor, Produto, Categoria
    with app.app_context():
        cat = Categoria(nome='Geral', descricao='Teste', icone='box')
        db.session.add(cat)
        db.session.commit()

        usuario = Usuario(email='produtor_teste@example.com', tipo_usuario='produtor')
        usuario.set_senha('teste123')
        # Vincula produtor via relação para garantir usuario_id populado
        usuario.produtor_perfil = Produtor(
            nome='Produtor Teste',
            cpf='00000000000',
            telefone='(00) 0000-0000',
            endereco='Rua A, 123',
            certificacoes='Orgânico',
            descricao='Produtor de testes'
        )
        db.session.add(usuario)
        db.session.commit()

        produtor = usuario.produtor_perfil

        produto = Produto(nome='Produto Teste', descricao='Desc', preco=10.0, unidade='kg', categoria_id=cat.id, estoque=5, imagens='', tags='orgânico', produtor_id=produtor.id)
        db.session.add(produto)
        db.session.commit()
        return produtor.id, produto.id


def test_catalogo_status_ok(client, app):
    seed_minimo(app)
    resp = client.get('/produtos/')
    assert resp.status_code == 200
    # Deve conter placeholder quando produto não tem imagem
    assert b'images/placeholders/produto.svg' in resp.data


def test_perfil_publico_status_ok(client, app):
    produtor_id, _ = seed_minimo(app)
    resp = client.get(f'/produtores/produtores/{produtor_id}')
    assert resp.status_code == 200
    # Deve conter placeholder do produtor quando não houver foto
    assert b'images/placeholders/produtor.svg' in resp.data


def test_detalhe_produto_status_ok(client, app):
    _, produto_id = seed_minimo(app)
    resp = client.get(f'/produtos/detalhe/{produto_id}')
    assert resp.status_code == 200
    # Página de detalhe deve carregar sem erro
    assert b'Produto' in resp.data or b'produtos' in resp.data.lower()
