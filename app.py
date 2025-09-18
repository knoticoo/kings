"""
King's Choice Management Web App
Main Flask application entry point

This app manages MVP assignments and alliance winners for the King's Choice game
with rotation logic to ensure fair distribution of awards.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_babel import Babel, gettext, ngettext, get_locale
from flask_login import LoginManager, current_user
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from functools import wraps

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Simple in-memory cache for API responses
api_cache = {}

def cache_response(timeout_seconds=30):
    """Decorator to cache API responses"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}_{str(args)}_{str(kwargs)}"
            now = datetime.now()
            
            # Check if cached response exists and is still valid
            if cache_key in api_cache:
                cached_data, timestamp = api_cache[cache_key]
                if now - timestamp < timedelta(seconds=timeout_seconds):
                    return cached_data
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            api_cache[cache_key] = (result, now)
            
            # Clean old cache entries
            for key in list(api_cache.keys()):
                if now - api_cache[key][1] > timedelta(seconds=timeout_seconds * 2):
                    del api_cache[key]
            
            return result
        return decorated_function
    return decorator

# Database configuration
from config import Config
app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_main_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

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
from models import User, Player, Alliance, Event, MVPAssignment, WinnerAssignment, Guide, GuideCategory, Blacklist

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes
from routes import main_routes, player_routes, alliance_routes, event_routes, guide_routes, blacklist_routes
from routes import user_settings_routes
from auth import auth_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_routes.bp)
app.register_blueprint(player_routes.bp)
app.register_blueprint(alliance_routes.bp)
app.register_blueprint(event_routes.bp)
app.register_blueprint(guide_routes.bp)
app.register_blueprint(blacklist_routes.bp)
app.register_blueprint(user_settings_routes.bp)

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
    # Print configuration for debugging
    Config.print_config()
    print(f"🎯 Deployment type: {Config.detect_deployment_type()}")
    print()
    
    # Ensure directories exist
    Config.ensure_data_directories()
    
    create_tables()
    
    # Don't start any bots globally - they will be started per-user when needed
    print("🚀 Starting King's Choice Management Web App...")
    print("📝 Bots will be started individually when users configure their tokens")
    
    app.run(debug=True, host='0.0.0.0', port=5001)