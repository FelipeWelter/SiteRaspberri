from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, current_user, login_required
from email.message import EmailMessage
import smtplib
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from .models import db, User
from .forms import RegisterForm, ForgotPasswordForm, ResetPasswordForm

bp = Blueprint("auth", __name__, url_prefix="")


def _password_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def _send_reset_email(user: User) -> None:
    token = _password_serializer().dumps(
        user.email,
        salt=current_app.config["PASSWORD_RESET_SALT"],
    )
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    sender = current_app.config.get("MAIL_DEFAULT_SENDER") or current_app.config.get("MAIL_USERNAME")
    if not sender or not current_app.config.get("MAIL_USERNAME") or not current_app.config.get("MAIL_PASSWORD"):
        raise RuntimeError("Configuração de e-mail incompleta")

    msg = EmailMessage()
    msg["Subject"] = "Recuperação de senha - Sistema de Controle de Material"
    msg["From"] = sender
    msg["To"] = user.email
    msg.set_content(
        f"Olá, {user.full_name}!\n\n"
        f"Recebemos uma solicitação para redefinir sua senha.\n"
        f"Acesse o link abaixo para criar uma nova senha:\n{reset_url}\n\n"
        f"Este link expira em {current_app.config['PASSWORD_RESET_MAX_AGE'] // 60} minutos."
    )

    server = current_app.config.get("MAIL_SERVER")
    port = current_app.config.get("MAIL_PORT")
    username = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")

    if current_app.config.get("MAIL_USE_SSL"):
        with smtplib.SMTP_SSL(server, port) as smtp:
            smtp.login(username, password)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(server, port) as smtp:
            if current_app.config.get("MAIL_USE_TLS"):
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(msg)

@bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        user = User.query.filter_by(username=u, active=True).first()
        if user and user.check_password(p):
            login_user(user, remember=False)
            return redirect(url_for("main.dashboard"))
        flash("Usuário ou senha inválidos.", "danger")
    return render_template("login.html")

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegisterForm()
    if form.validate_on_submit():
        # checa username duplicado
        if User.query.filter_by(username=form.username.data).first():
            flash("Este login já está em uso.", "warning")
            return render_template("register.html", form=form)

        u = User(
            full_name=form.full_name.data,
            username=form.username.data,
            email=form.email.data.lower().strip(),
            identity=form.identity.data or None,
            role="user",
            active=False,  # exige aprovação do admin
        )

        if User.query.filter_by(email=u.email).first():
            flash("Este e-mail já está em uso.", "warning")
            return render_template("register.html", form=form)

        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()

        flash("Conta criada com sucesso! Aguarde aprovação do administrador.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email, active=True).first()

        if user:
            try:
                _send_reset_email(user)
            except Exception:
                current_app.logger.exception("Falha ao enviar e-mail de recuperação")
                flash("Não foi possível enviar o e-mail de recuperação agora.", "danger")
                return render_template("forgot_password.html", form=form)

        flash("Se o e-mail estiver cadastrado, você receberá instruções de recuperação.", "info")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html", form=form)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    try:
        email = _password_serializer().loads(
            token,
            salt=current_app.config["PASSWORD_RESET_SALT"],
            max_age=current_app.config["PASSWORD_RESET_MAX_AGE"],
        )
    except SignatureExpired:
        flash("O link de recuperação expirou. Solicite um novo.", "warning")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Link de recuperação inválido.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email, active=True).first()
    if not user:
        flash("Conta não encontrada para este link.", "danger")
        return redirect(url_for("auth.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Senha redefinida com sucesso. Faça login novamente.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", form=form)
