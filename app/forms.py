# app/forms.py (adicione/ajuste)
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, BooleanField, PasswordField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Optional, Length, EqualTo

SITUACOES = [("OK","OK"), ("EM_USO","EM_USO"), ("INOPERANTE","INOPERANTE")]

class CL2Form(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    situacao = StringField("Situação", validators=[Optional(), Length(max=30)])
    qtd_prevista = IntegerField("Quantidade Prevista", validators=[Optional(), NumberRange(min=0)])
    qtd_disp = IntegerField("Quantidade Disponível", validators=[Optional(), NumberRange(min=0)])
    qtd_indisp = IntegerField("Quantidade Indisponível", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Salvar")

class CL6Form(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    situacao = StringField("Situação", validators=[Optional(), Length(max=30)])
    qtd_prevista = IntegerField("Quantidade Prevista", validators=[Optional(), NumberRange(min=0)])
    qtd_disp = IntegerField("Quantidade Disponível", validators=[Optional(), NumberRange(min=0)])
    qtd_indisp = IntegerField("Quantidade Indisponível", validators=[Optional(), NumberRange(min=0)])
    valor = DecimalField("Valor (R$)", places=2, rounding=None, validators=[Optional(), NumberRange(min=0)])
    observacao = TextAreaField("Observação (defeito)", validators=[Optional(), Length(max=2000)])
    numero_serie = StringField("Número de Série", validators=[Optional(), Length(max=120)])
    numero_patrimonio = StringField("Número de Patrimônio", validators=[Optional(), Length(max=120)])
    modelo = StringField("Modelo", validators=[Optional(), Length(max=120)])
    marca = StringField("Marca", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Salvar")
    
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