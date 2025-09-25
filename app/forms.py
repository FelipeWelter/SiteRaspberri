# app/forms.py
from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, DecimalField, BooleanField, PasswordField,
    TextAreaField, SelectField, SubmitField, SelectMultipleField, widgets
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length, EqualTo

SITUACOES = [("OK", "OK"), ("EM_USO", "EM_USO"), ("INOPERANTE", "INOPERANTE")]

# ----------------- CL2 -----------------
class CL2Form(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    situacao = StringField("Situação", validators=[Optional(), Length(max=30)])
    qtd_prevista = IntegerField("Quantidade Prevista", validators=[Optional(), NumberRange(min=0)])
    qtd_disp = IntegerField("Quantidade Disponível", validators=[Optional(), NumberRange(min=0)])
    qtd_indisp = IntegerField("Quantidade Indisponível", validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField("Salvar")

# ----------------- CL6 -----------------
class CL6Form(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(), Length(max=120)])
    situacao = StringField("Situação", validators=[Optional(), Length(max=30)])
    qtd_prevista = IntegerField("Quantidade Prevista", validators=[Optional(), NumberRange(min=0)])
    qtd_disp = IntegerField("Quantidade Disponível", validators=[Optional(), NumberRange(min=0)])
    qtd_indisp = IntegerField("Quantidade Indisponível", validators=[Optional(), NumberRange(min=0)])
    valor = DecimalField("Valor (R$)", places=2, validators=[Optional(), NumberRange(min=0)])
    observacao = TextAreaField("Observação (defeito)", validators=[Optional(), Length(max=2000)])
    numero_serie = StringField("Número de Série", validators=[Optional(), Length(max=120)])
    numero_patrimonio = StringField("Número de Patrimônio", validators=[Optional(), Length(max=120)])
    modelo = StringField("Modelo", validators=[Optional(), Length(max=120)])
    marca = StringField("Marca", validators=[Optional(), Length(max=120)])
    submit = SubmitField("Salvar")

# ----------------- CL7 -----------------
class CL7Form(FlaskForm):
    material = StringField("Nome do Material", validators=[DataRequired(), Length(max=120)])
    marca = StringField("Marca", validators=[Optional(), Length(max=120)])
    modelo = StringField("Modelo", validators=[Optional(), Length(max=120)])
    numero_serie = StringField("Número de Série", validators=[Optional(), Length(max=120)])
    situacao = StringField("Situação", validators=[Optional(), Length(max=30)])
    observacao = TextAreaField("Observação (defeito)", validators=[Optional(), Length(max=2000)])
    submit = SubmitField("Salvar")

# ----------------- Usuários -----------------
class UserForm(FlaskForm):
    full_name = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    username = StringField("Login", validators=[DataRequired(), Length(max=80)])
    identity = StringField("Identidade", validators=[Optional(), Length(max=40)])

    # admin / all / user
    role = SelectField("Perfil", choices=[
        ("user", "Usuário (apenas classes selecionadas)"),
        ("all", "Usuário (todas as classes)"),
        ("admin", "Administrador (acesso total)"),
    ], validators=[DataRequired()])

    # múltiplas classes (apenas se role=user)
    classes = SelectMultipleField(
        "Classes com acesso",
        choices=[("CL2", "CL2"), ("CL6", "CL6"), ("CL7", "CL7")],
        option_widget=widgets.CheckboxInput(),
        widget=widgets.ListWidget(prefix_label=False),
        validators=[Optional()],
    )

    password = PasswordField("Senha", validators=[Optional(), Length(min=4, max=128)])
    confirm = PasswordField("Confirmar senha", validators=[Optional(), EqualTo("password", message="Senhas diferentes")])
    submit = SubmitField("Salvar")

class UserPasswordForm(FlaskForm):
    password = PasswordField("Nova senha", validators=[DataRequired(), Length(min=4, max=128)])
    confirm = PasswordField("Confirmar senha", validators=[DataRequired(), EqualTo("password", message="Senhas diferentes")])
    submit = SubmitField("Atualizar senha")
