from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired,Length, Email, EqualTo,ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators =[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email', validators =[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):

        user = User.query.filter_by(username=username.data).first()

        if user:
            raise ValidationError('That username is taken')

    def validate_email(self,email):

        email = User.query.filter_by(email=email.data).first()

        if email:
            raise ValidationError('That email is already taken')

class LoginForm(FlaskForm):
    email = StringField('Email', validators =[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators =[DataRequired(),Length(min=2,max=20)])
    email = StringField('Email', validators =[DataRequired(),Email()])
    picture = FileField('Update Profile Picture',validators =[FileAllowed(['jpg','png'])])
    about = StringField('About', validators =[Length(min=2,max=100)])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data!=current_user.username:
            user = User.query.filter_by(username=username.data).first()

            if user:
                raise ValidationError('That username is taken')

    def validate_email(self,email):
        if email.data!=current_user.email:
            email = User.query.filter_by(email=email.data).first()

            if email:
                raise ValidationError('That email is already taken')

class PostForm(FlaskForm):
    content = TextAreaField('Content', validators =[DataRequired(),Length(max=280)])
    tag = TextAreaField('Tag',validators =[Length(max=20)],default="#hello (możesz dać tylko jeden tag na raz)")
    submit = SubmitField('Post')

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
