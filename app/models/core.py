from app.extensions import db
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    tipo_usuario = db.Column(db.String(50), nullable=False, default='visitante')
    ativo = db.Column(db.Boolean, default=True)
    cpf = db.Column(db.String(14))
    foto_perfil = db.Column(db.String(300))
    produtor_perfil = db.relationship('Produtor', backref='usuario', uselist=False, lazy=True)
    cliente_perfil = db.relationship('Cliente', backref='usuario', uselist=False, lazy=True)

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def __repr__(self):
        return f'<Usuario {self.email}>'

class Produtor(db.Model):
    __tablename__ = 'produtores'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    certificacoes = db.Column(db.Text)
    descricao = db.Column(db.Text)
    fotos = db.Column(db.Text)
    produtos = db.relationship('Produto', backref='produtor', lazy=True)

    def __repr__(self):
        return f'<Produtor {self.nome}>'

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), unique=True, nullable=False)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    pedidos = db.relationship('Pedido', backref='cliente', lazy=True)
    enderecos = db.relationship('Endereco', backref='cliente', lazy=True)
    notificacoes = db.relationship('Notificacao', backref='cliente', lazy=True)
    favoritos = db.relationship('Favorito', backref='cliente', lazy=True)
    reviews = db.relationship('Review', backref='cliente', lazy=True)

    def __repr__(self):
        return f'<Cliente {self.nome}>'

class Endereco(db.Model):
    __tablename__ = 'enderecos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    apelido = db.Column(db.String(50))
    logradouro = db.Column(db.String(200), nullable=False)
    numero = db.Column(db.String(20))
    complemento = db.Column(db.String(100))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    cep = db.Column(db.String(10), nullable=False)
    principal = db.Column(db.Boolean, default=False)

class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    icone = db.Column(db.String(100))
    valor_minimo = db.Column(db.Float)  # valor mínimo em pedidos dessa categoria
    quantidade_minima = db.Column(db.Float)  # quantidade mínima (unidade base)
    produtos = db.relationship('Produto', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nome}>'

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float, nullable=False)
    unidade = db.Column(db.String(20))
    estoque = db.Column(db.Float, default=0.0)
    imagens = db.Column(db.Text)
    tags = db.Column(db.String(200))
    subcategoria = db.Column(db.String(100))
    origem = db.Column(db.String(150))
    informacoes_nutricionais = db.Column(db.Text)
    preco_promocional = db.Column(db.Float)
    sazonal_inicio = db.Column(db.DateTime)
    sazonal_fim = db.Column(db.DateTime)
    produtor_id = db.Column(db.Integer, db.ForeignKey('produtores.id'), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    reviews = db.relationship('Review', backref='produto', lazy=True)

    def __repr__(self):
        return f'<Produto {self.nome}>'

class PontoRetirada(db.Model):
    __tablename__ = 'pontos_retirada'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    endereco = db.Column(db.Text, nullable=False)
    cidade = db.Column(db.String(100))
    cep = db.Column(db.String(10))
    dias_funcionamento = db.Column(db.String(100))  # Ex: Seg-Sex, Sábado
    horario_abertura = db.Column(db.String(10))  # Ex: 08:00
    horario_fechamento = db.Column(db.String(10))  # Ex: 18:00
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<PontoRetirada {self.nome}>'

class TaxaEntrega(db.Model):
    __tablename__ = 'taxas_entrega'
    id = db.Column(db.Integer, primary_key=True)
    regiao = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    prazo_dias = db.Column(db.Integer, default=1)
    ativo = db.Column(db.Boolean, default=True)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    data = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(50), default='Aguardando confirmação')
    forma_pagamento = db.Column(db.String(50))
    tipo_recebimento = db.Column(db.String(50))
    total = db.Column(db.Float, default=0.0)
    # Logística avançada
    entrega_tipo = db.Column(db.String(20))  # 'retirada' ou 'entrega'
    ponto_retirada_id = db.Column(db.Integer, db.ForeignKey('pontos_retirada.id'))
    taxa_entrega_id = db.Column(db.Integer, db.ForeignKey('taxas_entrega.id'))
    valor_frete = db.Column(db.Float, default=0.0)
    data_agendada = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    data_cancelamento = db.Column(db.DateTime)
    motivo_cancelamento = db.Column(db.Text)
    cancelado_por = db.Column(db.String(50))  # cliente, admin, sistema
    # Campos de pagamento
    pagamento_id = db.Column(db.String(100))  # ID do pagamento no gateway (Mercado Pago, etc)
    status_pagamento = db.Column(db.String(50), default='pendente')  # pendente, aprovado, rejeitado, expirado, reembolsado
    data_pagamento = db.Column(db.DateTime)  # Quando o pagamento foi confirmado
    expiracao_pagamento = db.Column(db.DateTime)  # Quando o pagamento PIX expira
    motivo_rejeicao = db.Column(db.Text)  # Motivo se pagamento foi rejeitado
    token_cartao = db.Column(db.Text)  # Token criptografado do cartão (se aplicável)
    ultimos_4_cartao = db.Column(db.String(4))  # Últimos 4 dígitos do cartão
    bandeira_cartao = db.Column(db.String(50))  # Visa, Mastercard, etc
    itens = db.relationship('ItemPedido', backref='pedido', lazy=True)
    ponto_retirada = db.relationship('PontoRetirada', backref='pedidos', lazy=True)
    taxa_entrega = db.relationship('TaxaEntrega', backref='pedidos', lazy=True)

    def __repr__(self):
        return f'<Pedido {self.id} - {self.status}>'

class ItemPedido(db.Model):
    __tablename__ = 'itens_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    preco_unitario = db.Column(db.Float, nullable=False)
    produto = db.relationship('Produto')

class Notificacao(db.Model):
    __tablename__ = 'notificacoes'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    mensagem = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    criada_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Favorito(db.Model):
    __tablename__ = 'favoritos'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'))
    __table_args__ = (db.UniqueConstraint('cliente_id', 'produto_id', name='uix_cliente_produto'),)

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id'), nullable=False)
    nota = db.Column(db.Integer, nullable=False)  # 1-5
    comentario = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('cliente_id', 'produto_id', name='uix_cliente_produto_review'),)

class PostBlog(db.Model):
    __tablename__ = 'posts_blog'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(250), unique=True, nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    resumo = db.Column(db.String(300))
    categoria = db.Column(db.String(50))  # receitas, dicas, noticias
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    imagem_capa = db.Column(db.String(300))
    publicado = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    autor = db.relationship('Usuario', backref='posts', lazy=True)
    
    def __repr__(self):
        return f'<PostBlog {self.titulo}>'

class ComentarioBlog(db.Model):
    __tablename__ = 'comentarios_blog'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts_blog.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    comentario = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    post = db.relationship('PostBlog', backref='comentarios', lazy=True)
    usuario = db.relationship('Usuario', backref='comentarios_blog', lazy=True)
    
    def __repr__(self):
        return f'<ComentarioBlog {self.id}>'

class Contato(db.Model):
    __tablename__ = 'contatos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    respondido = db.Column(db.Boolean, default=False)