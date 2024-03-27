from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/home')
def home():
    return "<h1>Home</h1>"

@views.route('/build-lineup')
def build_lineup():
    return "<h1>Build Lineup</h1>"

@views.route('/about')
def about():
    return "<h1>About</h1>"

