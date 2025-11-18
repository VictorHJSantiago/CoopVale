from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import PontoRetirada
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

@admin_bp.route('/pontos_retirada')
@login_required
@admin_required
def listar_pontos():
    pontos = PontoRetirada.query.all()
    return render_template('admin/pontos_retirada.html', pontos=pontos)

@admin_bp.route('/pontos_retirada/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_ponto():
    if request.method == 'POST':
        nome = request.form['nome']
        endereco = request.form['endereco']
        dias_funcionamento = request.form['dias_funcionamento']
        horarios = request.form['horarios']
        ponto = PontoRetirada(nome=nome, endereco=endereco, dias_funcionamento=dias_funcionamento, horarios=horarios)
        db.session.add(ponto)
        db.session.commit()
        flash('Ponto de retirada cadastrado!', 'success')
        return redirect(url_for('admin_bp.listar_pontos'))
    return render_template('admin/novo_ponto.html')

@admin_bp.route('/pontos_retirada/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_ponto(id):
    ponto = PontoRetirada.query.get_or_404(id)
    if request.method == 'POST':
        ponto.nome = request.form['nome']
        ponto.endereco = request.form['endereco']
        ponto.dias_funcionamento = request.form['dias_funcionamento']
        ponto.horarios = request.form['horarios']
        db.session.commit()
        flash('Ponto de retirada atualizado!', 'info')
        return redirect(url_for('admin_bp.listar_pontos'))
    return render_template('admin/editar_ponto.html', ponto=ponto)

@admin_bp.route('/pontos_retirada/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_ponto(id):
    ponto = PontoRetirada.query.get_or_404(id)
    db.session.delete(ponto)
    db.session.commit()
    flash('Ponto de retirada excluído!', 'danger')
    return redirect(url_for('admin_bp.listar_pontos'))
