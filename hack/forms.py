from flask_wtf import FlaskForm
from wtforms import EmailField,StringField, PasswordField, SubmitField, TextAreaField, FileField, IntegerField, RadioField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from wtforms import ValidationError

from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

class RegForm(FlaskForm):
    email = EmailField('Email',validators=[DataRequired()])
    image = FileField('Upload a profile picture', validators=[FileAllowed('png', 'jpg')])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField("Register")

class SearchForm(FlaskForm):
    query = StringField('search', validators=[DataRequired()])
