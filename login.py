from flask_login import login_user
from flask import Blueprint, render_template, redirect, url_for, request
from jinja2 import TemplateNotFound, Template

bp = Blueprint('login', __name__)

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
        email = "test@test.com"
        user = User(True, True, False, email)
        login_user(user)
        return redirect('/')
        # add actual logging in here!!
        
    return render_template('login.html', error=error)

