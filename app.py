"""
King's Choice Management Web App
Main Flask application entry point

This app manages MVP assignments and alliance winners for the King's Choice game
with rotation logic to ensure fair distribution of awards.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_babel import Babel, gettext, ngettext, get_locale
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "kings_choice.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Babel configuration
app.config['LANGUAGES'] = {
    'en': 'English',
    'ru': 'Русский'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'ru'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

def get_locale():
    """Determine the best language for the user"""
    # Check if language is set in cookies
    if 'language' in request.cookies:
        return request.cookies.get('language')
    
    # Check if language is in URL parameters
    if request.args.get('lang'):
        return request.args.get('lang')
    
    # Check Accept-Language header
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or app.config['BABEL_DEFAULT_LOCALE']

# Initialize Babel
babel = Babel(app)

# Configure Babel with locale selector
babel.init_app(app, locale_selector=get_locale)

# Make get_locale available in templates
@app.context_processor
def inject_get_locale():
    return dict(get_locale=get_locale)

# Initialize database
from database import db, init_app, create_all_tables
init_app(app)

# Import models after database initialization
from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment, Guide, GuideCategory, Blacklist

# Import routes
from routes import main_routes, player_routes, alliance_routes, event_routes, guide_routes, blacklist_routes

# Register blueprints
app.register_blueprint(main_routes.bp)
app.register_blueprint(player_routes.bp)
app.register_blueprint(alliance_routes.bp)
app.register_blueprint(event_routes.bp)
app.register_blueprint(guide_routes.bp)
app.register_blueprint(blacklist_routes.bp)

@app.route('/set_language/<language>')
def set_language(language=None):
    """Set the language for the user"""
    if language and language in app.config['LANGUAGES']:
        response = redirect(request.referrer or url_for('main.dashboard'))
        response.set_cookie('language', language, max_age=60*60*24*365)  # 1 year
        return response
    return redirect(url_for('main.dashboard'))

def create_tables():
    """Create all database tables including blacklist"""
    create_all_tables(app)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)