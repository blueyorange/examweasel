from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, IntegerField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class SaveForm(FlaskForm):
    filename = StringField('Filename', validators=[DataRequired()])
    saveSubmit = SubmitField('Save')

class DataForm(FlaskForm):
    exam_sitting = StringField('Exam Sitting')
    paper = StringField('Exam Paper')
    question_number = IntegerField('Question')
    topic = StringField('Topic')
    question_type = StringField('Type')
    description = TextAreaField('Description')
    answer = StringField('Answer')
    submit = SubmitField('Save')