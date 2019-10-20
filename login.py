from flask_login import login_user
from flask import Blueprint, render_template, redirect, url_for, request, g
from jinja2 import TemplateNotFound, Template
import psycopg2
from argon2 import PasswordHasher

bp = Blueprint('login', __name__)

def db():
	try:
		return g._db
	except AttributeError:
		g._db = db = psycopg2.connect(dbname='politics')
		db.autocommit = True
		return db

ph = PasswordHasher()

class User:
	def __init__(self, is_authenticated, is_active, is_anonymous, user_id):
		self.is_authenticated = is_authenticated
		self.is_active = is_active
		self.is_anonymous = is_anonymous
		self.user_id = user_id

	def get_id(self) :
		return self.user_id

@bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form.get('inputEmail', 'test@test')
		password = request.form.get('inputPassword', 'test')
		with db().cursor() as cur:
			cur.execute('select user_password from users where user_email = %s', (email,))
			hash, = cur.fetchone()

		if PasswordHasher().verify(hash, password):
			user = User(True, True, False, email)
			login_user(user)
		return redirect('/')
		# add actual logging in here!!

	return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		email = request.form.get('inputEmail', 'test@test')
		password = request.form.get('inputPassword', 'test')
		state = request.form.get('inputState', 'Nebraska')
		hash = ph.hash(password)
		with db().cursor() as cur:
			cur.execute('insert into users (user_email, user_password, user_state) values (%s, %s, %s);', (email, hash, state))
		user = User(True, True, False, email)
		login_user(user)
		return redirect('/')
		# add actual logging in here!!

	return render_template('register.html')
