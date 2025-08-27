"""
King's Choice Management Web App
Main Flask application entry point

This app manages MVP assignments and alliance winners for the King's Choice game
with rotation logic to ensure fair distribution of awards.
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "kings_choice.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize database
db = SQLAlchemy(app)

# Import models after db initialization
from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment

# Import routes
from routes import main_routes, player_routes, alliance_routes, event_routes

# Register blueprints
app.register_blueprint(main_routes.bp)
app.register_blueprint(player_routes.bp)
app.register_blueprint(alliance_routes.bp)
app.register_blueprint(event_routes.bp)

def create_tables():
    """Create all database tables"""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)