from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length

from ..models import User, Agenda, Point

class AddAgendaForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired(), Length(max=128)])
	create = SubmitField('Create')

class AddPointForm(FlaskForm):
	name = StringField('Name', validators=[Length(max=128)])
	content = StringField('Body', validators=[Length(max=512)])
	add = SubmitField('Add')
	