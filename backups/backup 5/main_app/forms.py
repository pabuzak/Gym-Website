from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import (StringField, PasswordField, SubmitField,
                     BooleanField, TextAreaField)
from wtforms.validators import (DataRequired, Length, Email,
                                EqualTo, ValidationError)
from main_app.models import User

# Register Form
class RegistrationForm(FlaskForm):
    # username information
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(min=2, max=20)])
    # email information
    email = StringField('Email', validators=[DataRequired(), Email()])
    # password information
    password = PasswordField('Password', validators=[DataRequired()])
    # confirm password information
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # submit form
    submit = SubmitField('Sign Up')

    # validate username
    def validate_username(self, username):
        # check all users to ensure the username is not taken
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                # validation error message
                ('That username is taken. Please choose another one'))

    # validate email
    def validate_email(self, email):
        # check all users emails to ensure the email is not taken
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(
                # validation error message
                ('That email is taken. Please choose another one'))


# Login Form
class LoginForm(FlaskForm):
    # Email information
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Password information
    password = PasswordField('Password', validators=[DataRequired()])
    # remember password form
    remember = BooleanField('Remember Me')
    # submit form
    submit = SubmitField('Login')


# Update Account Form
class UpdateAccountForm(FlaskForm):
    # Username information
    username = StringField(
        'Username', validators=[DataRequired(), Length(min=2, max=20)])
    # Emai information
    email = StringField('Email', validators=[DataRequired(), Email()])
    # Picture information
    picture = FileField(
        'Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    # submit form
    submit = SubmitField('Update')

    # validate username
    def validate_username(self, username):
        if username.data != current_user.username:
            # check all users to ensure username is not taken
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError(
                    # validation error messsage
                    'That username is taken. Please choose another one')

    # validate email
    def validate_email(self, email):
        if email.data != current_user.email:
            # check all emails to ensure email is not taken
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    # validation error message
                    'That email is taken. Please choose another one')


# Post Form
class PostForm(FlaskForm):
    # title information
    title = StringField('Title', validators=[DataRequired()])
    # content information
    content = TextAreaField('Content', validators=[DataRequired()])
    # submit form
    submit = SubmitField('Post')


# Reqiest Reset Form
class RequestResetForm(FlaskForm):
    # email information
    email = StringField('Email', validators=[DataRequired(), Email()])
    # submit information
    submit = SubmitField('Request Password Reset') 

    # validate email
    def validate_email(self, email):
        # check email to see if there is an account with the email
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                # validation error message
                'There is not account with that email.'
                'You need to register first.')


# Reset Password Form
class ResetPasswordForm(FlaskForm):
    # password information
    password = PasswordField('Password', validators=[DataRequired()])
    # confirm password
    confirm_password = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    # submit form
    submit = SubmitField('Reset Password')
