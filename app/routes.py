# app/routes.py
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint("main", __name__)  # <- nome do blueprint = "main"

@bp.route("/")
def index():
    # se logado, manda pro dashboard; senão, pro login
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))

@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# util p/ testar disponibilidade sem login
@bp.route("/healthz")
def healthz():
    return "ok", 200
