from flask import render_template
from flask_login import login_required, current_user
from app.models.core import Produto, Pedido, ItemPedido
from . import produtores_bp

@produtores_bp.route('/dashboard')
@login_required
def dashboard():
    if not hasattr(current_user, 'produtor') or not current_user.produtor:
        return render_template('produtores/dashboard.html', erro='Apenas produtores têm acesso ao dashboard.')
    produtor = current_user.produtor
    produtos = Produto.query.filter_by(produtor_id=produtor.id).all()
    pedidos = (Pedido.query
        .join(ItemPedido)
        .filter(ItemPedido.produto_id.in_([p.id for p in produtos]))
        .all())
    total_vendas = sum(item.preco_unitario * item.quantidade for p in pedidos for item in p.itens if item.produto.produtor_id == produtor.id)
    return render_template('produtores/dashboard.html', produtos=produtos, pedidos=pedidos, total_vendas=total_vendas)
