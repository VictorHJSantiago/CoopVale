from itsdangerous import URLSafeTimedSerializer
from flask import current_app
# Recuperação de senha - solicitar
@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    if request.method == 'POST':
        email = request.form['email']
        user = Usuario.query.filter_by(email=email).first()
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='password-reset')
            # Aqui seria enviado o e-mail real. Para dev, exibe o link na tela:
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            flash(f'Link de redefinição: {reset_url}', 'info')
        else:
            flash('E-mail não encontrado.', 'warning')
    return render_template('auth/reset_password_request.html')

# Recuperação de senha - redefinir
@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
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
        user.senha_hash = generate_password_hash(senha)
        db.session.commit()
        flash('Senha redefinida com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token)
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.core import Usuario, Produtor, Cliente
from . import auth_bp

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = Usuario.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha_hash, senha):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('main_bp.index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        tipo_usuario = request.form['tipo_usuario']
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'warning')
            return redirect(url_for('auth.register'))
        user = Usuario(email=email, senha_hash=generate_password_hash(senha), tipo_usuario=tipo_usuario)
        db.session.add(user)
        db.session.commit()
        # Cria perfil de produtor ou cliente
        if tipo_usuario == 'produtor':
            produtor = Produtor(usuario_id=user.id, nome=request.form.get('nome', ''))
            db.session.add(produtor)
        elif tipo_usuario == 'cliente':
            cliente = Cliente(usuario_id=user.id, nome=request.form.get('nome', ''))
            db.session.add(cliente)
        db.session.commit()
        flash('Cadastro realizado! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')
