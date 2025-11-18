from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.core import Produtor
from . import produtores_bp

@produtores_bp.route('/produtores')
@login_required
def listar_produtores():
    produtores = Produtor.query.all()
    return render_template('produtores/produtores.html', produtores=produtores)

@produtores_bp.route('/produtores/novo', methods=['GET', 'POST'])
@login_required
def novo_produtor():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        certificacoes = request.form['certificacoes']
        descricao = request.form['descricao']
        fotos = request.form['fotos']
        produtor = Produtor(
            nome=nome,
            cpf=cpf,
            telefone=telefone,
            endereco=endereco,
            certificacoes=certificacoes,
            descricao=descricao,
            fotos=fotos,
            usuario_id=current_user.id
        )
        db.session.add(produtor)
        db.session.commit()
        flash('Produtor cadastrado com sucesso!', 'success')
        return redirect(url_for('produtores_bp.listar_produtores'))
    return render_template('produtores/novo_produtor.html')

@produtores_bp.route('/produtores/<int:id>/editar', methods=['GET', 'POST'])
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
        produtor.fotos = request.form['fotos']
        db.session.commit()
        flash('Produtor atualizado!', 'info')
        return redirect(url_for('produtores_bp.listar_produtores'))
    return render_template('produtores/editar_produtor.html', produtor=produtor)

@produtores_bp.route('/produtores/<int:id>/excluir', methods=['POST'])
@login_required
def excluir_produtor(id):
    produtor = Produtor.query.get_or_404(id)
    db.session.delete(produtor)
    db.session.commit()
    flash('Produtor excluído!', 'danger')
    return redirect(url_for('produtores_bp.listar_produtores'))
