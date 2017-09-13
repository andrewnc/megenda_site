from flask import flash, redirect, render_template, url_for, request, abort
from flask_login import login_required, login_user, logout_user
import datetime

from . import auth
from forms import RegistrationForm, LoginForm
from .. import db
from ..models import User


from urlparse import urlparse, urljoin
from flask import request, url_for


# TODO: Add a forgot my password email functionality - which will be hard... mostly because I don't want to do it....

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@auth.route('/register/', methods=['GET','POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(email=form.email.data,username=form.username.data,first_name=form.first_name.data,last_name=form.last_name.data,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		flash("Thank you for registering, you may now proceed to login!")


		return redirect(url_for('auth.login'))

	return render_template('auth/register.html', form=form, title="Register")


@auth.route("/login/", methods=['GET', 'POST'])
def login():
	form =LoginForm()
	if form.validate_on_submit():

		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user)
			user.last_login = datetime.datetime.utcnow()
			db.session.commit()

			next = request.args.get('next')

			if not is_safe_url(next):
				return abort(400)

			return redirect(next or url_for('home.dashboard'))

		else:
			flash('Invalid Email or Password')
	return render_template('auth/login.html', form=form, title="Login")

@auth.route("/logout/")
@login_required
def logout():
	logout_user()
	flash('You have been successfully logged out')
	return redirect(url_for('auth.login'))