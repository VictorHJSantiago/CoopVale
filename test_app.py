import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def test_homepage(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'CoopVale' in resp.data

def test_login_page(client):
    resp = client.get('/auth/login')
    assert resp.status_code == 200
    assert b'Login' in resp.data
# Adicione mais testes para cada rota e fluxo importante

def test_register_and_login(client):
    # Cadastro
    resp = client.post('/auth/register', data={
        'email': 'cliente@teste.com',
        'senha': '123456',
        'tipo_usuario': 'cliente',
        'nome': 'Cliente Teste'
    }, follow_redirects=True)
    assert b'Cadastro realizado' in resp.data
    # Login
    resp = client.post('/auth/login', data={
        'email': 'cliente@teste.com',
        'senha': '123456'
    }, follow_redirects=True)
    assert b'Login realizado' in resp.data or b'Olá, cliente@teste.com' in resp.data

def test_categoria_crud(client, app):
    with app.app_context():
        # Login como admin
        from app.models.core import Usuario
        from werkzeug.security import generate_password_hash
        admin = Usuario(email='admin@teste.com', senha_hash=generate_password_hash('admin123'), tipo_usuario='admin', ativo=True)
        db.session.add(admin)
        db.session.commit()
    client.post('/auth/login', data={'email': 'admin@teste.com', 'senha': 'admin123'}, follow_redirects=True)
    # Criar categoria
    resp = client.post('/produtos/categorias/nova', data={
        'nome': 'Hortifruti',
        'descricao': 'Frutas e verduras',
        'icone': 'fa-apple'
    }, follow_redirects=True)
    assert b'Categoria criada' in resp.data

def test_carrinho_fluxo(client, app):
    with app.app_context():
        from app.models.core import Usuario, Cliente, Categoria, Produto
        from werkzeug.security import generate_password_hash
        user = Usuario(email='cli2@teste.com', senha_hash=generate_password_hash('123456'), tipo_usuario='cliente', ativo=True)
        db.session.add(user)
        db.session.commit()
        cliente = Cliente(usuario_id=user.id, nome='Cliente 2', cpf='000.000.000-00')
        db.session.add(cliente)
        cat = Categoria(nome='Laticínios')
        db.session.add(cat)
        db.session.commit()
        prod = Produto(nome='Leite', preco=5.0, unidade='L', categoria_id=cat.id, estoque=10)
        db.session.add(prod)
        db.session.commit()
    client.post('/auth/login', data={'email': 'cli2@teste.com', 'senha': '123456'}, follow_redirects=True)
    # Adicionar ao carrinho
    resp = client.post(f'/pedidos/carrinho/adicionar/{prod.id}', data={'quantidade': 2}, follow_redirects=True)
    assert b'Produto adicionado' in resp.data
    # Finalizar pedido
    resp = client.post('/pedidos/finalizar', data={'forma_pagamento': 'dinheiro', 'tipo_recebimento': 'retirada'}, follow_redirects=True)
    assert b'Pedido realizado' in resp.data

def test_permissoes(client, app):
    with app.app_context():
        from app.models.core import Usuario
        from werkzeug.security import generate_password_hash
        admin = Usuario(email='admin2@teste.com', senha_hash=generate_password_hash('admin123'), tipo_usuario='admin', ativo=True)
        db.session.add(admin)
        db.session.commit()
    # Não logado
    resp = client.get('/admin/dashboard', follow_redirects=True)
    assert b'Login' in resp.data or b'Acesso restrito' in resp.data
    # Logado como admin
    client.post('/auth/login', data={'email': 'admin2@teste.com', 'senha': 'admin123'}, follow_redirects=True)
    resp = client.get('/admin/dashboard')
    assert b'Dashboard Administrativo' in resp.data
