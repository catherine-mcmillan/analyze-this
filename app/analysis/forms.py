from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class UploadForm(FlaskForm):
    title = StringField('Analysis Title', validators=[DataRequired(), Length(min=3, max=100)])
    csv_file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    submit = SubmitField('Upload')

class ColumnAnnotationForm(FlaskForm):
    # This will be dynamically generated based on CSV columns
    submit = SubmitField('Continue to Prompt')

class PromptForm(FlaskForm):
    prompt = TextAreaField('Analysis Prompt', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Generate Enhanced Prompt')

class EnhancedPromptForm(FlaskForm):
    enhanced_prompt = TextAreaField('Enhanced Prompt', validators=[DataRequired(), Length(min=10)])
    submit = SubmitField('Generate Analysis')