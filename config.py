# config.py
import os
from datetime import timedelta

class Config:
    # 🔑 
    APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '/')
    SECRET_KEY = "22107dd3d6ca53feda551ef8e6bfbeb02b4681e975bae7daf52b65e2ed40386a"
    SESSION_COOKIE_PATH = os.getenv('SESSION_COOKIE_PATH', '/')

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

    APP_VERSION = "1.4.7"

    # E-mail (SMTP Gmail)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    PASSWORD_RESET_SALT = os.getenv("PASSWORD_RESET_SALT", "password-reset")
    PASSWORD_RESET_MAX_AGE = int(os.getenv("PASSWORD_RESET_MAX_AGE", 3600))

