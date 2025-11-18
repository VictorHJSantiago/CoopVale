from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import Usuario, Produtor, Cliente, Produto, Pedido, ItemPedido
from . import admin_bp

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'admin':
            flash('Acesso restrito ao administrador.', 'danger')
            return redirect(url_for('main_bp.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    from sqlalchemy import func
    from datetime import datetime, timedelta
    total_produtores = Produtor.query.count()
    total_clientes = Cliente.query.count()
    total_produtos = Produto.query.count()
    total_pedidos = Pedido.query.count()
    pedidos_pendentes = Pedido.query.filter(Pedido.status=='Aguardando confirmação').count()

    # Visão geral de vendas
    hoje = datetime.utcnow().date()
    vendas_diario = db.session.query(func.sum(Pedido.total)).filter(func.date(Pedido.data)==hoje).scalar() or 0
    vendas_semana = db.session.query(func.sum(Pedido.total)).filter(Pedido.data >= hoje - timedelta(days=7)).scalar() or 0
    vendas_mes = db.session.query(func.sum(Pedido.total)).filter(Pedido.data >= hoje - timedelta(days=30)).scalar() or 0

    # Produtos mais vendidos
    mais_vendidos = db.session.query(
        Produto.nome, func.sum(ItemPedido.quantidade).label('qtd')
    ).join(ItemPedido).group_by(Produto.id).order_by(func.sum(ItemPedido.quantidade).desc()).limit(5).all()

    # Desempenho por produtor
    desempenho_produtores = db.session.query(
        Produtor.nome, func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).label('faturamento')
    ).join(Produto).join(ItemPedido).group_by(Produtor.id).order_by(func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).desc()).limit(5).all()

    # Faturamento por categoria
    from app.models.core import Categoria
    faturamento_categorias = db.session.query(
        Categoria.nome, func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).label('faturamento')
    ).join(Produto, Produto.categoria_id==Categoria.id).join(ItemPedido).group_by(Categoria.id).all()

    return render_template('admin/dashboard.html',
        total_produtores=total_produtores,
        total_clientes=total_clientes,
        total_produtos=total_produtos,
        total_pedidos=total_pedidos,
        pedidos_pendentes=pedidos_pendentes,
        vendas_diario=vendas_diario,
        vendas_semana=vendas_semana,
        vendas_mes=vendas_mes,
        mais_vendidos=mais_vendidos,
        desempenho_produtores=desempenho_produtores,
        faturamento_categorias=faturamento_categorias)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/usuarios/<int:id>/ativar', methods=['POST'])
@login_required
@admin_required
def ativar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = True
    db.session.commit()
    flash('Usuário ativado.', 'success')
    return redirect(url_for('admin_bp.usuarios'))

@admin_bp.route('/usuarios/<int:id>/desativar', methods=['POST'])
@login_required
@admin_required
def desativar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = False
    db.session.commit()
    flash('Usuário desativado.', 'warning')
    return redirect(url_for('admin_bp.usuarios'))
