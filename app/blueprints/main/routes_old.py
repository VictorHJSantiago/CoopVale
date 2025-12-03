from flask import render_template
from datetime import datetime
from app.models.core import Produtor
from . import main_bp

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/sobre')
def sobre():
    return render_template('main/sobre.html')

@main_bp.route('/produtores')
def produtores():
    produtores = Produtor.query.filter(Produtor.descricao != None).all()
    return render_template('main/produtores.html', produtores=produtores)

@main_bp.route('/blog')
def blog():
    return render_template('main/blog.html')

@main_bp.route('/contato')
def contato():
    return render_template('main/contato.html')

@main_bp.route('/faq')
def faq():
    return render_template('institucional/faq.html')

@main_bp.route('/privacidade')
def privacidade():
    return render_template('institucional/privacidade.html', now=datetime.now())

@main_bp.route('/termos')
def termos():
    return render_template('institucional/termos.html', now=datetime.now())