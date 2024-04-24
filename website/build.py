from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from .models import Player
from PTM import PTM
from LinearWeights import LinearWeights
from create import Create

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

@build.route('/calculate_lineup', methods=['POST'])
def calculate_lineup():
    # Extract player data from request
    # For example, let's say you receive player IDs
    player_ids = request.json['player_ids']
    
    # Retrieve player objects from the database
    players = Player.query.filter(Player.id.in_(player_ids)).all()
    
    # Convert player objects to the format expected by your calculation logic
    # Then perform the calculations
    optimized_lineup = perform_lineup_optimization(players)  # This is your adapted logic

    # Return the result as JSON
    return jsonify(optimized_lineup)

@build.route('/build-lineup')
def login():
    return render_template("build_lineup.html", user=current_user)

@build.route('/edit')
def forgot_password():
    return "<p>Edit</p>"


def perform_lineup_optimization(players):
    PTMs = players.build_player_objects()
    lw = LinearWeights()

    process = Create(players, 4)

    topk, topuniquek = process.topk, process.topuniquek
    first = 0
    best = None
    for score, ordering in sorted(topk, reverse=True):
        print(f"Score: {score}, Ordering: {ordering[0:9]}")
        if first == 0:
            best = ordering
        first += 1
    print("-------")
    for score, ordering in sorted(topuniquek, reverse=True):
        print(f"Score: {score}, Ordering: {ordering[0:9]}")
        return(score, ordering[0:9])