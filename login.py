from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

bp = Blueprint('login', __name__)

@bp.route('/login')
def show():
    try:
        return "hello"
    except TemplateNotFound:
        abort(404)
