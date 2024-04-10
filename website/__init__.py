from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

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
    app.config['MAIL_SERVER'] = 'smtp.freesmtpservers.com'
    app.config['MAIL_PORT'] = 25
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USERNAME'] = None
    app.config['MAIL_PASSWORD'] = None

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

    from .models import User, Lineup, Player, CustomPlayer

    with app.app_context():
        db.create_all()

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