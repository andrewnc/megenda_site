from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy.orm import relationship

from app import db, login_manager


class User(UserMixin, db.Model):


	__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(254), index=True, unique=True)
	username = db.Column(db.String(60), index=True, unique=True)
	first_name = db.Column(db.String(60), index=True)
	last_name = db.Column(db.String(60), index=True)
	password_hash = db.Column(db.String(128))
	last_login = db.Column(db.DateTime)
	agendas = relationship("Agenda", cascade="all, delete-orphan")
	date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	is_admin = db.Column(db.Boolean, default=False)

	@property
	def password(self):
		raise AttributeError("I can't show you that")


	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __repr__(self):
		return "<User: {}>".format(self.username)


	@login_manager.user_loader
	def load_user(user_id):
		return User.query.get(int(user_id))

class Agenda(db.Model):

	__tablename__ = 'agendas'

	id = db.Column(db.Integer, primary_key=True)
	created_by = db.Column(db.Integer, db.ForeignKey("users.id"))
	date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow())
	uuid = db.Column(db.String(36),index=True,unique=True)
	name = db.Column(db.String(128))
	points = relationship("Point", cascade="all, delete-orphan")

	def __repr__(self):
		# return "<Agenda: {}, Created By: {}, on {}>".format(self.name, str(User.query.filter_by(id=self.created_by).first().username), self.date_created)
		return "{}".format(self.date_created.strftime("%d %A %b %Y"))

class Point(db.Model):

	__tablename__ = 'points'

	id = db.Column(db.Integer, primary_key=True)
	agenda = db.Column(db.Integer, db.ForeignKey("agendas.id"))
	name = db.Column(db.String(128))
	content = db.Column(db.String(512))
	current_active = db.Column(db.Boolean, default=False)

	def __repr__(self):
		return "{}".format(self.name)
