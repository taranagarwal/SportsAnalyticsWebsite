from flask import Blueprint

auth = Blueprint('build', __name__)

@auth.route('/build_lineup')
def login():
    return "<p>Build</p>"

@auth.route('/edit')
def forgot_password():
    return "<p>Edit</p>"
