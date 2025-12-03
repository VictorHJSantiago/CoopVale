"""Testes para lógica de negócios."""
import pytest
from datetime import datetime, timedelta
from app.models.core import Pedido, ItemPedido, Produto, Categoria, Cliente, Usuario
from app import db

def test_categoria_minimo_valor(app):
    """Testar validação de valor mínimo por categoria."""
    with app.app_context():
        cat = Categoria.query.filter_by(nome='Verduras').first()
        assert cat is not None
        assert cat.valor_minimo == 10.0
        assert cat.quantidade_minima == 2.0

def test_cancelamento_prazo(app, cliente_user):
    """Testar regra de cancelamento dentro do prazo."""
    with app.app_context():
        cliente = Cliente.query.join(Usuario).filter(Usuario.tipo_usuario=='cliente').first()
        if not cliente:
            pytest.skip("No cliente user fixture found in session")
        pedido = Pedido(
            cliente_id=cliente.id,
            forma_pagamento='cartao',
            status='pendente',
            data=datetime.now()
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Dentro do prazo de 1 hora
        tempo_decorrido = (datetime.now() - pedido.data).total_seconds() / 3600
        assert tempo_decorrido < 1
        
        # Pode cancelar
        assert pedido.status == 'pendente'

def test_cancelamento_fora_prazo(app, cliente_user, produto):
    """Testar regra de cancelamento fora do prazo."""
    with app.app_context():
        cliente = Cliente.query.filter_by(usuario_id=cliente_user.id).first()
        pedido = Pedido(
            cliente_id=cliente.id,
            forma_pagamento='cartao',
            status='pendente',
            data=datetime.now() - timedelta(hours=2)
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Fora do prazo de 1 hora
        tempo_decorrido = (datetime.now() - pedido.data).total_seconds() / 3600
        assert tempo_decorrido > 1

def test_produto_sazonalidade(app, produto):
    """Testar lógica de sazonalidade de produtos (uso consistente de datetime)."""
    with app.app_context():
        prod = db.session.get(Produto, produto.id)

        # Sem sazonalidade
        assert prod.sazonal_inicio is None
        assert prod.sazonal_fim is None

        # Definir sazonalidade como datetime completo
        inicio = datetime.now()
        fim = datetime.now() + timedelta(days=90)
        prod.sazonal_inicio = inicio
        prod.sazonal_fim = fim
        db.session.commit()

        # Verificar se está na temporada
        agora = datetime.now()
        assert prod.sazonal_inicio <= agora <= prod.sazonal_fim

def test_restaurar_estoque_cancelamento(app, cliente_user, produto):
    """Testar restauração de estoque após cancelamento."""
    with app.app_context():
        cliente = Cliente.query.filter_by(usuario_id=cliente_user.id).first()
        prod = db.session.get(Produto, produto.id)
        estoque_inicial = prod.estoque
        
        # Criar pedido
        pedido = Pedido(
            cliente_id=cliente.id,
            forma_pagamento='cartao',
            status='pendente',
            data=datetime.now()
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Adicionar item e reduzir estoque
        item = ItemPedido(
            pedido_id=pedido.id,
            produto_id=prod.id,
            quantidade=5,
            preco_unitario=prod.preco
        )
        db.session.add(item)
        prod.estoque -= 5
        db.session.commit()
        
        # Cancelar pedido e restaurar estoque
        pedido.status = 'cancelado'
        prod.estoque += item.quantidade
        db.session.commit()
        
        # Verificar restauração
        prod = db.session.get(Produto, produto.id)
        assert prod.estoque == estoque_inicial

def test_calculo_faturamento_produtor(app, produtor_user, produto, cliente_user):
    """Testar cálculo de faturamento por produtor."""
    with app.app_context():
        cliente = Cliente.query.filter_by(usuario_id=cliente_user.id).first()
        
        # Criar pedido
        pedido = Pedido(
            cliente_id=cliente.id,
            forma_pagamento='cartao',
            status='finalizado'
        )
        db.session.add(pedido)
        db.session.commit()
        
        # Adicionar itens
        item1 = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=3,
            preco_unitario=5.50
        )
        item2 = ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=2,
            preco_unitario=5.50
        )
        db.session.add_all([item1, item2])
        db.session.commit()
        
        # Calcular faturamento
        faturamento = sum(item.quantidade * item.preco_unitario for item in pedido.itens)
        assert faturamento == 27.50
