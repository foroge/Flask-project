from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import MultipleFileField, FileRequired, FileAllowed


class CardForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    promt = StringField('Promt', validators=[DataRequired()])
    images = MultipleFileField(validators=[FileRequired(),
                                           FileAllowed(['jpg', 'png'], 'Images only!')])

    submit = SubmitField('Create')
