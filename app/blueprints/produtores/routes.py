import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.core import Produtor, Produto, Categoria
from . import produtores_bp

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@produtores_bp.route('/produtores', endpoint='listar')
@login_required
def listar_produtores():
    produtores = Produtor.query.all()
    return render_template('produtores/produtores.html', produtores=produtores)

@produtores_bp.route('/produtores/novo', methods=['GET', 'POST'], endpoint='novo')
@login_required
def novo_produtor():
    if request.method == 'POST':
        # Upload de fotos da propriedade
        fotos_files = request.files.getlist('fotos')
        fotos_paths = []
        if fotos_files:
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtores')
            os.makedirs(upload_dir, exist_ok=True)
            for file in fotos_files[:10]:  # Máximo 10 fotos
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Adiciona timestamp para evitar conflitos
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    file.save(os.path.join(upload_dir, filename))
                    fotos_paths.append(f'uploads/produtores/{filename}')
        
        produtor = Produtor(
            nome=request.form['nome'],
            cpf=request.form['cpf'],
            telefone=request.form['telefone'],
            endereco=request.form['endereco'],
            certificacoes=request.form['certificacoes'],
            descricao=request.form['descricao'],
            fotos=','.join(fotos_paths) if fotos_paths else None,
            usuario_id=current_user.id
        )
        db.session.add(produtor)
        db.session.commit()
        flash('Produtor cadastrado com sucesso!', 'success')
        return redirect(url_for('produtores.listar'))
    return render_template('produtores/novo_produtor.html')

@produtores_bp.route('/produtores/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar')
@login_required
def editar_produtor(id):
    produtor = Produtor.query.get_or_404(id)
    if request.method == 'POST':
        produtor.nome = request.form['nome']
        produtor.cpf = request.form['cpf']
        produtor.telefone = request.form['telefone']
        produtor.endereco = request.form['endereco']
        produtor.certificacoes = request.form['certificacoes']
        produtor.descricao = request.form['descricao']
        
        # Upload de novas fotos
        fotos_files = request.files.getlist('fotos')
        if fotos_files and fotos_files[0].filename:
            fotos_paths = []
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtores')
            os.makedirs(upload_dir, exist_ok=True)
            for file in fotos_files[:10]:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    from datetime import datetime
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{timestamp}_{filename}"
                    file.save(os.path.join(upload_dir, filename))
                    fotos_paths.append(f'uploads/produtores/{filename}')
            if fotos_paths:
                produtor.fotos = ','.join(fotos_paths)
        
        db.session.commit()
        flash('Produtor atualizado!', 'success')
        return redirect(url_for('produtores.listar'))
    return render_template('produtores/editar_produtor.html', produtor=produtor)

@produtores_bp.route('/produtores/<int:id>/excluir', methods=['POST'], endpoint='excluir')
@login_required
def excluir_produtor(id):
    produtor = Produtor.query.get_or_404(id)
    db.session.delete(produtor)
    db.session.commit()
    flash('Produtor excluído!', 'danger')
    return redirect(url_for('produtores.listar'))

# ---------------------- Área do Produtor (Dashboard + CRUD próprios) ----------------------
@produtores_bp.route('/dashboard', endpoint='dashboard_home')
@login_required
def dashboard():
    if current_user.tipo_usuario != 'produtor':
        return render_template('produtores/dashboard.html', erro='Apenas produtores têm acesso ao dashboard.', produtos=[], pedidos=[], total_vendas=0)
    produtor = Produtor.query.filter_by(usuario_id=current_user.id).first()
    produtos = Produto.query.filter_by(produtor_id=produtor.id).all() if produtor else []
    # Pedidos contendo produtos do produtor
    from app.models.core import Pedido, ItemPedido
    pedidos = []
    total_vendas = 0
    if produtos:
        ids_produtos = [p.id for p in produtos]
        itens = ItemPedido.query.filter(ItemPedido.produto_id.in_(ids_produtos)).all()
        pedido_ids = {it.pedido_id for it in itens}
        if pedido_ids:
            pedidos = Pedido.query.filter(Pedido.id.in_(list(pedido_ids))).order_by(Pedido.data.desc()).all()
            total_vendas = sum(it.quantidade * it.preco_unitario for it in itens)
    return render_template('produtores/dashboard.html', erro=None, produtor=produtor, produtos=produtos, pedidos=pedidos, total_vendas=total_vendas)

@produtores_bp.route('/perfil', methods=['GET','POST'], endpoint='perfil')
@login_required
def editar_perfil():
    if current_user.tipo_usuario != 'produtor':
        flash('Apenas produtores podem editar este perfil.', 'warning')
        return redirect(url_for('main_bp.index'))
    produtor = Produtor.query.filter_by(usuario_id=current_user.id).first_or_404()
    if request.method == 'POST':
        produtor.nome = request.form.get('nome', produtor.nome)
        produtor.descricao = request.form.get('descricao', produtor.descricao)
        produtor.endereco = request.form.get('endereco', produtor.endereco)
        produtor.cidade = request.form.get('cidade', getattr(produtor, 'cidade', None))
        produtor.estado = request.form.get('estado', getattr(produtor, 'estado', None))
        # Foto
        foto = request.files.get('foto')
        if foto and foto.filename and allowed_file(foto.filename):
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtores')
            os.makedirs(upload_dir, exist_ok=True)
            filename = secure_filename(foto.filename)
            foto.save(os.path.join(upload_dir, filename))
            produtor.fotos = f'uploads/produtores/{filename}'
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('produtores.dashboard_home'))
    return render_template('produtores/editar_perfil.html', produtor=produtor)

