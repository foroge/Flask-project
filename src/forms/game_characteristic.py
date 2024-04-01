from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed


class GameForm(FlaskForm):
    def __init__(self, maximum=0, **kwargs):
        question = DecimalField('Question 1', validators=[NumberRange(min=0, max=maximum, message='bla')])

        submit_btn = SubmitField('Start game')

        super().__init__(**kwargs)

