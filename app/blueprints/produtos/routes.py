import os
from flask import render_template, redirect, url_for, flash, request, current_app, abort
from datetime import datetime, timezone
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.core import Categoria, Produto, Produtor, Cliente, Review
from . import produtos_bp

@produtos_bp.route('/produtos', endpoint='listar_produtos')
@login_required
def listar_produtos():
    produtos = Produto.query.all()
    return render_template('produtos/produtos.html', produtos=produtos)

@produtos_bp.route('/produtos/novo', methods=['GET', 'POST'], endpoint='novo_produto')
@login_required
def novo_produto():
    categorias = Categoria.query.order_by(Categoria.nome.asc()).all()
    if request.method == 'POST':
        if not categorias:
            flash('Nenhuma categoria cadastrada. Crie uma categoria antes de cadastrar produtos.', 'warning')
            return redirect(url_for('produtos_bp.nova_categoria'))
        produtor_id = current_user.produtor_perfil.id if current_user.produtor_perfil else None
        
        imagens_files = request.files.getlist('imagens')
        imagens_paths = []
        if imagens_files:
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtos')
            os.makedirs(upload_dir, exist_ok=True)
            for file in imagens_files[:5]:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(upload_dir, filename))
                    imagens_paths.append(f'uploads/produtos/{filename}')
        
        sazonal_inicio = request.form.get('sazonal_inicio') or None
        sazonal_fim = request.form.get('sazonal_fim') or None
        from datetime import datetime
        dt_inicio = datetime.fromisoformat(sazonal_inicio) if sazonal_inicio else None
        dt_fim = datetime.fromisoformat(sazonal_fim) if sazonal_fim else None
        preco_promocional = request.form.get('preco_promocional') or None
        produto = Produto(
            nome=request.form['nome'],
            descricao=request.form['descricao'],
            preco=float(request.form['preco']),
            unidade=request.form['unidade'],
            categoria_id=int(request.form['categoria_id']),
            estoque=float(request.form['estoque']),
            imagens=','.join(imagens_paths),
            tags=request.form['tags'],
            subcategoria=request.form.get('subcategoria'),
            origem=request.form.get('origem'),
            informacoes_nutricionais=request.form.get('informacoes_nutricionais'),
            preco_promocional=float(preco_promocional) if preco_promocional else None,
            sazonal_inicio=dt_inicio,
            sazonal_fim=dt_fim,
            produtor_id=produtor_id
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('produtos_bp.listar_produtos'))
    return render_template('produtos/novo_produto.html', categorias=categorias)

@produtos_bp.route('/produtos/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar_produto')
@login_required
def editar_produto(id):
    produto = db.session.get(Produto, id)
    if not produto:
        abort(404)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.preco = float(request.form['preco'])
        produto.unidade = request.form['unidade']
        produto.categoria_id = int(request.form['categoria_id'])
        produto.estoque = float(request.form['estoque'])
        produto.tags = request.form['tags']
        produto.subcategoria = request.form.get('subcategoria')
        produto.origem = request.form.get('origem')
        produto.informacoes_nutricionais = request.form.get('informacoes_nutricionais')
        preco_promocional = request.form.get('preco_promocional') or None
        produto.preco_promocional = float(preco_promocional) if preco_promocional else None
        sazonal_inicio = request.form.get('sazonal_inicio') or None
        sazonal_fim = request.form.get('sazonal_fim') or None
        from datetime import datetime
        produto.sazonal_inicio = datetime.fromisoformat(sazonal_inicio) if sazonal_inicio else None
        produto.sazonal_fim = datetime.fromisoformat(sazonal_fim) if sazonal_fim else None
        db.session.commit()
        flash('Produto atualizado!', 'info')
        return redirect(url_for('produtos_bp.listar_produtos'))
    return render_template('produtos/editar_produto.html', produto=produto, categorias=categorias)

@produtos_bp.route('/produtos/<int:id>/excluir', methods=['POST'], endpoint='excluir_produto')
@login_required
def excluir_produto(id):
    produto = db.session.get(Produto, id)
    if not produto:
        abort(404)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído!', 'danger')
    return redirect(url_for('produtos_bp.listar_produtos'))

