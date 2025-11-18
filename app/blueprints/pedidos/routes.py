# Detalhe do pedido
@pedidos_bp.route('/pedido/<int:pedido_id>')
@login_required
def detalhe_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    if pedido.cliente.usuario_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pedidos_bp.historico'))
    return render_template('pedidos/detalhe_pedido.html', pedido=pedido)
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import Produto, Pedido, ItemPedido, Cliente
from . import pedidos_bp

# Carrinho de compras (sessão)
@pedidos_bp.route('/carrinho')
@login_required
def carrinho():
    carrinho = session.get('carrinho', {})
    produtos = []
    total = 0
    for produto_id, qtd in carrinho.items():
        produto = Produto.query.get(int(produto_id))
        if produto:
            subtotal = produto.preco * qtd
            produtos.append({'produto': produto, 'quantidade': qtd, 'subtotal': subtotal})
            total += subtotal
    return render_template('pedidos/carrinho.html', produtos=produtos, total=total)

@pedidos_bp.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'])
@login_required
def adicionar_ao_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    qtd = int(request.form.get('quantidade', 1))
    carrinho[str(produto_id)] = carrinho.get(str(produto_id), 0) + qtd
    session['carrinho'] = carrinho
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('pedidos_bp.carrinho'))


# Atualizar quantidade no carrinho
@pedidos_bp.route('/carrinho/atualizar/<int:produto_id>', methods=['POST'])
@login_required
def atualizar_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    qtd = int(request.form.get('quantidade', 1))
    if qtd > 0:
        carrinho[str(produto_id)] = qtd
    else:
        carrinho.pop(str(produto_id), None)
    session['carrinho'] = carrinho
    flash('Quantidade atualizada.', 'info')
    return redirect(url_for('pedidos_bp.carrinho'))

@pedidos_bp.route('/carrinho/remover/<int:produto_id>', methods=['POST'])
@login_required
def remover_do_carrinho(produto_id):
    carrinho = session.get('carrinho', {})
    carrinho.pop(str(produto_id), None)
    session['carrinho'] = carrinho
    flash('Produto removido do carrinho.', 'info')
    return redirect(url_for('pedidos_bp.carrinho'))

# Finalizar pedido
@pedidos_bp.route('/finalizar', methods=['GET', 'POST'])
@login_required
def finalizar_pedido():
    carrinho = session.get('carrinho', {})
    if not carrinho:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('pedidos_bp.carrinho'))
    if request.method == 'POST':
        cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
        if not cliente:
            flash('Perfil de cliente não encontrado.', 'danger')
            return redirect(url_for('pedidos_bp.carrinho'))
        data_agendada = request.form.get('data_agendada')
        observacoes = request.form.get('observacoes')
        pedido = Pedido(
            cliente_id=cliente.id,
            status='Aguardando confirmação',
            forma_pagamento=request.form['forma_pagamento'],
            tipo_recebimento=request.form['tipo_recebimento'],
            total=0,
            data_agendada=data_agendada,
            observacoes=observacoes
        )
        db.session.add(pedido)
        total = 0
        for produto_id, qtd in carrinho.items():
            produto = Produto.query.get(int(produto_id))
            if produto:
                item = ItemPedido(
                    pedido=pedido,
                    produto=produto,
                    quantidade=qtd,
                    preco_unitario=produto.preco
                )
                db.session.add(item)
                total += produto.preco * qtd
                produto.estoque -= qtd
        pedido.total = total
        db.session.commit()
        session['carrinho'] = {}
        flash('Pedido realizado com sucesso!', 'success')
        return redirect(url_for('pedidos_bp.historico'))
    return render_template('pedidos/finalizar.html')

# Histórico de pedidos do cliente
@pedidos_bp.route('/historico')
@login_required
def historico():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    pedidos = Pedido.query.filter_by(cliente_id=cliente.id).order_by(Pedido.data.desc()).all() if cliente else []
    return render_template('pedidos/historico.html', pedidos=pedidos)
