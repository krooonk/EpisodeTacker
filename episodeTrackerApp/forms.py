from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField
from wtforms.validators import Length,DataRequired,Email,EqualTo,ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[Length(3, 25), DataRequired()])
    email = StringField("Email", validators=[Email(), DataRequired()])
    password = PasswordField("Password", validators=[Length(min=8), DataRequired()])
    confirm_password = PasswordField("Repeat Password",
                                     validators=[DataRequired(),
                                                 EqualTo("password", message="Passwords must match.")])

    def validate_username(self, username_to_be_checked):
        if User.query.filter_by(username=username_to_be_checked.data).first():
            raise ValidationError("This username already exists. Please try a different one.")

    def validate_email(self,email_to_be_checked):
        if User.query.filter_by(email=email_to_be_checked.data).first():
            raise ValidationError("This email address already exists. Please try a different one.")
