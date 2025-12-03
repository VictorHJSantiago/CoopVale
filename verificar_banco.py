from app import create_app
from app.models.core import Usuario, Produto, Categoria, PontoRetirada, TaxaEntrega
from app.extensions import db

app = create_app()
app.app_context().push()

print('=' * 60)
print('ESTATISTICAS DO BANCO DE DADOS')
print('=' * 60)
print(f'Usuarios: {Usuario.query.count()}')
print(f'Produtos: {Produto.query.count()}')
print(f'Categorias: {Categoria.query.count()}')
print(f'Pontos de Retirada: {PontoRetirada.query.count()}')
print(f'Taxas de Entrega: {TaxaEntrega.query.count()}')
print('=' * 60)
