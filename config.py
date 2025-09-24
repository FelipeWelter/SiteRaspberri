# config.py
import os
from datetime import timedelta

class Config:
    # 🔑 Chave provisória (troque em produção)
    SECRET_KEY = "teste123"

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
    APP_VERSION = "1.1"