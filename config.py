import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'uma-chave-muito-secreta-dev'
    # Usando SQLite para desenvolvimento conforme RNF02
    SQLALCHEMY_DATABASE_URI = 'sqlite:///coopvale.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False