from flask import render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_required, current_user
from datetime import datetime
from app.extensions import db
from app.models.core import Produto, Pedido, ItemPedido, Cliente, PontoRetirada, TaxaEntrega
from . import pedidos_bp
import io
import base64
import hashlib

@pedidos_bp.route('/carrinho', endpoint='carrinho')
@login_required
def carrinho():
    carrinho_session = session.get('carrinho', {})
    produtos = []
    total = 0
    for produto_id, qtd in carrinho_session.items():
        produto = db.session.get(Produto, int(produto_id))
        if produto:
            subtotal = produto.preco * qtd
            produtos.append({'produto': produto, 'quantidade': qtd, 'subtotal': subtotal})
            total += subtotal
    return render_template('pedidos/carrinho.html', produtos=produtos, total=total)

@pedidos_bp.route('/carrinho/adicionar/<int:produto_id>', methods=['POST'], endpoint='carrinho_adicionar')
@login_required
def adicionar_ao_carrinho(produto_id):
    carrinho_session = session.get('carrinho', {})
    qtd = int(request.form.get('quantidade', 1))
    carrinho_session[str(produto_id)] = carrinho_session.get(str(produto_id), 0) + qtd
    session['carrinho'] = carrinho_session
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('pedidos.carrinho'))

# Alias para compatibilidade com testes que esperam /pedidos/adicionar-carrinho/<id>
@pedidos_bp.route('/adicionar-carrinho/<int:produto_id>', methods=['POST'], endpoint='adicionar_carrinho')
@login_required
def adicionar_carrinho_alias(produto_id):
    return adicionar_ao_carrinho(produto_id)

@pedidos_bp.route('/carrinho/atualizar/<int:produto_id>', methods=['POST'], endpoint='carrinho_atualizar')
@login_required
def atualizar_carrinho(produto_id):
    carrinho_session = session.get('carrinho', {})
    qtd = int(request.form.get('quantidade', 1))
    if qtd > 0:
        carrinho_session[str(produto_id)] = qtd
    else:
        carrinho_session.pop(str(produto_id), None)
    session['carrinho'] = carrinho_session
    flash('Quantidade atualizada.', 'info')
    return redirect(url_for('pedidos.carrinho'))

@pedidos_bp.route('/carrinho/remover/<int:produto_id>', methods=['POST'], endpoint='carrinho_remover')
@login_required
def remover_do_carrinho(produto_id):
    carrinho_session = session.get('carrinho', {})
    carrinho_session.pop(str(produto_id), None)
    session['carrinho'] = carrinho_session
    flash('Produto removido do carrinho.', 'info')
    return redirect(url_for('pedidos.carrinho'))

