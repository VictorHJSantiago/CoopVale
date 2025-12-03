from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import Usuario, Produtor, Cliente, Produto, Pedido, ItemPedido, Notificacao, PontoRetirada, TaxaEntrega, Contato
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

@admin_bp.route('/dashboard', endpoint='dashboard')
@login_required
@admin_required
def dashboard():
    from sqlalchemy import func
    from datetime import datetime, timedelta, timezone
    total_produtores = Produtor.query.count()
    total_clientes = Cliente.query.count()
    total_produtos = Produto.query.count()
    total_pedidos = Pedido.query.count()
    pedidos_pendentes = Pedido.query.filter(Pedido.status=='Aguardando confirmação').count()

    # Visão geral de vendas
    hoje = datetime.now(timezone.utc).date()
    vendas_diario = db.session.query(func.sum(Pedido.total)).filter(func.date(Pedido.data)==hoje).scalar() or 0
    vendas_semana = db.session.query(func.sum(Pedido.total)).filter(Pedido.data >= hoje - timedelta(days=7)).scalar() or 0
    vendas_mes = db.session.query(func.sum(Pedido.total)).filter(Pedido.data >= hoje - timedelta(days=30)).scalar() or 0

    # Produtos mais vendidos
    mais_vendidos = db.session.query(
        Produto.nome, func.sum(ItemPedido.quantidade).label('qtd')
    ).join(ItemPedido).group_by(Produto.id).order_by(func.sum(ItemPedido.quantidade).desc()).limit(5).all()

    # Desempenho por produtor (joins explícitos para evitar ambiguidade)
    desempenho_produtores = db.session.query(
        Produtor.nome, func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).label('faturamento')
    ).select_from(Produtor)
    desempenho_produtores = desempenho_produtores.join(Produto, Produto.produtor_id == Produtor.id)
    desempenho_produtores = desempenho_produtores.join(ItemPedido, ItemPedido.produto_id == Produto.id)
    desempenho_produtores = desempenho_produtores.group_by(Produtor.id).order_by(func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).desc()).limit(5).all()

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

@admin_bp.route('/usuarios', endpoint='usuarios')
@login_required
@admin_required
def usuarios():
    usuarios = Usuario.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)

@admin_bp.route('/pedidos', endpoint='pedidos')
@login_required
@admin_required
def pedidos():
    pedidos = Pedido.query.order_by(Pedido.data.desc()).all()
    return render_template('admin/pedidos.html', pedidos=pedidos)

@admin_bp.route('/pedidos/<int:pedido_id>/status', methods=['POST'], endpoint='atualizar_status_pedido')
@login_required
@admin_required
def atualizar_status_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    novo_status = request.form.get('status')
    if novo_status and novo_status != pedido.status:
        pedido.status = novo_status
        # Criar notificação para cliente
        notificacao = Notificacao(cliente_id=pedido.cliente_id, mensagem=f'Seu pedido #{pedido.id} agora está: {pedido.status}')
        db.session.add(notificacao)
        db.session.commit()
        flash(f'Status do pedido #{pedido.id} atualizado para "{pedido.status}". Cliente notificado.', 'success')
    else:
        flash('Nenhuma alteração de status aplicada.', 'info')
    return redirect(url_for('admin.pedidos'))

