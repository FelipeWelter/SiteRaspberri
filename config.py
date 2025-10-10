# config.py
import os
from datetime import timedelta

class Config:
    # 🔑 
    APPLICATION_ROOT = '/clsite'
    SECRET_KEY = "22107dd3d6ca53feda551ef8e6bfbeb02b4681e975bae7daf52b65e2ed40386a"

    # Banco SQLite na pasta instance/
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuração de sessão/cookies
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = timedelta(hours=8)

    # Em produção, com HTTPS, mude para True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False

    APP_NAME = "SISTEMA DE CONTROLE DE MATERIAL"

    APP_VERSION = "1.2.4"
