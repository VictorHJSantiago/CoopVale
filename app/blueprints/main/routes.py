from flask import render_template
from . import main_bp

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/sobre')
def sobre():
    return render_template('main/sobre.html')

@main_bp.route('/produtores')
def produtores():
    return render_template('main/produtores.html')

@main_bp.route('/blog')
def blog():
    return render_template('main/blog.html')

@main_bp.route('/contato')
def contato():
    return render_template('main/contato.html')
