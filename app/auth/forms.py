from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_babel import lazy_gettext as _l
from app.models import User, MyCompany


class LoginForm(FlaskForm):
    username = StringField(_l('Username *'), validators=[DataRequired()])
    password = PasswordField(_l('Password *'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username *'), validators=[DataRequired()])
    email = StringField(_l('Email *'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password *'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password *'),
                              validators=[DataRequired(), EqualTo('password')])
    company = StringField(_l('Company name *'), validators=[DataRequired()])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_l('Please use a different email address.'))

    def validate_company(self, company):
        my_company = MyCompany.query.filter_by(name=company.data).first()
        if my_company is not None:
            raise ValidationError(_l('This company already exists!'))


class RegistrationInvitedForm(FlaskForm):
    username = StringField(_l('Username *'), validators=[DataRequired()])
    email = StringField(_l('Email *'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password *'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password *'),
                              validators=[DataRequired(), EqualTo('password')])

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request password reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(_l('Repeat Password'),
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
