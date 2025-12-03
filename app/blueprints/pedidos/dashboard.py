from flask import render_template
from flask_login import login_required, current_user
from app.models.core import Produto, Pedido, ItemPedido
from . import produtores_bp

@produtores_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.produtor_perfil:
        return render_template('produtores/dashboard.html', erro='Apenas produtores têm acesso ao dashboard.')
    
    produtor = current_user.produtor_perfil
    produtos = Produto.query.filter_by(produtor_id=produtor.id).all()
    
    produtos_ids = [p.id for p in produtos]
    
    pedidos = (Pedido.query
        .join(ItemPedido)
        .filter(ItemPedido.produto_id.in_(produtos_ids))
        .distinct()
        .all())
    
    total_vendas = 0
    for pedido in pedidos:
        for item in pedido.itens:
            if item.produto_id in produtos_ids:
                total_vendas += item.quantidade * item.preco_unitario

    return render_template('produtores/dashboard.html', produtos=produtos, pedidos=pedidos, total_vendas=total_vendas)