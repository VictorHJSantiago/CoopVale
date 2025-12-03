import os
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.core import PostBlog, ComentarioBlog, Usuario
from app.blueprints.admin.routes import admin_required
from . import blog_bp
from datetime import datetime, timezone
def produtor_ou_admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario not in ['produtor','admin']:
            flash('Apenas produtores ou administradores podem acessar.', 'danger')
            return redirect(url_for('main_bp.index'))
        return f(*args, **kwargs)
    return wrapper

@blog_bp.route('/novo', methods=['GET','POST'], endpoint='novo_produtor_post')
@login_required
@produtor_ou_admin_required
def novo_produtor_post():
    """Cria um post no blog por produtores/admin"""
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        slug = criar_slug(titulo)
        if PostBlog.query.filter_by(slug=slug).first():
            slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        imagem_capa = None
        if 'imagem_capa' in request.files:
            file = request.files['imagem_capa']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'blog')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                imagem_capa = f'uploads/blog/{filename}'
        post = PostBlog(
            titulo=titulo,
            slug=slug,
            conteudo=request.form.get('conteudo'),
            resumo=request.form.get('resumo'),
            categoria=request.form.get('categoria'),
            autor_id=current_user.id,
            imagem_capa=imagem_capa,
            publicado=True
        )
        db.session.add(post)
        db.session.commit()
        flash('Matéria publicada com sucesso!', 'success')
        return redirect(url_for('blog.index'))
    return render_template('blog/admin/novo_post.html')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def criar_slug(titulo):
    """Cria um slug a partir do título"""
    import unicodedata
    import re
    # Normaliza unicode e remove acentos
    titulo = unicodedata.normalize('NFKD', titulo).encode('ascii', 'ignore').decode('ascii')
    # Converte para minúsculas e substitui espaços por hífens
    slug = re.sub(r'[^\w\s-]', '', titulo.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

# Rotas públicas
@blog_bp.route('/', endpoint='index')
def index():
    """Lista todos os posts publicados"""
    categoria = request.args.get('categoria')
    query = PostBlog.query.filter_by(publicado=True) 
    if categoria:
        query = query.filter_by(categoria=categoria)
    posts = query.order_by(PostBlog.criado_em.desc()).all()
    return render_template('blog/index.html', posts=posts, categoria_selecionada=categoria)

@blog_bp.route('/<slug>', endpoint='ver_post')
def ver_post(slug):
    """Exibe um post específico"""
    post = PostBlog.query.filter_by(slug=slug, publicado=True).first_or_404() 
    comentarios = ComentarioBlog.query.filter_by(post_id=post.id).order_by(ComentarioBlog.criado_em.desc()).all()
    return render_template('blog/ver_post.html', post=post, comentarios=comentarios)

@blog_bp.route('/<slug>/comentar', methods=['POST'], endpoint='adicionar_comentario')
@login_required
def adicionar_comentario(slug):
    """Adiciona comentário em um post"""
    post = PostBlog.query.filter_by(slug=slug).first_or_404() 
    comentario_texto = request.form.get('comentario')
    if comentario_texto:
        comentario = ComentarioBlog(
            post_id=post.id,
            usuario_id=current_user.id,
            comentario=comentario_texto
        )
        db.session.add(comentario)
        db.session.commit()
        flash('Comentário adicionado com sucesso!', 'success')
    return redirect(url_for('blog.ver_post', slug=slug))

# Rotas administrativas
@blog_bp.route('/admin/posts', endpoint='listar_posts')
@login_required
@admin_required
def listar_posts():
    """Lista todos os posts para administração"""
    posts = PostBlog.query.order_by(PostBlog.criado_em.desc()).all() 
    return render_template('blog/admin/listar_posts.html', posts=posts)

@blog_bp.route('/admin/posts/novo', methods=['GET', 'POST'], endpoint='novo_post')
@login_required
@admin_required
def novo_post():
    """Cria um novo post"""
    if request.method == 'POST': 
        titulo = request.form.get('titulo')
        slug = criar_slug(titulo)
        
        # Verifica se slug já existe
        if PostBlog.query.filter_by(slug=slug).first():
            slug = f"{slug}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Upload de imagem de capa
        imagem_capa = None
        if 'imagem_capa' in request.files:
            file = request.files['imagem_capa']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'blog')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                imagem_capa = f'uploads/blog/{filename}'
        
        post = PostBlog(
            titulo=titulo,
            slug=slug,
            conteudo=request.form.get('conteudo'),
            resumo=request.form.get('resumo'),
            categoria=request.form.get('categoria'),
            autor_id=current_user.id,
            imagem_capa=imagem_capa,
            publicado=request.form.get('publicado') == 'on'
        )
        db.session.add(post)
        db.session.commit()
        flash('Post criado com sucesso!', 'success')
        return redirect(url_for('blog.listar_posts'))
    
    return render_template('blog/admin/novo_post.html')

@blog_bp.route('/admin/posts/<int:id>/editar', methods=['GET', 'POST'], endpoint='editar_post')
@login_required
@admin_required
def editar_post(id):
    """Edita um post existente"""
    post = PostBlog.query.get_or_404(id) 
    
    if request.method == 'POST':
        post.titulo = request.form.get('titulo')
        post.conteudo = request.form.get('conteudo')
        post.resumo = request.form.get('resumo')
        post.categoria = request.form.get('categoria')
        post.publicado = request.form.get('publicado') == 'on'
        post.atualizado_em = datetime.now(timezone.utc)
        
        # Upload de nova imagem de capa
        if 'imagem_capa' in request.files:
            file = request.files['imagem_capa']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'blog')
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                post.imagem_capa = f'uploads/blog/{filename}'
        
        db.session.commit()
        flash('Post atualizado com sucesso!', 'success')
        return redirect(url_for('blog.listar_posts'))
    
    return render_template('blog/admin/editar_post.html', post=post)

@blog_bp.route('/admin/posts/<int:id>/excluir', methods=['POST'], endpoint='excluir_post')
@login_required
@admin_required
def excluir_post(id):
    """Exclui um post"""
    post = PostBlog.query.get_or_404(id) 
    db.session.delete(post)
    db.session.commit()
    flash('Post excluído com sucesso!', 'danger')
    return redirect(url_for('blog.listar_posts'))

@blog_bp.route('/admin/comentarios', endpoint='listar_comentarios')
@login_required
@admin_required
def listar_comentarios():
    """Lista todos os comentários"""
    comentarios = ComentarioBlog.query.order_by(ComentarioBlog.criado_em.desc()).all() 
    return render_template('blog/admin/listar_comentarios.html', comentarios=comentarios)

@blog_bp.route('/admin/comentarios/<int:id>/excluir', methods=['POST'], endpoint='excluir_comentario')
@login_required
@admin_required
def excluir_comentario(id):
    """Exclui um comentário"""
    comentario = ComentarioBlog.query.get_or_404(id) 
    db.session.delete(comentario)
    db.session.commit()
    flash('Comentário excluído com sucesso!', 'danger')
    return redirect(request.referrer or url_for('blog.listar_comentarios'))
