# app/utils.py
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import login_required, current_user

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if getattr(current_user, "role", None) != "admin":
            # se preferir, pode usar abort(403)
            return redirect(url_for("main.dashboard"))
        return fn(*args, **kwargs)
    return wrapper

def class_required(classe: str):
    """Restringe acesso a uma classe (ex.: 'CL2', 'CL6', 'CL7').
       Admin e 'all' sempre entram.
       Para role='user', verifica permissões por classe do usuário.
    """
    classe = (classe or "").strip().upper()

    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            role = getattr(current_user, "role", "")
            if role in ("admin", "all"):
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

            return redirect(url_for("main.dashboard"))  # ou abort(403)
        return wrapper
    return decorator
