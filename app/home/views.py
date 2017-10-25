from flask import flash, redirect, render_template, url_for, request, abort, Response
from flask_login import login_required, current_user
import uuid
import json
from collections import defaultdict
import datetime


from forms import AddAgendaForm, AddPointForm, MailingListForm
from .. import db
from ..models import User, Agenda, Point
from . import home


# There might be a better way to set this up in the models so you can just say agenda.current_active and not worry about it
def get_current_point(agenda):
	# agenda = Agenda.query.filter_by(uuid=agenda_uuid).first()
	current_point = agenda.points[0]
	for point in agenda.points:
		if point.current_active == True:
			current_point = point
	return current_point

def get_agenda_duration(agenda):
	times = []
	s = "00:00:00"
	total_time = datetime.datetime.strptime(s, "%H:%M:%S")
	for point in agenda.points:
		try:
			point_time = datetime.timedelta(hours=int(point.hours), minutes=int(point.minutes), seconds=int(point.seconds))
			times.append(point_time)
		except Exception, e:
			pass #fail silently
	for time in times:
		total_time += time
	return total_time.strftime("%H:%M:%S")

@home.route('/signup/', methods=['POST'])
def signup():
	print(request.form.Email)
	return redirect(url_for('home.homepage'))

@home.route('/')
def homepage():
	return render_template('home/index.html', title="Welcome")

# There are two routes here because when you redirect from a 'back' press breadcrumb you want the viewed app to still be open
@home.route('/dashboard', defaults={'agenda_uuid': None})
@home.route('/dashboard/<string:agenda_uuid>')
@login_required
def dashboard(agenda_uuid):
	cur = []
	total_times = []
	agendas = current_user.agendas
	
	for agenda in agendas:

		# this handles agendas with no points
		try:
			cur.append(get_current_point(agenda))
		except Exception, e:
			cur.append("N/A")
			print str(e)

		
		total_times.append(get_agenda_duration(agenda))


	return render_template('home/dashboard.html', agendas=agendas, cur=cur,times=total_times, clicked=agenda_uuid, title="Dashboard")

# This was the old way to add agendas, I don't think it'll get used anymore
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
		counter = 0
		for key,value in info.iteritems():
			#pull names based on key data, grab the associated content and create an object
			if key.startswith('point'):
				index = key.split("_")[1]

				content_key = "content_point_{}".format(index)
				hours_key = "hours_{}".format(index)
				minutes_key = "minutes_{}".format(index)
				seconds_key = "seconds_{}".format(index)

				content_value = str(info[content_key][0])
				hours_value = int(info[hours_key][0])
				minutes_value = int(info[minutes_key][0])
				seconds_value = int(info[seconds_key][0])

				if(hours_value == 0 and minutes_value == 0 and seconds_value == 0):
					seconds_value = 1

				if hours_value > 24:
					hours_value = 24
				elif hours_value < 0:
					hours_value = 0


				if minutes_value > 59:
					minutes_value = 59
				elif minutes_value < 0:
					minutes_value = 0

				if seconds_value > 59:
					seconds_value = 59
				elif seconds_value < 0:
					seconds_value = 0

				point_name = str(value[0])
				if index == '0':
					active = True
				else:
					active = False

				# Doesn't add points with no name - definitely should make that required in the form itself.
				if point_name != "":
					point = Point(agenda=agenda.id, name=point_name, internal_order=counter, content=content_value, hours=int(hours_value), minutes=int(minutes_value), seconds=int(seconds_value), current_active=active)
					db.session.add(point)
					db.session.commit()
					counter += 1
		

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

	# Gather all the data from the form and points, clean it server side and spit it out as JSON - this will be used for the apps and for
	# the single page dashboard. It is fast, lightweight, and O(n) for a page load which should never be a problem.

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

	
	for i,point in enumerate(points):
		point_dict = defaultdict(str)
		point_dict['name'] = str(point.name)
		point_dict['content'] = str(point.content)
		point_dict['current_active'] = str(point.current_active)
		point_dict['duration'] = "{}:{}:{}".format(point.hours, point.minutes, point.seconds)
		li.append(dict(point_dict))
	duration = get_agenda_duration(agenda)
	agenda = agenda.__dict__
	agenda.pop('_sa_instance_state', None)

	agenda['points'] = li
	agenda['created_by'] = created_by
	agenda['duration'] = duration
	for key, value in agenda.iteritems():
		if key == 'date_created':
			agenda[key] = str(value)
	
	# return render_template('home/agenda_view.html', agenda=agenda, points=agenda.points, title=agenda.name)
	return Response(json.dumps(agenda),  mimetype='application/json')


# This will be depreciated and replaced with a monster "edit agenda" method or something - just to make it easier for people to use
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


# currently no UX functionality for this
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