@produtos_bp.route('/', endpoint='catalogo')
def catalogo():
    busca = request.args.get('busca', '').strip()
    categoria_id = request.args.get('categoria_id', type=int)
    produtor_nome = request.args.get('produtor', '').strip()
    preco_min = request.args.get('preco_min', type=float)
    preco_max = request.args.get('preco_max', type=float)
    tag = request.args.get('tag', '').strip()
    so_organico = request.args.get('so_organico')
    
    query = Produto.query
    if busca:
        query = query.filter((Produto.nome.ilike(f'%{busca}%')) | (Produto.tags.ilike(f'%{busca}%')))
    if categoria_id:
        query = query.filter_by(categoria_id=categoria_id)
    if produtor_nome:
        query = query.join(Produtor).filter(Produtor.nome.ilike(f'%{produtor_nome}%'))
    if preco_min is not None:
        query = query.filter(Produto.preco >= preco_min)
    if preco_max is not None:
        query = query.filter(Produto.preco <= preco_max)
    if tag:
        query = query.filter(Produto.tags.ilike(f'%{tag}%'))
    if so_organico:
        query = query.filter(Produto.tags.ilike('%orgânico%'))
        
    produtos = query.all()
    categorias = Categoria.query.all()
    return render_template('produtos/catalogo.html', produtos=produtos, categorias=categorias, datetime=datetime, timezone=timezone)

# Alias para compatibilidade com testes que esperam /produtos/catalogo
@produtos_bp.route('/catalogo', endpoint='catalogo_alias')
def catalogo_alias():
    return render_template('produtos/catalogo.html', produtos=Produto.query.all(), categorias=Categoria.query.all(), datetime=datetime, timezone=timezone)

@produtos_bp.route('/detalhe/<int:produto_id>', endpoint='detalhe')
def detalhe(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
    reviews = Review.query.filter_by(produto_id=produto_id).order_by(Review.criado_em.desc()).all()
    from sqlalchemy import func
    media_nota = db.session.query(func.avg(Review.nota)).filter_by(produto_id=produto_id).scalar() or 0
    return render_template('produtos/detalhe_produto.html', produto=produto, reviews=reviews, media_nota=media_nota, datetime=datetime, timezone=timezone)

@produtos_bp.route('/categorias', endpoint='listar_categorias')
@login_required
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('produtos/categorias.html', categorias=categorias)

@produtos_bp.route('/categorias/nova', methods=['GET', 'POST'], endpoint='nova_categoria')
@login_required
def nova_categoria():
    if request.method == 'POST':
        valor_minimo = request.form.get('valor_minimo') or None
        quantidade_minima = request.form.get('quantidade_minima') or None
        categoria = Categoria(
            nome=request.form['nome'],
            descricao=request.form['descricao'],
            icone=request.form['icone'],
            valor_minimo=float(valor_minimo) if valor_minimo else None,
            quantidade_minima=float(quantidade_minima) if quantidade_minima else None
        )
        db.session.add(categoria)
        db.session.commit()
        flash('Categoria criada!', 'success')
        return redirect(url_for('produtos_bp.listar_categorias'))
    return render_template('produtos/nova_categoria.html')

@produtos_bp.route('/categorias/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar_categoria')
@login_required
def editar_categoria(id):
    categoria = db.session.get(Categoria, id)
    if not categoria:
        abort(404)
    if request.method == 'POST':
        categoria.nome = request.form['nome']
        categoria.descricao = request.form['descricao']
        categoria.icone = request.form['icone']
        valor_minimo = request.form.get('valor_minimo') or None
        quantidade_minima = request.form.get('quantidade_minima') or None
        categoria.valor_minimo = float(valor_minimo) if valor_minimo else None
        categoria.quantidade_minima = float(quantidade_minima) if quantidade_minima else None
        db.session.commit()
        flash('Categoria atualizada!', 'info')
        return redirect(url_for('produtos_bp.listar_categorias'))
    return render_template('produtos/editar_categoria.html', categoria=categoria)

@produtos_bp.route('/categorias/<int:id>/excluir', methods=['POST'], endpoint='excluir_categoria')
@login_required
def excluir_categoria(id):
    categoria = db.session.get(Categoria, id)
    if not categoria:
        abort(404)
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoria excluída!', 'danger')
    return redirect(url_for('produtos_bp.listar_categorias'))

@produtos_bp.route('/produto/<int:produto_id>/avaliar', methods=['POST'], endpoint='avaliar_produto')
@login_required
def avaliar_produto(produto_id):
    produto = db.session.get(Produto, produto_id)
    if not produto:
        abort(404)
    cliente = Cliente.query.filter_by(usuario_id=current_user.id).first()
    if not cliente:
        flash('Perfil de cliente não encontrado.', 'danger')
        return redirect(url_for('produtos_bp.detalhe', produto_id=produto_id))
    nota = int(request.form.get('nota', 5))
    comentario = request.form.get('comentario', '')
    # Verificar se já avaliou
    review_existente = Review.query.filter_by(cliente_id=cliente.id, produto_id=produto_id).first()
    if review_existente:
        review_existente.nota = nota
        review_existente.comentario = comentario
        flash('Avaliação atualizada!', 'success')
    else:
        review = Review(cliente_id=cliente.id, produto_id=produto_id, nota=nota, comentario=comentario)
        db.session.add(review)
        flash('Avaliação enviada com sucesso!', 'success')
    db.session.commit()
    return redirect(url_for('produtos_bp.detalhe', produto_id=produto_id))