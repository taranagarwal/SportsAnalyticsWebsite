from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from .models import Player

build = Blueprint('build', __name__)

@build.route('/search_players')
def search_players():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])  # No query provided, return empty list

    # Search for players whose name contains the query
    players = Player.query.filter(Player.player.ilike(f'%{query}%')).all()

    results = [{
        'id': player.id,
        'player': player.player,
        'season': player.season
    } for player in players]

    return jsonify(results)

@build.route('/build-lineup')
def login():
    return render_template("build_lineup.html", user=current_user)

@build.route('/edit')
def forgot_password():
    return "<p>Edit</p>"
