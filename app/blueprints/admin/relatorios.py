from flask import render_template
from flask_login import login_required, current_user
from app.models.core import Pedido, Produto, Produtor
from . import admin_bp

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'admin':
            return render_template('admin/erro.html', erro='Acesso restrito ao administrador.')
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/relatorios')
@login_required
@admin_required
def relatorios():
    produtos_mais_vendidos = Produto.query.order_by(Produto.estoque).limit(5).all()
    produtores = Produtor.query.all()
    pedidos = Pedido.query.all()
    return render_template('admin/relatorios.html', produtos_mais_vendidos=produtos_mais_vendidos, produtores=produtores, pedidos=pedidos)
