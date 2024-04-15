from . import db
from flask_login import UserMixin

class Lineup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lineup_name = db.Column(db.String(25))
    player1id = db.Column(db.Integer)
    player2id = db.Column(db.Integer)
    player3id = db.Column(db.Integer)
    player4id = db.Column(db.Integer)
    player5id = db.Column(db.Integer)
    player6id = db.Column(db.Integer)
    player7id = db.Column(db.Integer)
    player8id = db.Column(db.Integer)
    player9id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(150))
    season = db.Column(db.String(4))
    team = db.Column(db.String(10))
    plate_appearances = db.Column(db.Integer)
    hits = db.Column(db.Integer)
    oneB = db.Column(db.Integer)
    twoB = db.Column(db.Integer)
    threeB = db.Column(db.Integer)
    home_runs = db.Column(db.Integer)
    walks = db.Column(db.Integer)
    intentional_walks = db.Column(db.Integer)
    stolen_bases = db.Column(db.Integer)
    sprint_coeff = db.Column(db.Float)


class CustomPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(150))
    season = db.Column(db.String(4))
    team = db.Column(db.String(10))
    plate_appearances = db.Column(db.Integer)
    hits = db.Column(db.Integer)
    oneB = db.Column(db.Integer)
    twoB = db.Column(db.Integer)
    threeB = db.Column(db.Integer)
    home_runs = db.Column(db.Integer)
    walks = db.Column(db.Integer)
    intentional_walks = db.Column(db.Integer)
    stolen_bases = db.Column(db.Integer)
    sprint_coeff = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    lineups = db.relationship('Lineup')
    custom_players = db.relationship('CustomPlayer')