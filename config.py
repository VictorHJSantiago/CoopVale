import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-muito-secreta-dev'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    INSTANCE_DIR = os.path.join(BASEDIR, 'instance')
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    DB_PATH = os.path.join(INSTANCE_DIR, 'coopvale.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Upload de arquivos
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    
    # Configurações de Pagamento - Mercado Pago
    MERCADOPAGO_ACCESS_TOKEN = os.environ.get('MERCADOPAGO_ACCESS_TOKEN')
    MERCADOPAGO_PUBLIC_KEY = os.environ.get('MERCADOPAGO_PUBLIC_KEY')
    MERCADOPAGO_WEBHOOK_SECRET = os.environ.get('MERCADOPAGO_WEBHOOK_SECRET')
    
    # URL base para webhooks (produção)
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', 'http://localhost:5000')
    
    # Criptografia de dados sensíveis
    ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
    
    # Configurações de Email
    MAIL_ENABLED = os.environ.get('MAIL_ENABLED', 'False').lower() == 'true'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@agrofeira.com')