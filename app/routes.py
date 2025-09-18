# app/routes.py
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    # Pode ser público por enquanto
    return render_template("dashboard.html")

@bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
