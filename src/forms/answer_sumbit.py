from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed


class AnswerForm(FlaskForm):
    submit_btn = SubmitField('Play on')
