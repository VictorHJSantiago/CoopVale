from app.models.core import Pedido, ItemPedido
# Rotas para recompra rápida
@cliente_bp.route('/recompras')
@login_required
def recompras():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    pedidos = Pedido.query.filter_by(cliente_id=cliente.id).order_by(Pedido.data.desc()).all() if cliente else []
    return render_template('cliente/recompras.html', pedidos=pedidos)

@cliente_bp.route('/recomprar/<int:pedido_id>', methods=['POST'])
@login_required
def recomprar(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    # Simular adicionar itens do pedido ao carrinho (session['carrinho'])
    carrinho = {}
    for item in pedido.itens:
        carrinho[str(item.produto_id)] = {'quantidade': item.quantidade}
    # Salvar no session
    from flask import session
    session['carrinho'] = carrinho
    flash('Itens do pedido adicionados ao carrinho para recompra!', 'success')
    return redirect(url_for('pedidos_bp.carrinho'))
from app.models.core import Notificacao
# Rotas para notificações do cliente
@cliente_bp.route('/notificacoes')
@login_required
def notificacoes():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    notificacoes = Notificacao.query.filter_by(cliente_id=cliente.id).order_by(Notificacao.criada_em.desc()).all() if cliente else []
    return render_template('cliente/notificacoes.html', notificacoes=notificacoes)

@cliente_bp.route('/notificacoes/ler/<int:notificacao_id>', methods=['POST'])
@login_required
def ler_notificacao(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    notificacao.lida = True
    db.session.commit()
    return redirect(url_for('cliente_bp.notificacoes'))

@cliente_bp.route('/notificacoes/excluir/<int:notificacao_id>', methods=['POST'])
@login_required
def excluir_notificacao(notificacao_id):
    notificacao = Notificacao.query.get_or_404(notificacao_id)
    db.session.delete(notificacao)
    db.session.commit()
    flash('Notificação excluída.', 'info')
    return redirect(url_for('cliente_bp.notificacoes'))
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import Cliente, Produto, Favorito, Endereco

# Rotas para endereços salvos do cliente
@cliente_bp.route('/enderecos')
@login_required
def enderecos():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    enderecos = Endereco.query.filter_by(cliente_id=cliente.id).all() if cliente else []
    return render_template('cliente/enderecos.html', enderecos=enderecos)

@cliente_bp.route('/enderecos/novo', methods=['GET', 'POST'])
@login_required
def novo_endereco():
    if request.method == 'POST':
        cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
        if not cliente:
            flash('Perfil de cliente não encontrado.', 'danger')
            return redirect(url_for('cliente_bp.enderecos'))
        apelido = request.form.get('apelido')
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')
        principal = bool(request.form.get('principal'))
        if principal:
            # Desmarcar outros endereços principais
            Endereco.query.filter_by(cliente_id=cliente.id, principal=True).update({'principal': False})
        endereco = Endereco(
            cliente_id=cliente.id,
            apelido=apelido,
            logradouro=logradouro,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep,
            principal=principal
        )
        db.session.add(endereco)
        db.session.commit()
        flash('Endereço salvo com sucesso!', 'success')
        return redirect(url_for('cliente_bp.enderecos'))
    return render_template('cliente/endereco_form.html', endereco=None)

@cliente_bp.route('/enderecos/editar/<int:endereco_id>', methods=['GET', 'POST'])
@login_required
def editar_endereco(endereco_id):
    endereco = Endereco.query.get_or_404(endereco_id)
    if request.method == 'POST':
        apelido = request.form.get('apelido')
        logradouro = request.form.get('logradouro')
        numero = request.form.get('numero')
        complemento = request.form.get('complemento')
        bairro = request.form.get('bairro')
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        cep = request.form.get('cep')
        principal = bool(request.form.get('principal'))
        if principal:
            Endereco.query.filter_by(cliente_id=endereco.cliente_id, principal=True).update({'principal': False})
        endereco.apelido = apelido
        endereco.logradouro = logradouro
        endereco.numero = numero
        endereco.complemento = complemento
        endereco.bairro = bairro
        endereco.cidade = cidade
        endereco.estado = estado
        endereco.cep = cep
        endereco.principal = principal
        db.session.commit()
        flash('Endereço atualizado com sucesso!', 'success')
        return redirect(url_for('cliente_bp.enderecos'))
    return render_template('cliente/endereco_form.html', endereco=endereco)

@cliente_bp.route('/enderecos/excluir/<int:endereco_id>', methods=['POST'])
@login_required
def excluir_endereco(endereco_id):
    endereco = Endereco.query.get_or_404(endereco_id)
    db.session.delete(endereco)
    db.session.commit()
    flash('Endereço removido com sucesso.', 'info')
    return redirect(url_for('cliente_bp.enderecos'))
from . import cliente_bp

@cliente_bp.route('/favoritos')
@login_required
def favoritos():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    favoritos = Favorito.query.filter_by(cliente_id=cliente.id).all() if cliente else []
    produtos = [Produto.query.get(fav.produto_id) for fav in favoritos]
    return render_template('cliente/favoritos.html', produtos=produtos)

@cliente_bp.route('/favoritos/adicionar/<int:produto_id>', methods=['POST'])
@login_required
def adicionar_favorito(produto_id):
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    if not cliente:
        flash('Perfil de cliente não encontrado.', 'danger')
        return redirect(url_for('produtos_bp.catalogo'))
    if not Favorito.query.filter_by(cliente_id=cliente.id, produto_id=produto_id).first():
        fav = Favorito(cliente_id=cliente.id, produto_id=produto_id)
        db.session.add(fav)
        db.session.commit()
        flash('Adicionado aos favoritos!', 'success')
    return redirect(request.referrer or url_for('produtos_bp.catalogo'))

@cliente_bp.route('/favoritos/remover/<int:produto_id>', methods=['POST'])
@login_required
def remover_favorito(produto_id):
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    fav = Favorito.query.filter_by(cliente_id=cliente.id, produto_id=produto_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        flash('Removido dos favoritos.', 'info')
    return redirect(request.referrer or url_for('cliente_bp.favoritos'))
