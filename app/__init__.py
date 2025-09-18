# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"   # rota de login

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object("config")

    db.init_app(app)
    login_manager.init_app(app)

    # Importa models para o db.create_all encontrar as tabelas
    from . import models
    from .routes import bp as main_bp
    from .routes_auth import bp as auth_bp  # ver arquivo abaixo

    app.register_blueprint(main_bp)   # rotas públicas/privadas do app
    app.register_blueprint(auth_bp)   # rotas de autenticação

    with app.app_context():
        db.create_all()

    return app

# >>>>> OBRIGATÓRIO: quem carrega o usuário da sessão <<<<<
@login_manager.user_loader
def load_user(user_id: str):
    from .models import User
    return User.query.get(int(user_id))
