from flask import flash, redirect, render_template, url_for, request, abort
from flask_login import login_required, current_user
import uuid


from forms import AddAgendaForm, AddPointForm
from .. import db
from ..models import User, Agenda, Point
from . import home

@home.route('/')
def homepage():
	return render_template('home/index.html', title="Welcome")

@home.route('/dashboard/')
@login_required
def dashboard():
	agendas = current_user.agendas
	return render_template('home/dashboard.html', agendas=agendas, title="Dashboard")

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

@home.route('/delete/agenda/<uuid:agenda_id>/')
@login_required
def delete_agenda(agenda_id):
	agenda = Agenda.query.filter_by(uuid=agenda_id).first()
	if current_user.id != agenda.created_by:
		abort(404)

	db.session.delete(agenda)
	db.session.commit()
	flash("Deleted {}".format(agenda))

	return redirect(url_for('home.dashboard'))

# This is confusing, but I promise it's good. There are two ids. One is the database primary key. and the other is the uuid that is used
# as an external reference. So when you see agenda_id that refers usually to the uuid.
@home.route('/agenda/<uuid:agenda_id>/')
@login_required
def view_agenda(agenda_id):
	agenda = Agenda.query.filter_by(uuid=agenda_id).first()
	if agenda is None:
		abort(404)
	return render_template('home/agenda_view.html', agenda=agenda, points=agenda.points, title=agenda.name)


@home.route('/add/point/<uuid:agenda_id>/', methods=['GET','POST'])
@login_required
def add_point(agenda_id):
	form = AddPointForm()
	agenda = Agenda.query.filter_by(uuid=agenda_id).first()
	if current_user.id != agenda.created_by:
		abort(404)
	if form.validate_on_submit():
		if current_user.id == agenda.created_by:
			point = Point(agenda = agenda.id, name=form.name.data, content = form.content.data)
			db.session.add(point)
			db.session.commit()
			flash("Your point has been added")
			return redirect(url_for('home.view_agenda', agenda_id=agenda_id))

	return render_template('home/point_add.html', form=form, agenda_id=agenda_id, title="Add Point")



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

	return redirect(url_for('home.view_agenda', agenda_id=agenda.uuid))




