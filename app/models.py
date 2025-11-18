from app.extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash 

# --- Entidades Core (Seção 5 do Plano de Ação) ---

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    # Tipo de usuário: 'admin', 'produtor', 'cliente', 'visitante'
    tipo_usuario = db.Column(db.String(50), nullable=False, default='visitante') 
    ativo = db.Column(db.Boolean, default=True)

    # Relacionamentos 1:1 com Produtor e Cliente
    produtor_perfil = db.relationship('Produtor', backref='usuario', uselist=False, lazy=True)
    cliente_perfil = db.relationship('Cliente', backref='usuario', uselist=False, lazy=True)

    def set_senha(self, senha): 
        # RNF04: Cria o hash da senha usando bcrypt
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha): 
        # RNF04: Verifica a senha fornecida com o hash
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.email}>'


class Produtor(db.Model):
    __tablename__ = 'produtores'
    
    id = db.Column(db.Integer, primary_key=True)
    # Relacionamento 1:1 com Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    certificacoes = db.Column(db.Text) 
    
    # Relacionamento 1:N: Produtor tem vários Produtos
    produtos = db.relationship('Produto', backref='produtor', lazy=True)

    def __repr__(self):
        return f'<Produtor {self.nome}>'


class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    # Relacionamento 1:1 com Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    # RF09.3: Endereços salvos (armazenado como texto simples/JSON por enquanto)
    enderecos = db.Column(db.Text) 
    
    # Relacionamento 1:N: Cliente faz vários Pedidos
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'


class Categoria(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    icone = db.Column(db.String(100)) 
    
    # Relacionamento 1:N: Categoria tem vários Produtos
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Produto(db.Model):
    __tablename__ = 'produtos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False) 
    unidade = db.Column(db.String(20)) # RF03.1: ex: kg, un, l
    estoque = db.Column(db.Float, default=0.0)
    imagens = db.Column(db.Text) # RF03.2: Caminhos das imagens (separados por ;)
    
    # Chaves Estrangeiras para Produtor e Categoria
    produtor_id = db.Column(db.Integer, db.ForeignKey('produtores.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

    def __repr__(self):
        return f'<Produto {self.nome}>'


class PontoRetirada(db.Model):
    __tablename__ = 'pontos_retirada'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    # RF06.2: Dias e horários de funcionamento
    dias_funcionamento = db.Column(db.String(100))
    horarios = db.Column(db.String(100))

    def __repr__(self):
        return f'<PontoRetirada {self.nome}>'


class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    # RF05.1: Status do pedido
    status = db.Column(db.String(50), default='Aguardando confirmação') 
    # RF04.4: Forma de pagamento
    forma_pagamento = db.Column(db.String(50))
    # RF04.5: Tipo de recebimento (Entrega ou Retirada)
    tipo_recebimento = db.Column(db.String(50)) 
    total = db.Column(db.Float, default=0.0)
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    
    # Adicional para RF04.6 (Agendamento)
    data_agendada = db.Column(db.DateTime) 

    # Relacionamento 1:N com ItemPedido
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)

    def __repr__(self):
        return f'<Pedido {self.id} - {self.status}>'


class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False) 
    
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    
    # Relacionamento para acessar os dados do produto a partir do item (necessário para RF05.3 - Divisão por produtor)
    produto = db.relationship('Produto') 

    def __repr__(self):
        return f'<Item ProdutoID:{self.produto_id} x {self.quantidade}>'