@pedidos_bp.route('/finalizar', methods=['GET', 'POST'], endpoint='finalizar_pedido')
@login_required
def finalizar_pedido():
    carrinho_session = session.get('carrinho', {})
    if not carrinho_session:
        flash('Carrinho vazio.', 'warning')
        return redirect(url_for('pedidos.carrinho'))
        
    pontos_retirada = PontoRetirada.query.filter_by(ativo=True).all()
    taxas_entrega = TaxaEntrega.query.filter_by(ativo=True).all()
    
    if request.method == 'POST':
        cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
        if not cliente:
            flash('Perfil de cliente não encontrado.', 'danger')
            return redirect(url_for('pedidos.carrinho'))
            
        data_str = request.form.get('data_agendada')
        data_agendada = datetime.strptime(data_str, '%Y-%m-%d') if data_str else None
        
        # Validação de mínimos por categoria
        from app.models.core import Categoria
        agregados = {}
        for produto_id, qtd in carrinho_session.items():
            produto = db.session.get(Produto, int(produto_id))
            if not produto:
                continue
            cat_id = produto.categoria_id
            valor = produto.preco * qtd
            agregados.setdefault(cat_id, {'valor':0,'quantidade':0})
            agregados[cat_id]['valor'] += valor
            agregados[cat_id]['quantidade'] += qtd
        categorias_invalidas = []
        for cat_id, dados in agregados.items():
            categoria = db.session.get(Categoria, cat_id)
            if categoria:
                if categoria.valor_minimo and dados['valor'] < categoria.valor_minimo:
                    categorias_invalidas.append(f"{categoria.nome} valor mínimo R$ {categoria.valor_minimo:.2f}")
                if categoria.quantidade_minima and dados['quantidade'] < categoria.quantidade_minima:
                    categorias_invalidas.append(f"{categoria.nome} quantidade mínima {categoria.quantidade_minima}")
        if categorias_invalidas:
            flash('Requisitos mínimos não atendidos: ' + '; '.join(categorias_invalidas), 'warning')
            return redirect(url_for('pedidos.carrinho'))

        pedido = Pedido(
            cliente_id=cliente.id,
            status='Aguardando confirmação',
            forma_pagamento=request.form['forma_pagamento'],
            tipo_recebimento=request.form['tipo_recebimento'],
            total=0,
            data_agendada=data_agendada,
            observacoes=request.form.get('observacoes')
        )
        db.session.add(pedido)
        # Logística: retirada ou entrega
        entrega_tipo = request.form.get('tipo_recebimento')
        pedido.entrega_tipo = entrega_tipo
        frete = 0.0
        if entrega_tipo == 'retirada':
            pr_id = request.form.get('ponto_retirada_id')
            if not pr_id:
                flash('Selecione um ponto de retirada.', 'warning')
                return redirect(url_for('pedidos.finalizar_pedido'))
            pedido.ponto_retirada_id = int(pr_id)
        elif entrega_tipo == 'entrega':
            taxa_id = request.form.get('taxa_entrega_id')
            if not taxa_id:
                flash('Selecione a região de entrega.', 'warning')
                return redirect(url_for('pedidos.finalizar_pedido'))
            taxa = db.session.get(TaxaEntrega, int(taxa_id))
            if not taxa or not taxa.ativo:
                flash('Taxa de entrega inválida.', 'danger')
                return redirect(url_for('pedidos.finalizar_pedido'))
            pedido.taxa_entrega_id = taxa.id
            frete = float(taxa.valor or 0)
            # CEP opcional: validação de formato e inclusão nas observações
            cep_info = (request.form.get('cep') or '').strip()
            if cep_info:
                import re
                if not re.fullmatch(r"\d{5}-?\d{3}", cep_info):
                    flash('CEP inválido. Use o formato 12345-678.', 'warning')
                    return redirect(url_for('pedidos.finalizar_pedido'))
                # normaliza para 12345-678
                somente_numeros = re.sub(r"[^0-9]", "", cep_info)
                cep_info = f"{somente_numeros[:5]}-{somente_numeros[5:]}"
                obs = pedido.observacoes + f" | CEP entrega: {cep_info}" if pedido.observacoes else f"CEP entrega: {cep_info}"
                pedido.observacoes = obs
            # Endereço detalhado opcional
            rua = (request.form.get('endereco_rua') or '').strip()
            bairro = (request.form.get('endereco_bairro') or '').strip()
            cidade = (request.form.get('endereco_cidade') or '').strip()
            uf = (request.form.get('endereco_uf') or '').strip().upper()
            numero = (request.form.get('endereco_numero') or '').strip()
            detalhes = []
            if rua: detalhes.append(f"Rua: {rua}")
            if numero: detalhes.append(f"Nº: {numero}")
            if bairro: detalhes.append(f"Bairro: {bairro}")
            if cidade: detalhes.append(f"Cidade: {cidade}")
            if uf: detalhes.append(f"UF: {uf}")
            if detalhes:
                extra = ' | ' + ' '.join(detalhes)
                pedido.observacoes = (pedido.observacoes or '') + extra
        
        total = 0
        for produto_id, qtd in carrinho_session.items():
            produto = db.session.get(Produto, int(produto_id))
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
        
        pedido.valor_frete = frete
        pedido.total = total + frete
        
        # Armazenar dados do pagamento
        forma_pgto = request.form['forma_pagamento']
        if forma_pgto in ['cartao_credito', 'cartao_debito']:
            # Armazenar dados do cartão (em produção: criptografar ou usar tokenização)
            numero_cartao = request.form.get('numero_cartao', '')
            nome_cartao = request.form.get('nome_cartao', '')
            validade_cartao = request.form.get('validade_cartao', '')
            cvv_cartao = request.form.get('cvv_cartao', '')
            # Adicionar nas observações (apenas para demonstração - NÃO FAZER EM PRODUÇÃO!)
            mascara_cartao = '**** **** **** ' + numero_cartao.replace(' ', '')[-4:]
            obs_cartao = f" | Cartão: {mascara_cartao}, Nome: {nome_cartao}, Validade: {validade_cartao}"
            pedido.observacoes = (pedido.observacoes or '') + obs_cartao
        
        db.session.commit()
        session['carrinho'] = {}
        
        # Se for PIX, redirecionar para página de pagamento
        if forma_pgto == 'pix':
            return redirect(url_for('pedidos.pagamento_pix', pedido_id=pedido.id))
        
        flash('Pedido realizado com sucesso!', 'success')
        return redirect(url_for('pedidos.historico'))
        
    # calcular subtotal para exibição
    subtotal = 0
    for produto_id, qtd in carrinho_session.items():
        produto = db.session.get(Produto, int(produto_id))
        if produto:
            subtotal += produto.preco * qtd
    return render_template('pedidos/finalizar.html', pontos_retirada=pontos_retirada, taxas_entrega=taxas_entrega, subtotal=subtotal)

