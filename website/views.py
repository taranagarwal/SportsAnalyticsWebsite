from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from . models import Player
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
    actualNames = ['Player Name', 'Season', 'Position', 'Age', 'Team', 'Games', 'Plate Appearances', 'At Bats', 'Runs', 'Hits', 'Doubles', 'Triples', 'Home Runs', 'Runs Batted In', 'Stolen Bases', 'Caught Stealing', 'Walks', 'Strikeouts', 'Batting Average', 'On Base Percentage', 'Slugging', 'OPS', 'OPS+', 'Total Bases', 'Ground Out Double Plays', 'Hit By Pitch', 'Sacrafice Bunts', 'Sacrafice Flys', 'Intentional Walks', 'Speed Factor']
    i = 0
    id_to_name = {}
    data = request.get_json()
    player_data = data.get('stat')
    for id in player_data:
        id_to_name[id] = actualNames[i]
        i += 1
    errorMsg = "Incorrectly formatted data: "
    ogError = len(errorMsg)
    type = ''
    count = 0
    for id in player_data:
        try:
            if id in ['season','pos', 'age', 'team'] and player_data[id] == '':
                pass
            elif id in ['age', 'g', 'pa', 'ab', 'r', 'h', 'twoB', 'threeB', 'hr', 'rbi', 'sb', 'cs', 'bb', 'so', 'opsPlus', 'tb', 'gdp', 'hbp', 'sh', 'sf', 'ibb', 'spf']:
                type = 'integer'
                player_data[id] = int(player_data[id])
            elif id in ['ba', 'obp', 'slg', 'ops', ]:
                type = 'float'
                player_data[id] = float(player_data[id])
            elif id == 'player':
                #this check doesn't work
                print(id)
                if Player.query.filter(Player.player.ilike(player_data[id]), Player.isCustom == True, Player.user_id == current_user.id).first():
                    if count == 0: "player name must be unique"
                    else: errorMsg += ", player name must be unique"
                if len(player_data[id]) > 150:
                    if count == 0: errorMsg += "player name must be 150 characters or less"
                    else: errorMsg += ", player name must be 150 characters or less"
                    count+=1
            elif id == 'season':
                if len(player_data[id]) > 4:
                    if count == 0: errorMsg += "season year must be 4 characters or less"
                    else: errorMsg += ", season year must be 4 characters or less"
                    count+=1
            elif id == 'pos':
                if len(player_data[id]) > 150:
                    if count == 0: errorMsg += "position must be 150 characters or less"
                    else: errorMsg += ", position must be 150 characters or less"
                    count+=1
            elif id == 'team':
                if len(player_data[id]) > 50:
                    if count == 0: errorMsg += "position must be 150 characters or less"
                    else: errorMsg += ", position must be 150 characters or less"
                    count+=1
        except ValueError:
            if count == 0: errorMsg = errorMsg + f'{id_to_name[id]} must be of the type: {type}'
            else: errorMsg = errorMsg + f', {id_to_name[id]} must be of the type: {type}'
            count+=1

    if len(errorMsg) > ogError:
        flash(f'{errorMsg}', category='error')
        return jsonify({'error': f'{errorMsg}'}), 400
    
    new_player = Player(
        player=player_data['player'],
        season=player_data['season'],
        pos=player_data['pos'],
        age=player_data['age'],
        team=player_data['team'],
        g=player_data['g'],
        pa=player_data['pa'],
        ab=player_data['ab'],
        r=player_data['r'],
        h=player_data['h'],
        twoB=player_data['twoB'],
        threeB=player_data['threeB'],
        hr=player_data['hr'],
        rbi=player_data['rbi'],
        sb=player_data['sb'],
        cs=player_data['cs'],
        bb=player_data['bb'],
        so=player_data['so'],
        ba=player_data['ba'],
        obp=player_data['obp'],
        slg=player_data['slg'],
        ops=player_data['ops'],
        opsPlus=player_data['opsPlus'],
        tb=player_data['tb'],
        gdp=player_data['gdp'],
        hbp=player_data['hbp'],
        sh=player_data['sh'],
        sf=player_data['sf'],
        ibb=player_data['ibb'],
        spf=player_data['spf'],
        isCustom=True
    )

    print(Player.query.filter_by(player=player_data['player']).first())
    db.session.add(new_player)
    db.session.commit()

    flash('Player added successfully', category='success')
    return jsonify({'message': "Player added successfully"}), 200
