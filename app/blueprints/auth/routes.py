from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from app.extensions import db
from app.models.core import Usuario, Produtor, Cliente
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'], endpoint='login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = Usuario.query.filter_by(email=email).first()
        if user and user.check_senha(senha):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main_bp.index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout', endpoint='logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'], endpoint='register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']
        nome = request.form['nome']
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'warning')
            return redirect(url_for('auth.register'))
            
        user = Usuario(email=email, tipo_usuario=tipo_usuario)
        user.set_senha(senha)
        db.session.add(user)
        db.session.commit()
        
        if tipo_usuario == 'produtor':
            produtor = Produtor(usuario_id=user.id, nome=nome, cpf='00000000000')
            db.session.add(produtor)
        elif tipo_usuario == 'cliente':
            cliente = Cliente(usuario_id=user.id, nome=nome, cpf='00000000000')
            db.session.add(cliente)
            
        db.session.commit()
        flash('Cadastro realizado! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/reset_password', methods=['GET', 'POST'], endpoint='reset_password_request')
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = Usuario.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Link de redefinição: {reset_url}', 'info')
        else:
            flash('E-mail não encontrado.', 'warning')
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'], endpoint='reset_password')
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset', max_age=3600)
    except Exception:
        flash('Link inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))
    
    user = Usuario.query.filter_by(email=email).first()
    if not user:
        flash('Usuário não encontrado.', 'danger')
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        senha = request.form['senha']
        user.set_senha(senha)
        db.session.commit()
        flash('Senha redefinida com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/perfil', methods=['GET', 'POST'], endpoint='perfil')
@login_required
def perfil():
    if request.method == 'POST':
        cpf = request.form.get('cpf', '').strip()
        # Validação: CPF deve conter apenas números
        if cpf and not cpf.isdigit():
            flash('CPF deve conter apenas números.', 'warning')
            return redirect(url_for('auth.perfil'))
        if cpf and len(cpf) != 11:
            flash('CPF deve ter 11 dígitos.', 'warning')
            return redirect(url_for('auth.perfil'))
        
        current_user.cpf = cpf if cpf else None
        
        # Upload de foto
        from werkzeug.utils import secure_filename
        import os
        foto = request.files.get('foto_perfil')
        if foto and foto.filename:
            filename = secure_filename(foto.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'perfil')
            os.makedirs(upload_folder, exist_ok=True)
            filepath = os.path.join(upload_folder, f"{current_user.id}_{filename}")
            foto.save(filepath)
            current_user.foto_perfil = f"uploads/perfil/{current_user.id}_{filename}"
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('auth.perfil'))
    
    # Gerar avatar aleatório se não houver foto
    if not current_user.foto_perfil:
        import hashlib
        hash_email = hashlib.md5(current_user.email.encode()).hexdigest()
        avatar_url = f"https://www.gravatar.com/avatar/{hash_email}?d=identicon&s=200"
        avatar_gerado = avatar_url
    else:
        avatar_gerado = None
    
    return render_template('auth/perfil.html', avatar_gerado=avatar_gerado)