# ===== Gestão de Ponto de Retirada =====
@pedidos_bp.route('/pontos-retirada', endpoint='listar_pontos')
@login_required
def listar_pontos():
    pontos = PontoRetirada.query.order_by(PontoRetirada.nome.asc()).all()
    return render_template('pedidos/pontos_retirada_list.html', pontos=pontos)

@pedidos_bp.route('/pontos-retirada/novo', methods=['GET','POST'], endpoint='novo_ponto')
@login_required
def novo_ponto():
    if request.method == 'POST':
        ponto = PontoRetirada(
            nome=request.form['nome'],
            endereco=request.form['endereco'],
            cidade=request.form.get('cidade'),
            cep=request.form.get('cep'),
            dias_funcionamento=request.form.get('dias_funcionamento'),
            horario_abertura=request.form.get('horario_abertura'),
            horario_fechamento=request.form.get('horario_fechamento'),
            ativo=bool(request.form.get('ativo'))
        )
        db.session.add(ponto)
        db.session.commit()
        flash('Ponto de retirada criado!', 'success')
        return redirect(url_for('pedidos.listar_pontos'))
    return render_template('pedidos/pontos_retirada_form.html', ponto=None)

@pedidos_bp.route('/pontos-retirada/<int:id>/editar', methods=['GET','POST'], endpoint='editar_ponto')
@login_required
def editar_ponto(id):
    ponto = db.session.get(PontoRetirada, id)
    if not ponto:
        abort(404)
    if request.method == 'POST':
        ponto.nome = request.form['nome']
        ponto.endereco = request.form['endereco']
        ponto.cidade = request.form.get('cidade')
        ponto.cep = request.form.get('cep')
        ponto.dias_funcionamento = request.form.get('dias_funcionamento')
        ponto.horario_abertura = request.form.get('horario_abertura')
        ponto.horario_fechamento = request.form.get('horario_fechamento')
        ponto.ativo = bool(request.form.get('ativo'))
        db.session.commit()
        flash('Ponto de retirada atualizado!', 'info')
        return redirect(url_for('pedidos.listar_pontos'))
    return render_template('pedidos/pontos_retirada_form.html', ponto=ponto)

@pedidos_bp.route('/pontos-retirada/<int:id>/excluir', methods=['POST'], endpoint='excluir_ponto')
@login_required
def excluir_ponto(id):
    ponto = db.session.get(PontoRetirada, id)
    if not ponto:
        abort(404)
    db.session.delete(ponto)
    db.session.commit()
    flash('Ponto de retirada excluído!', 'danger')
    return redirect(url_for('pedidos.listar_pontos'))

# ===== Gestão de Taxas de Entrega =====
@pedidos_bp.route('/taxas-entrega', endpoint='listar_taxas')
@login_required
def listar_taxas():
    taxas = TaxaEntrega.query.order_by(TaxaEntrega.regiao.asc()).all()
    return render_template('pedidos/taxas_entrega_list.html', taxas=taxas)

@pedidos_bp.route('/taxas-entrega/nova', methods=['GET','POST'], endpoint='nova_taxa')
@login_required
def nova_taxa():
    if request.method == 'POST':
        taxa = TaxaEntrega(
            regiao=request.form['regiao'],
            valor=float(request.form['valor']),
            prazo_dias=int(request.form.get('prazo_dias', 1)),
            ativo=bool(request.form.get('ativo'))
        )
        db.session.add(taxa)
        db.session.commit()
        flash('Taxa de entrega criada!', 'success')
        return redirect(url_for('pedidos.listar_taxas'))
    return render_template('pedidos/taxas_entrega_form.html', taxa=None)

