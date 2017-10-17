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
		# find the current point for display
		current_point = agenda.points[0]
		for point in agenda.points:
			if point.current_active == True:
				current_point = point
	except Exception, e:
		current_point = 0
		print str(e)
	
	

	try:
		points = []
		for i in agenda.points:
			if i.internal_order is None:
				raise ValueError("oops")
			points.append([i, i.internal_order])
		points = sorted(points, key=lambda x:x[1])
		points = list(zip(*points)[0])
	except Exception as e:
		print(e)
		points = []
		for i in agenda.points:
			points.append([i, i.id])
		points = sorted(points, key=lambda x:x[1])
		points = list(zip(*points)[0])


	return render_template('present/present.html',agenda=agenda, points=points, current_point=current_point, title="Present")


# @socketio.on('client_connected')
# def handle_client_connect_event(json):
#     print('received json: {0}'.format(str(json)))
#     emit('my response', {'data': 'connected'})

# @socketio.on('disconnect', namespace='/test')
# def test_disconnect():
#     print('Client disconnected')

# called when a card has been advanced
@socketio.on('my_event')
def new_active(agenda_uuid):
	# print "new_active"
	socketio.emit('new_active', {'data':str(agenda_uuid)})

# This is the method that handles the click from presentation mode
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
	new_active(agenda.uuid)
	return str(current_point.name)
