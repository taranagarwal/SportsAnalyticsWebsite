from flask import Blueprint, render_template 

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template("login.html")

@auth.route('/forgot-password')
def forgot_password():
    return render_template("forgot-password.html")

@auth.route('/sign-up')
def register():
    return render_template("sign-up.html")