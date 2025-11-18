from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin # Recomendado pelo RNF01 para autenticação

# Instância do banco de dados (geralmente criada aqui ou no __init__.py e importada)
db = SQLAlchemy()

# --- Entidades Core ---

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    # Tipo de usuário: 'admin', 'produtor', 'cliente', 'visitante'
    tipo_usuario = db.Column(db.String(50), nullable=False, default='visitante') 
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos 1:1 (One-to-One)
    produtor_perfil = db.relationship('Produtor', backref='usuario', uselist=False, lazy=True)
    cliente_perfil = db.relationship('Cliente', backref='usuario', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Produtor(db.Model):
    __tablename__ = 'produtores'
    
    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira ligando ao Usuário (1:1)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    certificacoes = db.Column(db.Text) # Pode ser texto livre ou lista separada por vírgulas
    
    # Relacionamento 1:N (Um produtor tem vários produtos)
    produtos = db.relationship('Produto', backref='produtor', lazy=True)

    def __repr__(self):
        return f'<Produtor {self.nome}>'


class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    # Chave estrangeira ligando ao Usuário (1:1)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    enderecos = db.Column(db.Text) # Pode ser melhorado criando uma tabela separada de endereços futuramente
    
    # Relacionamento 1:N (Um cliente faz vários pedidos)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    icone = db.Column(db.String(100)) # Caminho da imagem ou classe de ícone (ex: fontawesome)
    
    # Relacionamento 1:N (Uma categoria tem vários produtos)
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False) # Considere usar Decimal para valores monetários em produção
    unidade = db.Column(db.String(20)) # ex: kg, un, l
    estoque = db.Column(db.Float, default=0.0)
    imagens = db.Column(db.Text) # Caminhos das imagens separados por ; ou JSON
    
    # Chaves Estrangeiras
    produtor_id = db.Column(db.Integer, db.ForeignKey('produtores.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    def __repr__(self):
        return f'<Produto {self.nome}>'


class PontoRetirada(db.Model):
    __tablename__ = 'pontos_retirada'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    dias_funcionamento = db.Column(db.String(100))
    horarios = db.Column(db.String(100))


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Aguardando confirmação') # RF05.1
    forma_pagamento = db.Column(db.String(50))
    tipo_recebimento = db.Column(db.String(50)) # Entrega ou Retirada
    total = db.Column(db.Float, default=0.0)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Relacionamento 1:N com ItemPedido
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)

    def __repr__(self):
        return f'<Pedido {self.id} - {self.status}>'


class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False) # Preço no momento da compra
    
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    
    # Relacionamento para acessar os dados do produto a partir do item
    produto = db.relationship('Produto')

    def __repr__(self):
        return f'<Item {self.produto.nome} x {self.quantidade}>'