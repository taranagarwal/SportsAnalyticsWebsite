from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, current_user
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash 

profile = Blueprint('profile', __name__)

@profile.route('/')
@login_required
def user():
    return render_template('profile.html', user=current_user)

@profile.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password1 = request.form.get('password1')
        new_password2 = request.form.get('password2')

        if check_password_hash(current_user.password, old_password):
            if new_password1 != new_password2:
                flash('New passwords must match', category='error')
            elif len(new_password1) < 5:
                flash('New password must be 5 characters or longer', category='error')
            elif check_password_hash(current_user.password, new_password1):
                flash('New password cannot match old password', category='error')
            else:
                hashed_new_password = generate_password_hash(new_password1, method='pbkdf2:sha256')
                current_user.password = hashed_new_password
                db.session.commit()
                flash('Successfully changed password', category='success')
                return redirect(url_for('views.home'))
        else:
            flash('Current password is incorrect', category='error')

    return render_template("change-password.html", user=current_user)

@profile.route('/my-lineups')
@login_required
def my_lineups():
    return "<p>Lineups</p>"

@profile.route('/my-players')
@login_required
def my_players():
    return "<p>Players</p>"

