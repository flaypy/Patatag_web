import os
from datetime import timedelta

class Config:
    """Configurações da aplicação"""

    # Secret key para sessões
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Configuração do banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///patatag.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuração de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # CORS
    CORS_HEADERS = 'Content-Type'

    # Paginação
    LOCATIONS_PER_PAGE = 100

    # Tempo máximo sem receber dados para considerar o dispositivo offline (em minutos)
    DEVICE_OFFLINE_TIMEOUT = 15
