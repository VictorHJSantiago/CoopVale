# Imports devem estar no topo
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import Categoria, Produto
from . import produtos_bp

# CRUD de Produtos
@produtos_bp.route('/produtos')
@login_required
def listar_produtos():
    produtos = Produto.query.all()
    return render_template('produtos/produtos.html', produtos=produtos)


import os
from werkzeug.utils import secure_filename

@produtos_bp.route('/produtos/novo', methods=['GET', 'POST'])
@login_required
def novo_produto():
    categorias = Categoria.query.all()
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        preco = float(request.form['preco'])
        unidade = request.form['unidade']
        categoria_id = int(request.form['categoria_id'])
        estoque = int(request.form['estoque'])
        tags = request.form['tags']
        produtor_id = current_user.produtor.id if hasattr(current_user, 'produtor') and current_user.produtor else None

        # Upload múltiplo de imagens
        imagens_files = request.files.getlist('imagens')
        imagens_paths = []
        if imagens_files:
            for file in imagens_files[:5]:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtos')
                    os.makedirs(upload_dir, exist_ok=True)
                    file.save(os.path.join(upload_dir, filename))
                    imagens_paths.append(f'uploads/produtos/{filename}')
        imagens = ','.join(imagens_paths)

        produto = Produto(
            nome=nome,
            descricao=descricao,
            preco=preco,
            unidade=unidade,
            categoria_id=categoria_id,
            estoque=estoque,
            imagens=imagens,
            tags=tags,
            produtor_id=produtor_id
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto cadastrado com sucesso!', 'success')
        return redirect(url_for('produtos_bp.listar_produtos'))
    return render_template('produtos/novo_produto.html', categorias=categorias)


@produtos_bp.route('/produtos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    categorias = Categoria.query.all()
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.preco = float(request.form['preco'])
        produto.unidade = request.form['unidade']
        produto.categoria_id = int(request.form['categoria_id'])
        produto.estoque = int(request.form['estoque'])
        produto.tags = request.form['tags']

        # Upload múltiplo de imagens (adiciona às existentes)
        imagens_files = request.files.getlist('imagens')
        imagens_paths = produto.imagens.split(',') if produto.imagens else []
        if imagens_files:
            for file in imagens_files:
                if file and file.filename and len(imagens_paths) < 5:
                    filename = secure_filename(file.filename)
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtos')
                    os.makedirs(upload_dir, exist_ok=True)
                    file.save(os.path.join(upload_dir, filename))
                    imagens_paths.append(f'uploads/produtos/{filename}')
        # Remover imagens selecionadas
        remover = request.form.getlist('remover_imagem')
        imagens_paths = [img for img in imagens_paths if img not in remover]
        produto.imagens = ','.join(imagens_paths[:5])

        db.session.commit()
        flash('Produto atualizado!', 'info')
        return redirect(url_for('produtos_bp.listar_produtos'))
    return render_template('produtos/editar_produto.html', produto=produto, categorias=categorias)

@produtos_bp.route('/produtos/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído!', 'danger')
    return redirect(url_for('produtos_bp.listar_produtos'))

# Catálogo de Produtos (RF03)
@produtos_bp.route('/')
def catalogo():
    from app.models.core import Categoria, Produtor
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
    return render_template('produtos/catalogo.html', produtos=produtos, categorias=categorias)

@produtos_bp.route('/detalhe/<int:id>')
def detalhe(id):
    produto = Produto.query.get_or_404(id)
    return render_template('produtos/detalhe.html', produto=produto)

# CRUD de Categorias
@produtos_bp.route('/categorias')
@login_required
def listar_categorias():
    categorias = Categoria.query.all()
    return render_template('produtos/categorias.html', categorias=categorias)

@produtos_bp.route('/categorias/nova', methods=['GET', 'POST'])
@login_required
def nova_categoria():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        icone = request.form['icone']
        categoria = Categoria(nome=nome, descricao=descricao, icone=icone)
        db.session.add(categoria)
        db.session.commit()
        flash('Categoria criada com sucesso!', 'success')
        return redirect(url_for('produtos_bp.listar_categorias'))
    return render_template('produtos/nova_categoria.html')

@produtos_bp.route('/categorias/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    if request.method == 'POST':
        categoria.nome = request.form['nome']
        categoria.descricao = request.form['descricao']
        categoria.icone = request.form['icone']
        db.session.commit()
        flash('Categoria atualizada!', 'info')
        return redirect(url_for('produtos_bp.listar_categorias'))
    return render_template('produtos/editar_categoria.html', categoria=categoria)

@produtos_bp.route('/categorias/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoria excluída!', 'danger')
    return redirect(url_for('produtos_bp.listar_categorias'))