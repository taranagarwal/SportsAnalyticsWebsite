from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("home.html", user=current_user)

@views.route('/about')
def about():
    return render_template("about.html", user=current_user)

@views.route('/custom-player')
@login_required
def custom_player():
    return render_template("custom.html", user=current_user)


@views.route('/add_custom', methods=['POST'])
def add_custom():
    print(1)
    player_data = request.json['player_data']
    print(player_data)
    return jsonify({"status": "success", "message": "Player added successfully!"})
