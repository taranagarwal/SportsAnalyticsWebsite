from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail
import json
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

db = SQLAlchemy()
mail = Mail()
DB_NAME = "database.db"
MAIL_SERVER = 'smtp.freesmtpservers.com' #need a mail server -- testing with a free one that doesn't work
MAIL_PORT = 25
MAIL_USE_TLS = False
MAIL_USERNAME = None
MAIL_PASSWORD = None


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'anthonyvolpeissogoodatshortstop'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['MAIL_SERVER'] = MAIL_SERVER
    app.config['MAIL_PORT'] = MAIL_PORT
    app.config['MAIL_USE_TLS'] = MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD

    # Initialize extensions with the app
    mail.init_app(app)
    db.init_app(app)



    from .views import views
    from .auth import auth
    from .build import build
    from .profile import profile


    app.register_blueprint(views, url_prefix= '/')
    app.register_blueprint(auth, url_prefix= '/')
    app.register_blueprint(build, url_prefix= '/')
    app.register_blueprint(profile, url_prefix= '/profile')

    from .models import Player, User, Lineup

    with app.app_context():
        db.create_all() 
        preload_players()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database')

def preload_players(filename='data.json'):
    from .models import Player
    base_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of this file
    json_path = os.path.join(base_dir, filename)  # Construct the full path to 'data.json'

    # Open the JSON file and read the data
    with open(json_path, 'r') as file:
        players_data = json.load(file)

    # Add Player instances to the session
    for player_dict in players_data:
        player = Player.query.filter_by(player=player_dict['player'], season=player_dict['season']).first()
        if not player:  # Only add the player if they don't already exist
            player = Player(**player_dict)
            db.session.add(player)
    
    # Commit the session to save the players to the database
    db.session.commit()