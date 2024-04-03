from flask import Blueprint
from flask_login import login_required, current_user

build = Blueprint('build', __name__)

@build.route('/build_lineup')
def login():
    return "<p>Build</p>"

@build.route('/edit')
def forgot_password():
    return "<p>Edit</p>"
