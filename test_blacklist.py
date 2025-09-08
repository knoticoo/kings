#!/usr/bin/env python3
"""
Test script to verify blacklist functionality
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
    
    def to_dict(self):
        """Convert blacklist entry to dictionary for API responses"""
        return {
            'id': self.id,
            'alliance_name': self.alliance_name,
            'player_name': self.player_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Test the functionality
if __name__ == '__main__':
    with app.app_context():
        try:
            # Test querying the blacklist (this is what was failing before)
            blacklist_entries = Blacklist.query.order_by(Blacklist.created_at.desc()).all()
            print(f"✅ Successfully loaded blacklist data: {len(blacklist_entries)} entries found")
            
            # Test adding a sample entry
            test_entry = Blacklist(
                alliance_name="TestAlliance",
                player_name="TestPlayer"
            )
            
            db.session.add(test_entry)
            db.session.commit()
            print("✅ Successfully added test blacklist entry")
            
            # Test querying again
            blacklist_entries = Blacklist.query.order_by(Blacklist.created_at.desc()).all()
            print(f"✅ Successfully loaded blacklist data after addition: {len(blacklist_entries)} entries found")
            
            # Display the entries
            for entry in blacklist_entries:
                print(f"   - ID: {entry.id}, Alliance: {entry.alliance_name}, Player: {entry.player_name}")
            
            # Clean up the test entry
            db.session.delete(test_entry)
            db.session.commit()
            print("✅ Test entry cleaned up successfully")
            
            print("\n🎉 All blacklist functionality tests passed! The 'Failed to load blacklist data' error should be resolved.")
            
        except Exception as e:
            print(f"❌ Error testing blacklist functionality: {str(e)}")
            import traceback
            traceback.print_exc()