# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class UserClass(db.Model):
    __tablename__ = "user_classes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    classe = db.Column(db.String(10), nullable=False)  # ex.: "CL2", "CL6", "CL7"

    __table_args__ = (
        db.UniqueConstraint("user_id", "classe", name="uq_userclass_user_classe"),
    )

# ---------- Usuários e Permissões por Classe ----------

class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    identity = db.Column(db.String(50))  # identidade funcional, se desejar
    role = db.Column(db.String(20), default="user")  # "admin", "all", "user"
    active = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relacionamento 1-N com UserClass (permissões por classe)
    classes = db.relationship(
        "UserClass",
        backref="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ---- helpers de senha ----
    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ---- regra de acesso por classe ----
    def can_access(self, classe: str) -> bool:
        """Admin e 'all' sempre entram. Para 'user', verifica permissões por classe."""
        if not self.active:
            return False
        cls = (classe or "").strip().upper()
        if self.role in ("admin", "all"):
            return True

        # relacionamento com UserClass
        try:
            perms = [c.classe.upper() for c in (self.classes or [])]
        except Exception:
            perms = []

        return cls in perms
    

    # CLASSE 1 - RAÇÕES

class CL1(db.Model):
    __tablename__ = "cl1"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # RA, R2, R3
    quantidade = db.Column(db.Integer, nullable=False)
    validade = db.Column(db.Date, nullable=False)
    cardapio1 = db.Column(db.Text)
    cardapio2 = db.Column(db.Text)
    cardapio3 = db.Column(db.Text)
    cardapio4 = db.Column(db.Text)
    menu_atual = db.Column(db.String(20))
    lote = db.Column(db.String(120))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    logs = db.relationship(
        "CL1Log",
        backref="cl1",
        cascade="all, delete-orphan",
        order_by="desc(CL1Log.criado_em)",
    )

    def __repr__(self):
        return f"<CL1 {self.tipo} - {self.quantidade} - {self.validade}>"


class CL1Log(db.Model):
    __tablename__ = "cl1_logs"

    id = db.Column(db.Integer, primary_key=True)
    cl1_id = db.Column(
        db.Integer, db.ForeignKey("cl1.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_name = db.Column(db.String(120))
    motivo = db.Column(db.Text, nullable=False)
    dados_antes = db.Column(db.JSON)
    dados_depois = db.Column(db.JSON)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class CL2(db.Model):
    __tablename__ = "cl2"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # auto
    nome = db.Column(db.String(120), nullable=False)
    situacao = db.Column(db.String(30), default="OK")
    qtd_prevista = db.Column(db.Integer, default=0)
    qtd_disp = db.Column(db.Integer, default=0)
    qtd_indisp = db.Column(db.Integer, default=0)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)




# ATUALIZAÇÃO CLASSE 6 --------------
class CL6(db.Model):
    __tablename__ = "cl6"


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


    # Novos campos padronizados
    situacao_patrimonial = db.Column(db.String(20), nullable=False, default="em carga") # em carga | fora de carga
    codot_item_material = db.Column(db.String(120))
    numero_patrimonio_material = db.Column(db.String(120))
    ano_fabricacao = db.Column(db.Integer)
    disponibilidade = db.Column(db.String(30)) # ex.: Disponível | Indisponível
    categoria = db.Column(db.String(20)) # construcao | combate
    valor_inclusao_carga = db.Column(db.Numeric(12, 2), default=0)
    localizacao_atual = db.Column(db.String(120))


    # Mantidos
    marca = db.Column(db.String(120))
    modelo = db.Column(db.String(120))
    numero_serie = db.Column(db.String(120))


    # Metadados
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CL7(db.Model):
    __tablename__ = "cl7"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material = db.Column(db.String(120), nullable=False)
    marca = db.Column(db.String(120))
    modelo = db.Column(db.String(120))
    numero_serie = db.Column(db.String(120))
    situacao = db.Column(db.String(30), default="OK")
    observacao = db.Column(db.Text)
    pelotao = db.Column(db.String(20), nullable=True, index=True, default="1º PELOTAO") #1 PEL
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)