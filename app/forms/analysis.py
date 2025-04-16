from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class UploadCSVForm(FlaskForm):
    """Form for uploading CSV files"""
    file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'Only CSV files are allowed!')
    ])
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Upload')

class PromptForm(FlaskForm):
    """Form for submitting analysis prompts"""
    prompt = TextAreaField('Analysis Prompt', validators=[
        DataRequired(),
        Length(min=10, max=1000)
    ])
    submit = SubmitField('Analyze')

class ReviewPromptForm(FlaskForm):
    """Form for reviewing and editing prompts"""
    prompt = TextAreaField('Analysis Prompt', validators=[
        DataRequired(),
        Length(min=10, max=1000)
    ])
    submit = SubmitField('Update Prompt') 