# app/forms.py (adicione/ajuste)
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, BooleanField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, EqualTo

SITUACOES = [("OK","OK"), ("EM_USO","EM_USO"), ("INOPERANTE","INOPERANTE")]

class CL2Form(FlaskForm):
    item_id = StringField("ID", validators=[DataRequired(), Length(max=50)])
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    situacao = SelectField("Situação", choices=SITUACOES, validators=[DataRequired()])
    qtd_prevista = IntegerField("Qtd Prevista", validators=[NumberRange(min=0)], default=0)
    qtd_disp = IntegerField("Qtd Disponível", validators=[NumberRange(min=0)], default=0)
    qtd_indisp = IntegerField("Qtd Indisponível", validators=[NumberRange(min=0)], default=0)
    submit = SubmitField("Salvar")

class CL6Form(CL2Form):
    valor = DecimalField("Valor", places=2, rounding=None, validators=[Optional()])
    observacao = TextAreaField("Observação/Defeito", validators=[Optional(), Length(max=2000)])
    numero_serie = StringField("Número de Série", validators=[Optional(), Length(max=120)])
    numero_patrimonio = StringField("Número de Patrimônio", validators=[Optional(), Length(max=120)])
    modelo = StringField("Modelo", validators=[Optional(), Length(max=120)])
    marca = StringField("Marca", validators=[Optional(), Length(max=120)])

class UserCreateForm(FlaskForm):
    username = StringField("Usuário", validators=[DataRequired(), Length(max=80)])
    role = SelectField("Papel", choices=[("admin","admin"), ("user","user")], validators=[DataRequired()])
    active = BooleanField("Ativo", default=True)
    password = PasswordField("Senha", validators=[DataRequired(), Length(min=4, max=128)])
    confirm = PasswordField("Confirmar senha", validators=[DataRequired(), EqualTo("password", message="Senhas diferentes")])
    submit = SubmitField("Salvar")

class UserEditForm(FlaskForm):
    role = SelectField("Papel", choices=[("admin","admin"), ("user","user")], validators=[DataRequired()])
    active = BooleanField("Ativo", default=True)
    submit = SubmitField("Salvar")

class UserPasswordForm(FlaskForm):
    password = PasswordField("Nova senha", validators=[DataRequired(), Length(min=4, max=128)])
    confirm = PasswordField("Confirmar senha", validators=[DataRequired(), EqualTo("password", message="Senhas diferentes")])
    submit = SubmitField("Atualizar senha")