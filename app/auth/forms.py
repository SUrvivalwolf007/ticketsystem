from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from ..models import User

class LoginForm(FlaskForm):
    username_or_email = StringField('Benutzername oder E-Mail', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=80)])
    first_name = StringField('Vorname', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Nachname', validators=[DataRequired(), Length(max=100)])
    email = StringField('E-Mail', validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Passwort bestätigen', validators=[DataRequired(), EqualTo('password', message='Passwörter müssen übereinstimmen.')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Dieser Benutzername ist bereits vergeben.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Diese E-Mail-Adresse wird bereits verwendet.')