@admin_bp.route('/usuarios/<int:id>/ativar', methods=['POST'], endpoint='ativar_usuario')
@login_required
@admin_required
def ativar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = True
    db.session.commit()
    flash('Usuário ativado.', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/usuarios/<int:id>/desativar', methods=['POST'], endpoint='desativar_usuario')
@login_required
@admin_required
def desativar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    usuario.ativo = False
    db.session.commit()
    flash('Usuário desativado.', 'warning')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/pontos-retirada', endpoint='pontos_retirada')
@login_required
@admin_required
def pontos_retirada():
    pontos = PontoRetirada.query.all()
    return render_template('admin/pontos_retirada.html', pontos=pontos)

@admin_bp.route('/pontos-retirada/novo', methods=['GET', 'POST'], endpoint='novo_ponto_retirada')
@login_required
@admin_required
def novo_ponto_retirada():
    if request.method == 'POST':
        ponto = PontoRetirada(
            nome=request.form['nome'],
            endereco=request.form['endereco'],
            cidade=request.form.get('cidade'),
            cep=request.form.get('cep'),
            dias_funcionamento=request.form.get('dias_funcionamento'),
            horario_abertura=request.form.get('horario_abertura'),
            horario_fechamento=request.form.get('horario_fechamento'),
            ativo=True
        )
        db.session.add(ponto)
        db.session.commit()
        flash('Ponto de retirada criado!', 'success')
        return redirect(url_for('admin.pontos_retirada'))
    return render_template('admin/ponto_retirada_form.html', ponto=None)

@admin_bp.route('/pontos-retirada/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar_ponto_retirada')
@login_required
@admin_required
def editar_ponto_retirada(id):
    ponto = PontoRetirada.query.get_or_404(id)
    if request.method == 'POST':
        ponto.nome = request.form['nome']
        ponto.endereco = request.form['endereco']
        ponto.cidade = request.form.get('cidade')
        ponto.cep = request.form.get('cep')
        ponto.dias_funcionamento = request.form.get('dias_funcionamento')
        ponto.horario_abertura = request.form.get('horario_abertura')
        ponto.horario_fechamento = request.form.get('horario_fechamento')
        db.session.commit()
        flash('Ponto de retirada atualizado!', 'success')
        return redirect(url_for('admin.pontos_retirada'))
    return render_template('admin/ponto_retirada_form.html', ponto=ponto)

@admin_bp.route('/pontos-retirada/<int:id>/excluir', methods=['POST'], endpoint='excluir_ponto_retirada')
@login_required
@admin_required
def excluir_ponto_retirada(id):
    ponto = PontoRetirada.query.get_or_404(id)
    db.session.delete(ponto)
    db.session.commit()
    flash('Ponto de retirada excluído!', 'danger')
    return redirect(url_for('admin.pontos_retirada'))

@admin_bp.route('/taxas-entrega', endpoint='taxas_entrega')
@login_required
@admin_required
def taxas_entrega():
    taxas = TaxaEntrega.query.all()
    return render_template('admin/taxas_entrega.html', taxas=taxas)

@admin_bp.route('/taxas-entrega/nova', methods=['GET', 'POST'], endpoint='nova_taxa_entrega')
@login_required
@admin_required
def nova_taxa_entrega():
    if request.method == 'POST':
        taxa = TaxaEntrega(
            regiao=request.form['regiao'],
            valor=float(request.form['valor']),
            prazo_dias=int(request.form.get('prazo_dias', 1)),
            ativo=True
        )
        db.session.add(taxa)
        db.session.commit()
        flash('Taxa de entrega criada!', 'success')
        return redirect(url_for('admin.taxas_entrega'))
    return render_template('admin/taxa_entrega_form.html', taxa=None)

@admin_bp.route('/taxas-entrega/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar_taxa_entrega')
@login_required
@admin_required
def editar_taxa_entrega(id):
    taxa = TaxaEntrega.query.get_or_404(id)
    if request.method == 'POST':
        taxa.regiao = request.form['regiao']
        taxa.valor = float(request.form['valor'])
        taxa.prazo_dias = int(request.form.get('prazo_dias', 1))
        db.session.commit()
        flash('Taxa de entrega atualizada!', 'success')
        return redirect(url_for('admin.taxas_entrega'))
    return render_template('admin/taxa_entrega_form.html', taxa=taxa)

@admin_bp.route('/taxas-entrega/<int:id>/excluir', methods=['POST'], endpoint='excluir_taxa_entrega')
@login_required
@admin_required
def excluir_taxa_entrega(id):
    taxa = TaxaEntrega.query.get_or_404(id)
    db.session.delete(taxa)
    db.session.commit()
    flash('Taxa de entrega excluída!', 'danger')
    return redirect(url_for('admin.taxas_entrega'))

# ------------------------ Produtores (Admin CRUD) ------------------------
@admin_bp.route('/produtores', endpoint='produtores_list')
@login_required
@admin_required
def produtores_list():
    produtores = Produtor.query.order_by(Produtor.nome.asc()).all()
    return render_template('admin/produtores_list.html', produtores=produtores)

@admin_bp.route('/produtores/novo', methods=['GET','POST'], endpoint='produtores_novo')
@login_required
@admin_required
def produtores_novo():
    if request.method == 'POST':
        nome = request.form['nome']
        cidade = request.form.get('cidade')
        estado = request.form.get('estado')
        bio = request.form.get('bio')
        produtor = Produtor(nome=nome, cidade=cidade, estado=estado, bio=bio)
        db.session.add(produtor)
        db.session.commit()
        flash('Produtor criado com sucesso!', 'success')
        return redirect(url_for('admin.produtores_list'))
    return render_template('admin/produtor_form.html', produtor=None)

@admin_bp.route('/produtores/<int:id>/editar', methods=['GET','POST'], endpoint='produtores_editar')
@login_required
@admin_required
def produtores_editar(id):
    produtor = Produtor.query.get_or_404(id)
    if request.method == 'POST':
        produtor.nome = request.form['nome']
        produtor.cidade = request.form.get('cidade')
        produtor.estado = request.form.get('estado')
        produtor.bio = request.form.get('bio')
        db.session.commit()
        flash('Produtor atualizado!', 'success')
        return redirect(url_for('admin.produtores_list'))
    return render_template('admin/produtor_form.html', produtor=produtor)

@admin_bp.route('/produtores/<int:id>/excluir', methods=['POST'], endpoint='produtores_excluir')
@login_required
@admin_required
def produtores_excluir(id):
    produtor = Produtor.query.get_or_404(id)
    db.session.delete(produtor)
    db.session.commit()
    flash('Produtor excluído!', 'danger')
    return redirect(url_for('admin.produtores_list'))

# ------------------------ Seed de Produtos (Admin) ------------------------
@admin_bp.route('/seed-produtos', methods=['POST'], endpoint='seed_produtos')
@login_required
@admin_required
def seed_produtos():
    from random import randint, uniform, choice
    # Garantir categorias base
    from app.models.core import Categoria
    categorias = Categoria.query.all()
    if not categorias:
        base = [
            ('Verduras', 'Folhosas e verdes', 'leaf'),
            ('Frutas', 'Frescas e sazonais', 'apple'),
            ('Legumes', 'Tubérculos e afins', 'carrot'),
            ('Grãos', 'Cereais e farinhas', 'grain'),
            ('Laticínios', 'Leite e derivados', 'milk')
        ]
        for nome, desc, icone in base:
            db.session.add(Categoria(nome=nome, descricao=desc, icone=icone))
        db.session.commit()
        categorias = Categoria.query.all()
    # Selecionar um produtor ou criar dummy
    produtor = Produtor.query.first()
    if not produtor:
        produtor = Produtor(nome='Produtor Demo', descricao='Produtor de demonstração', usuario_id=None)
        db.session.add(produtor)
        db.session.commit()
    # Criar 100 produtos
    created = 0
    for i in range(1, 101):
        nome = f"Produto Demo {i}"
        if Produto.query.filter_by(nome=nome).first():
            continue
        categoria = choice(categorias)
        preco = round(uniform(3.0, 50.0), 2)
        estoque = round(uniform(10, 200), 1)
        unidade = choice(['kg', 'un', 'molho', 'litro'])
        produto = Produto(
            nome=nome,
            descricao=f"Descrição do {nome} com qualidade e origem local.",
            preco=preco,
            unidade=unidade,
            categoria_id=categoria.id,
            estoque=estoque,
            imagens='',
            tags='orgânico, local',
            produtor_id=produtor.id
        )
        db.session.add(produto)
        created += 1
    db.session.commit()
    flash(f'{created} produtos de demonstração adicionados com sucesso!', 'success')
    return redirect(url_for('produtos_bp.catalogo'))

@admin_bp.route('/relatorios/faturamento-produtor', endpoint='relatorio_faturamento_produtor')
@login_required
@admin_required
def relatorio_faturamento_produtor():
    from sqlalchemy import func
    from datetime import datetime
    import csv
    import io
    from flask import make_response
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    export_format = request.args.get('export')
    
    query = db.session.query(
        Produtor.id,
        Produtor.nome,
        func.sum(ItemPedido.quantidade * ItemPedido.preco_unitario).label('faturamento'),
        func.count(ItemPedido.id).label('total_itens')
    ).join(Produto).join(ItemPedido).join(Pedido)
    
    if data_inicio:
        dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d')
        query = query.filter(Pedido.data >= dt_inicio)
    if data_fim:
        dt_fim = datetime.strptime(data_fim, '%Y-%m-%d')
        query = query.filter(Pedido.data <= dt_fim)
    
    relatorio = query.group_by(Produtor.id).all()
    
    # Exportação CSV
    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Produtor', 'Faturamento (R$)', 'Total de Itens'])
        for item in relatorio:
            writer.writerow([item.id, item.nome, f'{item.faturamento:.2f}', item.total_itens])
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_faturamento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
    
    # Exportação PDF
    if export_format == 'pdf':
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title = Paragraph('<b>Relatório de Faturamento por Produtor</b>', styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.5*cm))
        
        # Período
        if data_inicio or data_fim:
            periodo_text = f"Período: {data_inicio or 'Início'} até {data_fim or 'Hoje'}"
            periodo = Paragraph(periodo_text, styles['Normal'])
            elements.append(periodo)
            elements.append(Spacer(1, 0.3*cm))
        
        # Tabela
        data = [['ID', 'Produtor', 'Faturamento (R$)', 'Total de Itens']]
        for item in relatorio:
            data.append([str(item.id), item.nome, f'R$ {item.faturamento:.2f}', str(item.total_itens)])
        
        table = Table(data, colWidths=[2*cm, 8*cm, 4*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        
        response = make_response(buffer.read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_faturamento_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        return response
    
    # Renderização HTML normal
    return render_template('admin/relatorio_faturamento.html', relatorio=relatorio, data_inicio=data_inicio, data_fim=data_fim)

@admin_bp.route('/contatos', endpoint='contatos')
@login_required
@admin_required
def contatos():
    filtro = request.args.get('filtro', 'todos')
    query = Contato.query.order_by(Contato.criado_em.desc())
    if filtro == 'novos':
        query = query.filter_by(respondido=False)
    registros = query.all()
    return render_template('admin/contatos.html', contatos=registros, filtro=filtro)

@admin_bp.route('/contatos/<int:id>/responder', methods=['POST'], endpoint='responder_contato')
@login_required
@admin_required
def responder_contato(id):
    contato = Contato.query.get_or_404(id)
    contato.respondido = True
    db.session.commit()
    flash('Contato marcado como respondido.', 'success')
    return redirect(url_for('admin.contatos', filtro=request.args.get('filtro', 'todos')))

@admin_bp.route('/contatos/<int:id>/excluir', methods=['POST'], endpoint='excluir_contato')
@login_required
@admin_required
def excluir_contato(id):
    contato = Contato.query.get_or_404(id)
    db.session.delete(contato)
    db.session.commit()
    flash('Contato excluído.', 'danger')
    return redirect(url_for('admin.contatos', filtro=request.args.get('filtro', 'todos')))