@pedidos_bp.route('/taxas-entrega/<int:id>/editar', methods=['GET','POST'], endpoint='editar_taxa')
@login_required
def editar_taxa(id):
    taxa = db.session.get(TaxaEntrega, id)
    if not taxa:
        abort(404)
    if request.method == 'POST':
        taxa.regiao = request.form['regiao']
        taxa.valor = float(request.form['valor'])
        taxa.prazo_dias = int(request.form.get('prazo_dias', 1))
        taxa.ativo = bool(request.form.get('ativo'))
        db.session.commit()
        flash('Taxa de entrega atualizada!', 'info')
        return redirect(url_for('pedidos.listar_taxas'))
    return render_template('pedidos/taxas_entrega_form.html', taxa=taxa)

@pedidos_bp.route('/taxas-entrega/<int:id>/excluir', methods=['POST'], endpoint='excluir_taxa')
@login_required
def excluir_taxa(id):
    taxa = db.session.get(TaxaEntrega, id)
    if not taxa:
        abort(404)
    db.session.delete(taxa)
    db.session.commit()
    flash('Taxa de entrega excluída!', 'danger')
    return redirect(url_for('pedidos.listar_taxas'))

@pedidos_bp.route('/pagamento/pix/<int:pedido_id>', endpoint='pagamento_pix')
@login_required
def pagamento_pix(pedido_id):
    """
    Exibe página de pagamento PIX com QR Code
    Usa PagamentoService para gerar PIX via Mercado Pago ou simulado
    """
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    if pedido.cliente.usuario_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pedidos.historico'))
    
    # Gerar pagamento PIX
    from app.services.pagamento_service import PagamentoService
    pagamento_service = PagamentoService()
    
    try:
        dados_pix = pagamento_service.criar_pagamento_pix(pedido)
        
        return render_template('pedidos/pagamento_pix.html', 
                             pedido=pedido, 
                             codigo_pix=dados_pix['codigo_pix'],
                             qr_code_url=dados_pix['qr_code_url'],
                             simulado=dados_pix.get('simulado', False))
    except Exception as e:
        current_app.logger.error(f'Erro ao gerar pagamento PIX: {e}')
        flash('Erro ao gerar pagamento PIX. Tente novamente.', 'danger')
        return redirect(url_for('pedidos.historico'))

@pedidos_bp.route('/historico', endpoint='historico')
@login_required
def historico():
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    pedidos = Pedido.query.filter_by(cliente_id=cliente.id).order_by(Pedido.data.desc()).all() if cliente else []
    return render_template('pedidos/historico.html', pedidos=pedidos)

@pedidos_bp.route('/pedido/<int:pedido_id>', endpoint='detalhe_pedido')
@login_required
def detalhe_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    if pedido.cliente.usuario_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pedidos.historico'))
    # Agregar subtotal por produtor para evitar lógica complexa no template
    mapa = {}
    for item in pedido.itens:
        produtor = item.produto.produtor
        if not produtor:
            # Produto sem produtor, agrupar como 'N/A'
            pid = 'na'
            nome = 'N/A'
        else:
            pid = produtor.id
            nome = produtor.nome
        if pid not in mapa:
            mapa[pid] = {'nome': nome, 'quantidade': 0, 'subtotal': 0.0}
        mapa[pid]['quantidade'] += item.quantidade
        mapa[pid]['subtotal'] += float(item.preco_unitario or 0) * item.quantidade
    return render_template('pedidos/detalhe_pedido.html', pedido=pedido, mapa_produtores=mapa)

@pedidos_bp.route('/pedido/<int:pedido_id>/cancelar', methods=['POST'], endpoint='cancelar_pedido')
@login_required
def cancelar_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    if pedido.cliente.usuario_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pedidos.historico'))
    # Regra: só pode cancelar se status for 'Aguardando confirmação'
    if pedido.status != 'Aguardando confirmação':
        flash('Pedido não pode ser cancelado neste estágio.', 'warning')
        return redirect(url_for('pedidos.detalhe_pedido', pedido_id=pedido_id))
    # Verificar prazo (ex: até 1h após criação)
    from datetime import timedelta
    # Comparar usando datetimes ingênuos em UTC para evitar mistura de timezone
    limite = pedido.data + timedelta(hours=1)
    if datetime.utcnow() > limite:
        flash('Prazo para cancelamento expirado (1h após criação).', 'warning')
        return redirect(url_for('pedidos.detalhe_pedido', pedido_id=pedido_id))
    motivo = request.form.get('motivo', 'Cancelado pelo cliente')
    pedido.status = 'Cancelado'
    pedido.data_cancelamento = datetime.utcnow()
    pedido.motivo_cancelamento = motivo
    pedido.cancelado_por = 'cliente'
    # Restaurar estoque
    for item in pedido.itens:
        item.produto.estoque += item.quantidade
    db.session.commit()
    flash('Pedido cancelado com sucesso.', 'info')
    return redirect(url_for('pedidos.historico'))