@produtores_bp.route('/meus-produtos', endpoint='meus_produtos')
@login_required
def meus_produtos():
    if current_user.tipo_usuario != 'produtor':
        flash('Acesso restrito ao produtor.', 'danger')
        return redirect(url_for('main_bp.index'))
    produtor = Produtor.query.filter_by(usuario_id=current_user.id).first_or_404()
    produtos = Produto.query.filter_by(produtor_id=produtor.id).all()
    return render_template('produtores/meus_produtos.html', produtos=produtos)

@produtores_bp.route('/meus-produtos/novo', methods=['GET','POST'], endpoint='meus_produtos_novo')
@login_required
def novo_produto_produtor():
    if current_user.tipo_usuario != 'produtor':
        flash('Acesso restrito ao produtor.', 'danger')
        return redirect(url_for('main_bp.index'))
    produtor = Produtor.query.filter_by(usuario_id=current_user.id).first_or_404()
    if request.method == 'POST':
        imagens_files = request.files.getlist('imagens')
        imagens_paths = []
        if imagens_files:
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtos')
            os.makedirs(upload_dir, exist_ok=True)
            for file in imagens_files[:5]:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(upload_dir, filename))
                    imagens_paths.append(f'uploads/produtos/{filename}')
        categoria_id = int(request.form['categoria_id'])
        produto = Produto(
            nome=request.form['nome'],
            descricao=request.form['descricao'],
            preco=float(request.form['preco']),
            unidade=request.form['unidade'],
            categoria_id=categoria_id,
            estoque=float(request.form['estoque']),
            imagens=','.join(imagens_paths),
            tags=request.form.get('tags',''),
            produtor_id=produtor.id
        )
        db.session.add(produto)
        db.session.commit()
        flash('Produto criado!', 'success')
        return redirect(url_for('produtores.meus_produtos'))
    categorias = Categoria.query.all()
    return render_template('produtores/novo_produto.html', categorias=categorias)

@produtores_bp.route('/meus-produtos/<int:id>/editar', methods=['GET','POST'], endpoint='meus_produtos_editar')
@login_required
def editar_meu_produto(id):
    produto = Produto.query.get_or_404(id)
    produtor = Produtor.query.filter_by(usuario_id=current_user.id).first_or_404()
    if produto.produtor_id != produtor.id:
        flash('Você não tem permissão para editar este produto.', 'danger')
        return redirect(url_for('produtores.meus_produtos'))
    if request.method == 'POST':
        produto.nome = request.form['nome']
        produto.descricao = request.form['descricao']
        produto.preco = float(request.form['preco'])
        produto.unidade = request.form['unidade']
        produto.estoque = float(request.form['estoque'])
        imagens_files = request.files.getlist('imagens')
        if imagens_files:
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'produtos')
            os.makedirs(upload_dir, exist_ok=True)
            imgs = []
            for file in imagens_files[:5]:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(upload_dir, filename))
                    imgs.append(f'uploads/produtos/{filename}')
            produto.imagens = ','.join(imgs)
        db.session.commit()
        flash('Produto atualizado!', 'success')
        return redirect(url_for('produtores.meus_produtos'))
    return render_template('produtores/editar_meu_produto.html', produto=produto)

@produtores_bp.route('/meus-produtos/<int:id>/excluir', methods=['POST'], endpoint='meus_produtos_excluir')
@login_required
def excluir_meu_produto(id):
    produto = Produto.query.get_or_404(id)
    produtor = Produtor.query.filter_by(usuario_id=current_user.id).first_or_404()
    if produto.produtor_id != produtor.id:
        flash('Você não tem permissão para excluir este produto.', 'danger')
        return redirect(url_for('produtores_bp.meus_produtos'))
    db.session.delete(produto)
    db.session.commit()
    flash('Produto excluído!', 'danger')
    return redirect(url_for('produtores_bp.meus_produtos'))

# ---------------------- Perfil público do produtor ----------------------
@produtores_bp.route('/produtores/<int:produtor_id>', methods=['GET'], endpoint='perfil_publico')
def perfil_publico(produtor_id):
    produtor = Produtor.query.get_or_404(produtor_id)
    produtos = Produto.query.filter_by(produtor_id=produtor.id).order_by(Produto.created_at.desc()).all() if hasattr(Produto, 'created_at') else Produto.query.filter_by(produtor_id=produtor.id).all()
    return render_template('produtores/perfil.html', produtor=produtor, produtos=produtos)