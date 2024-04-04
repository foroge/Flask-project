from flask_wtf import FlaskForm
from wtforms import SubmitField, DecimalField
from wtforms.validators import DataRequired, Optional, NumberRange
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed


class StartGameForm(FlaskForm):
    question = DecimalField('Number of questions', validators=[NumberRange(min=1, max=10, message='bla')])
    submit_btn = SubmitField('Start game')
