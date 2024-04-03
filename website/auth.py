from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

 

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if len(email) < 1 or len(password) < 1:
            flash('Please fill in both the email and password', category='error')
        elif user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return render_template("forgot-password.html")

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists', category='error')
        elif len(email) < 1 or len(name) < 1 or len(password1) < 1 or len(password2) < 1:
            flash('Please fill in all fields', category='error')
        else:
            if len(email) < 4:
                flash('Email must be greater than 4 characters', category='error')
            if password1 != password2:
                flash('Passwords must match', category='error')
            elif len(password1) < 5:
                flash('Password must be 5 characters or longer', category='error')
            else:
                new_user = User(email=email, name=name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)
                flash('Account created', category='success')
                return redirect(url_for('views.home'))
    return render_template("sign-up.html", user=current_user)