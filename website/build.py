from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from . models import Player
from .PTM import PTM
from .LinearWeights import LinearWeights
from .create import Create
from .CycleStart import CycleStart
import pandas as pd
from . import db
import json

build = Blueprint('build', __name__)

@build.route('/search_players')
def search_players():
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    players = Player.query.filter(Player.player.ilike(f'%{query}%')).all()
    results = [{
        'id': player.id,
        'player': player.player,
        'season': player.season
    } for player in players]

    return jsonify(results)

@build.route('/calculate_lineup', methods=['POST'])
def calculate_lineup():
    player_ids = request.json['player_ids']
    players = Player.query.filter(Player.id.in_(player_ids)).all()
    optimized_lineup = perform_lineup_optimization(players)
    result = jsonify(optimized_lineup).get_json()
    return jsonify(result)

@build.route('/build-lineup')
def build_lineup():
    return render_template("build_lineup.html", user=current_user)

@build.route('/edit')
def edit_lineup():
    return "<p>Edit lineup</p>"


def perform_lineup_optimization(players):
    p = PTM(players)
    PTMs = p.build_player_objects()
    lw = LinearWeights(players)


    process = Create(players, p, 4)

    topk, topuniquek = process.topk, process.topuniquek
    first = 0
    best = None
    for score, ordering in sorted(topk, reverse=True):
        #print(f"Score: {score}, Ordering: {ordering[0:9]}")
        if first == 0:
            best = ordering
        first += 1
        
    #print("-------")
    #for score, ordering in sorted(topuniquek, reverse=True):
        #print(f"Score: {score}, Ordering: {ordering[0:9]}")

    #print(lw.getRunExpectancyBOS(PTMs[3:7]))
    #print(lw.getRunExpectancyBOS(PTMs[4:8]))
    custom_order = topk[0][1][0:9]
    custom_order2 = topk[1][1][0:9]
    custom_order3 = topk[2][1][0:9]
    print(custom_order)
    print(custom_order2)
    print(custom_order3)

    df1 = pd.DataFrame({
           "Unnamed: 0": list(range(9)),
           "Rk": list(range(1, 10)),
           "Pos": [player.pos for player in players],
           "Name": [p.player for p in players],
           "Pos": [p.pos for p in players],
           "Age": [p.age for p in players],
           "G": [p.g for p in players],
           "PA": [p.pa for p in players],
           "AB": [p.ab for p in players],
           "R": [p.r for p in players],
           "H": [p.h for p in players],
           "2B": [p.twoB for p in players],
           "3B": [p.threeB for p in players],
           "HR": [p.hr for p in players],
           "RBI": [p.rbi for p in players],
           "SB": [p.sb for p in players],
           "CS": [p.cs for p in players],
           "BB": [p.bb for p in players],
           "SO": [p.so for p in players],
           "BA": [p.ba for p in players],
           "OBP": [p.obp for p in players],
           "SLG": [p.slg for p in players],
           "OPS": [p.ops for p in players],
           "OPS+": [p.opsPlus for p in players],
           "TB": [p.tb for p in players],
           "GDP": [p.gdp for p in players],
           "HBP": [p.hbp for p in players],
           "SH": [p.sh for p in players],
           "SF": [p.sf for p in players],
           "IBB": [p.ibb for p in players],
           "SpF": [p.spf for p in players]
        })
    
    players1 = list(players)
    players2 = list(players)
    players3 = list(players)


    df1['Name'] = pd.Categorical(df1['Name'], categories=custom_order, ordered=True)
    df1 = df1.sort_values('Name')
    index = 0
    for name in df1["Name"]:
        for player in players1:
            if player.player == name:
                players[index] = player
        index+=1

    p_cs = PTM(players)
    PTMS_cs = p_cs.build_player_objects()
    
    cs = CycleStart(PTMS_cs, players)
    optimal_lineup1 = cs.StartCycle()
    print("Optimal 1:")
    print(optimal_lineup1)

    df2 = pd.DataFrame({
        "Unnamed: 0": list(range(9)),
        "Rk": list(range(1, 10)),
        "Pos": [player.pos for player in players],
        "Name": [p.player for p in players],
        "Pos": [p.pos for p in players],
        "Age": [p.age for p in players],
        "G": [p.g for p in players],
        "PA": [p.pa for p in players],
        "AB": [p.ab for p in players],
        "R": [p.r for p in players],
        "H": [p.h for p in players],
        "2B": [p.twoB for p in players],
        "3B": [p.threeB for p in players],
        "HR": [p.hr for p in players],
        "RBI": [p.rbi for p in players],
        "SB": [p.sb for p in players],
        "CS": [p.cs for p in players],
        "BB": [p.bb for p in players],
        "SO": [p.so for p in players],
        "BA": [p.ba for p in players],
        "OBP": [p.obp for p in players],
        "SLG": [p.slg for p in players],
        "OPS": [p.ops for p in players],
        "OPS+": [p.opsPlus for p in players],
        "TB": [p.tb for p in players],
        "GDP": [p.gdp for p in players],
        "HBP": [p.hbp for p in players],
        "SH": [p.sh for p in players],
        "SF": [p.sf for p in players],
        "IBB": [p.ibb for p in players],
        "SpF": [p.spf for p in players]
    })

    df2['Name'] = pd.Categorical(df2['Name'], categories=custom_order2, ordered=True)
    df2 = df2.sort_values('Name')
    index = 0
    for name in df2["Name"]:
        for player in players2:
            if player.player == name:
                players[index] = player
        index+=1

    p_cs = PTM(players)
    PTMS_cs = p_cs.build_player_objects()
    
    cs = CycleStart(PTMS_cs, players)
    optimal_lineup2 = cs.StartCycle()
    print("Optimal 2:")
    print(optimal_lineup2)

    df3 = pd.DataFrame({
        "Unnamed: 0": list(range(9)),
        "Rk": list(range(1, 10)),
        "Pos": [player.pos for player in players],
        "Name": [p.player for p in players],
        "Pos": [p.pos for p in players],
        "Age": [p.age for p in players],
        "G": [p.g for p in players],
        "PA": [p.pa for p in players],
        "AB": [p.ab for p in players],
        "R": [p.r for p in players],
        "H": [p.h for p in players],
        "2B": [p.twoB for p in players],
        "3B": [p.threeB for p in players],
        "HR": [p.hr for p in players],
        "RBI": [p.rbi for p in players],
        "SB": [p.sb for p in players],
        "CS": [p.cs for p in players],
        "BB": [p.bb for p in players],
        "SO": [p.so for p in players],
        "BA": [p.ba for p in players],
        "OBP": [p.obp for p in players],
        "SLG": [p.slg for p in players],
        "OPS": [p.ops for p in players],
        "OPS+": [p.opsPlus for p in players],
        "TB": [p.tb for p in players],
        "GDP": [p.gdp for p in players],
        "HBP": [p.hbp for p in players],
        "SH": [p.sh for p in players],
        "SF": [p.sf for p in players],
        "IBB": [p.ibb for p in players],
        "SpF": [p.spf for p in players]
    })

    df3['Name'] = pd.Categorical(df3['Name'], categories=custom_order3, ordered=True)
    df3 = df3.sort_values('Name')
    index = 0
    for name in df3["Name"]:
        for player in players3:
            if player.player == name:
                players[index] = player
        index+=1

    p_cs = PTM(players)
    PTMS_cs = p_cs.build_player_objects()
    
    cs = CycleStart(PTMS_cs, players)
    optimal_lineup3 = cs.StartCycle()
    print("Optimal 3:")
    print(optimal_lineup3)
    return [optimal_lineup1, optimal_lineup2, optimal_lineup3]
    