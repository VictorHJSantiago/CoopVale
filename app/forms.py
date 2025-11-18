from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from app.models import Usuario

class LoginForm(FlaskForm): # RF01.2
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    lembrar_me = BooleanField('Lembrar-me')
    submit = SubmitField('Login')

class CadastroForm(FlaskForm): # RF01.1
    email = StringField('Email', validators=[DataRequired(), Email()])
    tipo_usuario = SelectField('Eu sou', choices=[('cliente', 'Cliente'), ('produtor', 'Produtor')], validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirma_senha = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Cadastrar')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Este email já está cadastrado.')

class ProdutoForm(FlaskForm): # RF03.1
    nome = StringField('Nome do Produto', validators=[DataRequired(), Length(max=150)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    preco = FloatField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0.01)])
    unidade = StringField('Unidade de Medida (ex: kg, un, L)', validators=[DataRequired(), Length(max=20)])
    estoque = FloatField('Estoque Atual', default=0.0, validators=[NumberRange(min=0)])
    # categoria_id será populado dinamicamente na rota
    categoria_id = SelectField('Categoria', coerce=int, validators=[DataRequired()]) 
    submit = SubmitField('Salvar Produto')