from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    api_key = StringField('Anthropic API Key', validators=[Length(max=128)])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    api_key = StringField('Anthropic API Key', validators=[Length(max=128)])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    submit = SubmitField('Update Profile')

class UploadCSVForm(FlaskForm):
    title = StringField('Analysis Title', validators=[DataRequired(), Length(max=200)])
    file = FileField('Upload CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload')

class ColumnAnnotationForm(FlaskForm):
    # This form will be dynamically generated based on CSV columns
    submit = SubmitField('Continue to Prompt Creation')

class PromptForm(FlaskForm):
    prompt = TextAreaField('Analysis Prompt', validators=[DataRequired()])
    submit = SubmitField('Generate Enhanced Prompt')

class ReviewPromptForm(FlaskForm):
    enhanced_prompt = TextAreaField('Enhanced Prompt', validators=[DataRequired()])
    submit = SubmitField('Generate Analysis Report')