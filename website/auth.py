from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return "<p>Login</p>"

@auth.route('/forgot-password')
def forgot_password():
    return "<p>Forgot Password</p>"

@auth.route('/register')
def register():
    return "<p>Register</p>"