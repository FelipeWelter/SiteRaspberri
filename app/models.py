# app/models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    def set_password(self, p): self.password_hash = generate_password_hash(p)
    def check_password(self, p): return check_password_hash(self.password_hash, p)

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

class CL6(db.Model):
    __tablename__ = "cl6"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # auto
    nome = db.Column(db.String(120), nullable=False)
    situacao = db.Column(db.String(30), default="OK")
    qtd_prevista = db.Column(db.Integer, default=0)
    qtd_disp = db.Column(db.Integer, default=0)
    qtd_indisp = db.Column(db.Integer, default=0)
    valor = db.Column(db.Numeric(12,2), default=0)
    observacao = db.Column(db.Text)
    numero_serie = db.Column(db.String(120))
    numero_patrimonio = db.Column(db.String(120))
    modelo = db.Column(db.String(120))
    marca = db.Column(db.String(120))
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
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
