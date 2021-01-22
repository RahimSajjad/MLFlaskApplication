from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.modelsdb import User


## Registration form######################
class RegistrationForm(FlaskForm):
    # User name: name of the field:StringField(),check validation:validators()
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])

    # User Email
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    # password & password Confirm
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    # submit button
    submit = SubmitField('Sign Up')

    # Creating a custom validation. If user wanted to register using same email or username, then thorw a message
    def validate_username(self, username):
        # Check the database using query:is user already exist in database!
        user = User.query.filter_by(username=username.data).first()
        # If user already exist, then throw a validation message
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        ## If email is exist,then then throw validation error
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


# Login Form########################################
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


###Create reset forms########################
class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


###for password field
class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

#############Post
# class PostForm(FlaskForm):
#    title = StringField('Title', validators=[DataRequired()])
#    slug = StringField('Slug', validators=[DataRequired()])
#    content = TextAreaField('Content', validators=[DataRequired()])
#    submit = SubmitField('Post')
