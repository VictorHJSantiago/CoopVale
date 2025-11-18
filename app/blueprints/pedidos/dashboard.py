from flask import render_template
from flask_login import login_required, current_user
from app.models.core import Pedido
from . import pedidos_bp

@pedidos_bp.route('/dashboard')
@login_required
def dashboard_cliente():
    if not hasattr(current_user, 'cliente') or not current_user.cliente:
        return render_template('pedidos/dashboard.html', erro='Apenas clientes têm acesso ao dashboard.')
    cliente = current_user.cliente
    pedidos = Pedido.query.filter_by(cliente_id=cliente.id).all()
    total_pedidos = len(pedidos)
    total_gasto = sum(p.total for p in pedidos)
    return render_template('pedidos/dashboard.html', pedidos=pedidos, total_pedidos=total_pedidos, total_gasto=total_gasto)
