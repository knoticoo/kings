#!/usr/bin/env python3
"""
Simple script to create the blacklist database
"""

import os
from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create Flask app
app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "kings_choice.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'temp-key'

# Configure blacklist database
app.config['BLACKLIST_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "blacklist.db")}'
app.config['SQLALCHEMY_BINDS'] = {
    'blacklist': app.config['BLACKLIST_DATABASE_URI']
}

# Initialize database
db = SQLAlchemy(app)

# Define Blacklist model
class Blacklist(db.Model):
    __tablename__ = 'blacklist'
    __bind_key__ = 'blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    alliance_name = db.Column(db.String(100), nullable=True)
    player_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
if __name__ == '__main__':
    with app.app_context():
        # Create all tables for the blacklist bind
        db.create_all(bind_key='blacklist')
        print('Blacklist database tables created successfully!')
        
        # Verify the database was created
        if os.path.exists(os.path.join(basedir, 'blacklist.db')):
            print('blacklist.db file created successfully!')
        else:
            print('ERROR: blacklist.db file was not created!')