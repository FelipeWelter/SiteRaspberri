# app/__init__.py
from flask import Flask
from .extensions import db, login_manager, migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    migrate.init_app(app, db)

    # Importa models para o Alembic enxergar
    from . import models  # noqa: F401
    from .models import User  # precisamos do User para o loader

    # >>>>>>>>>>>>  USER LOADER (ESSENCIAL) <<<<<<<<<<<<<
    @login_manager.user_loader
    def load_user(user_id: str):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    # Blueprints
    from .routes_auth import bp as auth_bp
    from .routes_inventory import bp as inv_bp
    from .routes_users import bp as admin_bp
    from .routes import bp as main_bp  # precisa ter / e /dashboard

    app.register_blueprint(auth_bp)
    app.register_blueprint(inv_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(main_bp)

    return app

