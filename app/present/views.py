from flask import flash, redirect, render_template, url_for, request, abort
from flask_login import login_required, current_user
from flask_socketio import emit


from .. import db, socketio
from ..models import User, Agenda, Point
from . import present


@present.route('/view/<string:agenda_uuid>')
@login_required
def present_agenda(agenda_uuid):
	agenda = Agenda.query.filter_by(uuid=agenda_uuid).first()
	try:
		current_point = agenda.points[0]
		for point in agenda.points:
			if point.current_active == True:
				current_point = point
	except Exception, e:
		current_point = 0
		print str(e)

	return render_template('present/agenda.html',agenda=agenda, points=agenda.points, current_point=current_point, title="Present")


# @socketio.on('client_connected')
# def handle_client_connect_event(json):
#     print('received json: {0}'.format(str(json)))
#     emit('my response', {'data': 'connected'})

# @socketio.on('disconnect', namespace='/test')
# def test_disconnect():
#     print('Client disconnected')

@socketio.on('my_event', namespace='/view')
def new_active():
	# print "new_active"
	socketio.emit('new_active')

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
	new_active()
	return str(current_point.name)