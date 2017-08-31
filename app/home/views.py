from flask import flash, redirect, render_template, url_for, request, abort, Response
from flask_login import login_required, current_user
import uuid
import json
from collections import defaultdict


from forms import AddAgendaForm, AddPointForm
from .. import db
from ..models import User, Agenda, Point
from . import home


def get_current_point(agenda):
	# agenda = Agenda.query.filter_by(uuid=agenda_uuid).first()
	current_point = agenda.points[0]
	for point in agenda.points:
		if point.current_active == True:
			current_point = point
	return current_point

@home.route('/')
def homepage():
	return render_template('home/index.html', title="Welcome")

@home.route('/dashboard', defaults={'agenda_uuid': None})
@home.route('/dashboard/<string:agenda_uuid>')
@login_required
def dashboard(agenda_uuid):
	cur = []
	agendas = current_user.agendas
	
	for agenda in agendas:
		try:
			cur.append(get_current_point(agenda))
		except Exception, e:
			cur.append("N/A")
			print str(e)
	return render_template('home/dashboard.html', agendas=agendas, cur=cur, clicked=agenda_uuid, title="Dashboard")

@home.route('/add/agenda/', methods=['GET', 'POST'])
@login_required
def add_agenda():
	form = AddAgendaForm()
	if form.validate_on_submit():
		#uuid might eventually run into collision problems, but that would require our service to have more users than there are currently people on the earth. So that would be something..
		agenda = Agenda(created_by = current_user.id, uuid = uuid.uuid4(), name = form.name.data)

		db.session.add(agenda)
		db.session.commit()
		flash("Your agenda has been created")
		return redirect(url_for('home.dashboard'))

	return render_template('home/agenda_create.html', form=form, title="Add Agenda")


@home.route('/add/dynamic/agenda/', methods=['POST'])
@login_required
def add_dynamic_agenda():
	if request.method == 'POST':
		info = dict(request.form)
		agenda_name = str(info['name'][0])

		agenda = Agenda(created_by = current_user.id, uuid=uuid.uuid4(), name=agenda_name)
		db.session.add(agenda)
		db.session.commit()

		info.pop('name', None)
		points = []
		for key,value in info.iteritems():
			#pull names based on key data, grab the associated content and create an object
			if key.startswith('point'):
				index = key.split("_")[1]
				content_key = "content_point_{}".format(index)
				content_value = str(info[content_key][0])
				point_name = str(value[0])
				if index == '0':
					active = True
				else:
					active = False

				if point_name != "":
					point = Point(agenda =agenda.id, name=point_name, content=content_value, current_active=active)
					db.session.add(point)
					db.session.commit()
		

	return redirect(url_for('home.dashboard', clicked=agenda.uuid))

@home.route('/delete/agenda/<string:agenda_uuid>/')
@login_required
def delete_agenda(agenda_uuid):
	agenda = Agenda.query.filter_by(uuid=agenda_uuid).first()
	if current_user.id != agenda.created_by:
		abort(404)

	db.session.delete(agenda)
	db.session.commit()
	flash("Deleted {}".format(agenda.name))

	return redirect(url_for('home.dashboard'))

# This is confusing, but I promise it's good. There are two ids. One is the database primary key. and the other is the uuid that is used
# as an external reference. So when you see agenda_id that refers usually to the uuid.
@home.route('/agenda/<string:agenda_uuid>/')
@login_required
def view_agenda(agenda_uuid):
	agenda = Agenda.query.filter_by(uuid=agenda_uuid).first()
	created_by = User.query.filter_by(id=agenda.created_by).first().username
	if agenda is None:
		abort(404)
	points = agenda.points
	li = []
	for i,point in enumerate(points):
		point_dict = defaultdict(str)
		point_dict['name'] = str(point.name)
		point_dict['content'] = str(point.content)
		point_dict['current_active'] = str(point.current_active)
		li.append(dict(point_dict))
	agenda = agenda.__dict__
	agenda.pop('_sa_instance_state', None)

	agenda['points'] = li
	agenda['created_by'] = created_by
	for key, value in agenda.iteritems():
		if key == 'date_created':
			agenda[key] = str(value)
	
	# return render_template('home/agenda_view.html', agenda=agenda, points=agenda.points, title=agenda.name)
	return Response(json.dumps(agenda),  mimetype='application/json')


@home.route('/add/point/<string:agenda_uuid>/', methods=['GET','POST'])
@login_required
def add_point(agenda_uuid):
	form = AddPointForm()
	agenda = Agenda.query.filter_by(uuid=agenda_uuid).first()
	if current_user.id != agenda.created_by:
		abort(404)
	if form.validate_on_submit():
		if current_user.id == agenda.created_by:
			point = Point(agenda = agenda.id, name=form.name.data, content = form.content.data)
			db.session.add(point)
			db.session.commit()
			flash("Your point has been added")
			return redirect(url_for('home.dashboard', clicked=agenda_uuid))

	return render_template('home/point_add.html', form=form, agenda_uuid=agenda_uuid, title="Add Point")



@home.route('/delete/point/<int:point_id>/', methods=['GET', 'POST'])
@login_required
def delete_point(point_id):
	point = Point.query.filter_by(id=point_id).first()
	if point is None:
		abort(404)
	agenda = Agenda.query.filter_by(id = point.agenda).first()
	if current_user.id != agenda.created_by:
		abort(404)

	db.session.delete(point)
	db.session.commit()
	flash("Your point as been deleted")

	return redirect(url_for('home.view_agenda', agenda_uuid=agenda.uuid))




