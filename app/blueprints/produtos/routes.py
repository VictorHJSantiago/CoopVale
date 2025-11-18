from flask import render_template
from . import produtos_bp
from app.models import Produto

# Exemplo de Rota de Catálogo (RF03) [cite: 55]
@produtos_bp.route('/')
def catalogo():
    # Busca todos os produtos no banco
    lista_produtos = Produto.query.all()
    return render_template('produtos/catalogo.html', produtos=lista_produtos)

@produtos_bp.route('/detalhe/<int:id>')
def detalhe(id):
    produto = Produto.query.get_or_404(id)
    return render_template('produtos/detalhe.html', produto=produto)