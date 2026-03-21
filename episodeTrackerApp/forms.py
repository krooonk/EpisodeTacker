from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from wtforms.validators import Length,DataRequired,Email,EqualTo

class RegistrationForm(FlaskForm):
    username=StringField("Username",validators=[Length(3,25),DataRequired()])
    email=StringField("Email",validators=[Email(),DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    confirm_password=PasswordField("Repeat the Password",validators=[DataRequired(),EqualTo("password",message="Passwords must match.")])

