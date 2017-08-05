from flask import flash, redirect, render_template, url_for, request, abort
from flask_login import login_required, current_user

from .. import db
from ..models import User, Agenda, Point
from . import present

@present.route('/view/<uuid:agenda_id>')
@login_required
def present_agenda(agenda_id):
	agenda = Agenda.query.filter_by(uuid=agenda_id).first()
	current_point = agenda.points[0]
	for point in agenda.points:
		if point.current_active == True:
			current_point = point

	return render_template('present/agenda.html',agenda=agenda, points=agenda.points, current_point=current_point, title="Present")

@present.route('/view/active/<int:point_id>', methods=['GET', 'POST'])
@login_required
def update_active_point(point_id):
	current_point = Point.query.filter_by(id=point_id).first()
	agenda = Agenda.query.filter_by(id=current_point.agenda).first()

	for point in agenda.points:
		point.current_active = False

	current_point.current_active = True
	db.session.commit()

	for i in agenda.points:
		if i.current_active == True:
			current_point = i

	return str(current_point.name)