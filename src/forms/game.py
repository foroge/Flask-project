from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired


class GameForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    choices = SelectField('Rating card:', choices=[" ", "+", "-"])
    submit_btn = SubmitField('Sumbit')
