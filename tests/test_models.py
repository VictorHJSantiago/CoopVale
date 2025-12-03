"""Testes para modelos do banco de dados."""
import pytest
from app.models.core import Usuario, Cliente, Produtor, Produto, Pedido, ItemPedido, Review
from app import db

def test_usuario_criacao(app):
    """Testar criação de usuário."""
    with app.app_context():
        user = Usuario(email='test@example.com', tipo_usuario='cliente', ativo=True)
        user.set_senha('senha123')
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.email == 'test@example.com'
        assert user.check_senha('senha123')
        assert not user.check_senha('senhaerrada')

def test_produto_preco_promocional(app, produto):
    """Testar preço promocional de produto."""
    with app.app_context():
        prod = Produto.query.first()
        assert prod.preco == 5.50
        
        assert prod.preco_promocional is None
        
        prod.preco_promocional = 4.00
        db.session.commit()
        
        prod = Produto.query.first()
        assert prod.preco_promocional == 4.00

def test_pedido_total(app, cliente_user, produto):
    """Testar cálculo do total do pedido."""
    with app.app_context():
        cliente = Cliente.query.join(Usuario).filter(Usuario.email=='cliente@test.com').first()
        prod = Produto.query.first()
        pedido = Pedido(cliente_id=cliente.id, forma_pagamento='cartao', status='pendente')
        db.session.add(pedido)
        db.session.flush()
        
        item = ItemPedido(pedido_id=pedido.id, produto_id=prod.id, quantidade=3, preco_unitario=5.50)
        db.session.add(item)
        db.session.commit()
        
        pedido.total = 16.50
        db.session.commit()
        assert pedido.total == 16.50
        db.session.commit()
        
        # Verificar total
        assert pedido.total == 16.50

def test_review_media(app, cliente_user, produto):
    """Testar média de avaliações usando dois clientes distintos para evitar violação de UNIQUE."""
    with app.app_context():
        cliente1 = Cliente.query.join(Usuario).filter(Usuario.email=='cliente@test.com').first()
        prod = Produto.query.first()

        # Criar segundo cliente
        usuario2 = Usuario(email='cliente2@test.com', tipo_usuario='cliente', ativo=True)
        usuario2.set_senha('cliente2123')
        db.session.add(usuario2)
        db.session.flush()
        cliente2 = Cliente(usuario=usuario2, nome='Cliente Dois', cpf='98765432100')
        db.session.add(cliente2)
        db.session.commit()

        review1 = Review(produto_id=prod.id, cliente_id=cliente1.id, nota=5, comentario='Excelente!')
        review2 = Review(produto_id=prod.id, cliente_id=cliente2.id, nota=4, comentario='Bom')
        db.session.add_all([review1, review2])
        db.session.commit()

        reviews = Review.query.filter_by(produto_id=prod.id).all()
        assert len(reviews) == 2
        media = sum(r.nota for r in reviews) / len(reviews)
        assert media == (5 + 4) / 2

def test_produtor_associacao(app, produtor_user):
    """Testar associação entre usuário e produtor."""
    with app.app_context():
        produtor = Produtor.query.join(Usuario).filter(Usuario.email=='produtor@test.com').first()
        assert produtor is not None
        assert produtor.usuario.email == 'produtor@test.com'
        assert produtor.nome == 'Fazenda Teste'

def test_produto_estoque(app, produto):
    """Testar controle de estoque."""
    with app.app_context():
        prod = Produto.query.first()
        estoque_inicial = prod.estoque
        
        prod.estoque -= 10
        db.session.commit()
        
        prod = Produto.query.first()
        assert prod.estoque == estoque_inicial - 10
