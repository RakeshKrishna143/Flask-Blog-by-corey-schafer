from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,TextAreaField
from flask_wtf.file import FileField,FileAllowed
from wtforms.validators import DataRequired,Length,Email,EqualTo,ValidationError
from application.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = StringField('Password',validators=[DataRequired()])
    confirm_password = StringField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self,username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken')
    def validate_email(self,email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('That email is already taken')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = StringField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email',validators=[DataRequired(),Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user = User.objects(username=username.data).first()
            if user:
                raise ValidationError('That username is already taken')
    def validate_email(self,email):
        if email.data!=current_user.email:
            user = User.objects(email=email.data).first()
            if user:
                raise ValidationError('That email is already taken')
class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Post')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    submit = SubmitField('Reset Password Request')

    def validate_email(self,email):
        user = User.objects(email=email.data).first()
        if not(user):
            raise ValidationError('There is no such Email. Please Do register')

class ResetPasswordForm(FlaskForm):
    password = StringField('Password',validators=[DataRequired()])
    confirm_password = StringField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
    submit = SubmitField('Reset Password')


