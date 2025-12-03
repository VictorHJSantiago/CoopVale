from flask import render_template, redirect, url_for, request, flash
from app.extensions import db
from app.models.core import Produtor, Contato
from datetime import datetime
from app.models.core import Produtor
from . import main_bp

@main_bp.route('/', endpoint='index')
def index():
    return render_template('main/index.html')

@main_bp.route('/sobre', endpoint='sobre')
def sobre():
    return render_template('main/sobre.html')

@main_bp.route('/produtores', endpoint='produtores')
def produtores():
    q = request.args.get('q','').strip()
    cidade = request.args.get('cidade','').strip()
    estado = request.args.get('estado','').strip()
    query = Produtor.query
    if q:
        query = query.filter(Produtor.nome.ilike(f'%{q}%'))
    if cidade:
        query = query.filter(Produtor.cidade.ilike(f'%{cidade}%'))
    if estado:
        query = query.filter(Produtor.estado.ilike(f'%{estado}%'))
    produtores = query.order_by(Produtor.nome.asc()).all()
    return render_template('main/produtores.html', produtores=produtores)

@main_bp.route('/blog', endpoint='blog_redirect')
def blog():
    # Redireciona para o blueprint do blog
    return redirect(url_for('blog.index'))

@main_bp.route('/contato', endpoint='contato')
def contato():
    return render_template('main/contato.html')

@main_bp.route('/contato', methods=['POST'], endpoint='enviar_contato')
def enviar_contato():
    nome = request.form.get('nome')
    email = request.form.get('email')
    mensagem = request.form.get('mensagem')
    if not (nome and email and mensagem):
        flash('Preencha todos os campos.', 'warning')
        return redirect(url_for('main_bp.contato'))
    try:
        registro = Contato(nome=nome, email=email, mensagem=mensagem)
        db.session.add(registro)
        db.session.commit()
        flash('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success')
    except Exception:
        flash('Não foi possível registrar sua mensagem agora. Tente novamente mais tarde.', 'danger')
    return redirect(url_for('main_bp.contato'))

@main_bp.route('/faq', endpoint='faq')
def faq():
    return render_template('institucional/faq.html')

@main_bp.route('/privacidade', endpoint='privacidade')
def privacidade():
    return render_template('institucional/privacidade.html', now=datetime.now())

@main_bp.route('/termos', endpoint='termos')
def termos():
    return render_template('institucional/termos.html', now=datetime.now())
