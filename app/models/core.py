class Notificacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)

class Favorito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    __table_args__ = (db.UniqueConstraint('cliente_id', 'produto_id', name='uix_cliente_produto'),)


from app.extensions import db
from datetime import datetime

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False)  # admin, produtor, cliente
    ativo = db.Column(db.Boolean, default=True)
    produtor = db.relationship('Produtor', backref='usuario', uselist=False)
    cliente = db.relationship('Cliente', backref='usuario', uselist=False)

    # Métodos obrigatórios do Flask-Login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.ativo

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Produtor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.String(200))
    certificacoes = db.Column(db.String(200))
    descricao = db.Column(db.Text)
    fotos = db.Column(db.Text)  # lista de URLs separadas por vírgula
    produtos = db.relationship('Produto', backref='produtor', lazy=True)


class Endereco(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    apelido = db.Column(db.String(50))  # Ex: Casa, Trabalho
    logradouro = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    principal = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    enderecos = db.Column(db.Text)  # lista de endereços em JSON (legado)
    enderecos_rel = db.relationship('Endereco', backref='cliente', lazy=True)
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    notificacoes = db.relationship('Notificacao', backref='cliente', lazy=True)

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200))
    icone = db.Column(db.String(100))
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(10), nullable=False)
    produtor_id = db.Column(db.Integer, db.ForeignKey('produtor.id'))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'))
    estoque = db.Column(db.Integer, default=0)
    imagens = db.Column(db.Text)  # lista de URLs separadas por vírgula
    tags = db.Column(db.String(200))
    itens_pedido = db.relationship('ItemPedido', backref='produto', lazy=True)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(30), default='Aguardando confirmação')
    forma_pagamento = db.Column(db.String(30))
    tipo_recebimento = db.Column(db.String(30))
    total = db.Column(db.Float)
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)
    data_agendada = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)

class ItemPedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    quantidade = db.Column(db.Integer, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)

class PontoRetirada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    endereco = db.Column(db.String(200))
    dias_funcionamento = db.Column(db.String(100))
    horarios = db.Column(db.String(100))
