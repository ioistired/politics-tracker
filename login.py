from flask_login import login_user
from flask import Blueprint, render_template, redirect, url_for, request
from jinja2 import TemplateNotFound, Template
import psycopg2
from argon2 import PasswordHasher

bp = Blueprint('login', __name__)
conn = psycopg2.connect("dbname=politics user=postgres")
cur = conn.cursor()
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
    error = None
    if request.method == 'POST':
        email = request.form.get('inputEmail', 'test@test')
        password = request.form.get('inputPassword', 'test')
        cur.execute('select * from users where user_email = %s', [email])
        line = cur.fetchone()
        if line[2] == ph.hash(password):
            user = User(True, True, False, email)
            login_user(user)
        return redirect('/')
        # add actual logging in here!!
        
    return render_template('login.html', error=error)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        email = request.form.get('inputEmail', 'test@test')
        password = request.form.get('inputPassword', 'test')
        state = request.form.get('inputState', 'Nebraska')
        hash = ph.hash(password)
        cur.execute('insert into users values (%s, %s,  %s);', [email, hash, state])
        conn.commit()
        cur.close()
        conn.close()
        user = User(True, True, False, email)
        login_user(user)
        return redirect('/')
        # add actual logging in here!!
        
    return render_template('register.html', error=error)
