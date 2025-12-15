# app/utils.py
from functools import wraps
from flask import abort, flash, redirect, request, url_for
from flask_login import login_required, current_user

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if getattr(current_user, "role", None) != "admin":
            # se preferir, pode usar abort(403)
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect(url_for("main.dashboard"))
        return fn(*args, **kwargs)
    return wrapper

def class_required(classe: str, allow_view_all: bool = False):
    """Restringe acesso a uma classe (ex.: 'CL2', 'CL6', 'CL7').
       Admin e 'all' sempre entram.
       Para role='user' ou 'viewer', verifica permissões por classe do usuário.

       Se ``allow_view_all`` for ``True``, usuários com perfil ``viewer``
       podem acessar rotas de leitura de qualquer classe (GET/HEAD/OPTIONS),
       mantendo as restrições de edição apenas às classes atribuídas.
    """
    classe = (classe or "").strip().upper()

    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            role = getattr(current_user, "role", "")
            if role in ("admin", "all"):
                return fn(*args, **kwargs)

            # Visualizador: pode acessar qualquer classe para rotas de leitura
            if (
                role == "viewer"
                and allow_view_all
                and request.method in ("GET", "HEAD", "OPTIONS")
            ):
                return fn(*args, **kwargs)

            # Suporta tanto relacionamento (user.classes -> objetos com .classe)
            # quanto string CSV (user.classes -> "CL2,CL6")
            perms = []
            cu_classes = getattr(current_user, "classes", None)

            try:
                # relacionamento (lista de objetos)
                perms = [c.classe.upper() for c in cu_classes]  # type: ignore[attr-defined]
            except Exception:
                # fallback CSV
                if isinstance(cu_classes, str):
                    perms = [c.strip().upper() for c in cu_classes.split(",") if c.strip()]

            if classe in perms:
                return fn(*args, **kwargs)

            flash(
                "Você não tem permissão para acessar esta página.",
                "danger",
            )
            return redirect(url_for("main.dashboard"))  # ou abort(403)
        return wrapper
    return decorator