@pedidos_bp.route('/pedido/<int:pedido_id>/excluir', methods=['POST'], endpoint='excluir_pedido')
@login_required
def excluir_pedido(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    if pedido.cliente.usuario_id != current_user.id:
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pedidos.historico'))
    # Só pode excluir se estiver cancelado
    if pedido.status != 'Cancelado':
        flash('Apenas pedidos cancelados podem ser excluídos.', 'warning')
        return redirect(url_for('pedidos.historico'))
    # Excluir itens do pedido primeiro (relacionamento)
    for item in pedido.itens:
        db.session.delete(item)
    db.session.delete(pedido)
    db.session.commit()
    flash('Pedido excluído permanentemente.', 'info')
    return redirect(url_for('pedidos.historico'))

@pedidos_bp.route('/comprovante/<int:pedido_id>/pdf', endpoint='comprovante_pdf')
@login_required
def comprovante_pdf(pedido_id):
    pedido = db.session.get(Pedido, pedido_id)
    if not pedido:
        abort(404)
    if pedido.cliente.usuario_id != current_user.id and current_user.tipo_usuario != 'admin':
        flash('Acesso não autorizado.', 'danger')
        return redirect(url_for('pedidos.historico'))
    # Gerar PDF simples com reportlab
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    y = altura - 50
    c.setFont('Helvetica-Bold', 14)
    c.drawString(50, y, f'Comprovante Pedido #{pedido.id}')
    y -= 25
    c.setFont('Helvetica', 10)
    c.drawString(50, y, f"Data: {pedido.data.strftime('%d/%m/%Y %H:%M')}  Status: {pedido.status}")
    y -= 15
    c.drawString(50, y, f'Cliente: {pedido.cliente.nome}')
    y -= 15
    if pedido.data_agendada:
        c.drawString(50, y, f"Data Agendada: {pedido.data_agendada.strftime('%d/%m/%Y')}")
        y -= 15
    c.drawString(50, y, f'Forma Pgto: {pedido.forma_pagamento}  Recebimento: {pedido.tipo_recebimento}')
    y -= 15
    if getattr(pedido, 'entrega_tipo', None) == 'entrega' and getattr(pedido, 'taxa_entrega', None):
        c.drawString(50, y, f"Entrega: {pedido.taxa_entrega.regiao} - Prazo {pedido.taxa_entrega.prazo_dias} dia(s) - Frete R$ {pedido.valor_frete:.2f}")
        y -= 15
    elif getattr(pedido, 'entrega_tipo', None) == 'retirada' and getattr(pedido, 'ponto_retirada', None):
        c.drawString(50, y, f"Retirada: {pedido.ponto_retirada.nome} - {pedido.ponto_retirada.endereco}")
    y -= 25
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Itens:')
    y -= 15
    c.setFont('Helvetica', 10)
    for item in pedido.itens:
        linha = f"{item.quantidade} x {item.produto.nome} - R$ {item.preco_unitario:.2f} (Subtotal R$ {item.preco_unitario*item.quantidade:.2f})"
        c.drawString(55, y, linha)
        y -= 13
        if y < 80:
            c.showPage()
            y = altura - 50
            c.setFont('Helvetica', 10)
    y -= 10
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, f'Total: R$ {pedido.total:.2f}')
    y -= 20
    # Subtotal por produtor
    c.setFont('Helvetica-Bold', 11)
    c.drawString(50, y, 'Subtotal por Produtor:')
    y -= 15
    c.setFont('Helvetica', 10)
    mapa = {}
    for item in pedido.itens:
        pid = item.produto.produtor.id
        if pid not in mapa:
            mapa[pid] = {'nome': item.produto.produtor.nome, 'quantidade': 0, 'subtotal': 0}
        mapa[pid]['quantidade'] += item.quantidade
        mapa[pid]['subtotal'] += item.preco_unitario * item.quantidade
    for dados in mapa.values():
        linha = f"{dados['nome']}: qtd {dados['quantidade']} - R$ {dados['subtotal']:.2f}"
        c.drawString(55, y, linha)
        y -= 13
        if y < 80:
            c.showPage(); y = altura - 50; c.setFont('Helvetica', 10)
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    from flask import Response
    return Response(pdf, mimetype='application/pdf', headers={'Content-Disposition': f'attachment;filename=pedido_{pedido.id}.pdf'})