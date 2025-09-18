"""
Authentication module for King's Choice Management App

Handles user authentication, login/logout, and user management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import sqlite3
from database import db
from models import User
from config import Config

# Create blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

def create_user_database(user_id, username):
    """Create a separate database file for a user"""
    # Use configuration to get the correct path
    user_db_path = Config.get_user_database_path(user_id, username)
    
    # Ensure the user database directory exists
    Config.ensure_data_directories()
    
    # Create the database file and initialize tables
    conn = sqlite3.connect(user_db_path)
    cursor = conn.cursor()
    
    # Create all necessary tables for the user
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            is_current_mvp BOOLEAN DEFAULT 0,
            is_excluded BOOLEAN DEFAULT 0,
            mvp_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alliances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            is_current_winner BOOLEAN DEFAULT 0,
            win_count INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            event_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            has_mvp BOOLEAN DEFAULT 0,
            has_winner BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mvp_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (player_id) REFERENCES players (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS winner_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alliance_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alliance_id) REFERENCES alliances (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guide_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(100) NOT NULL,
            description TEXT,
            icon VARCHAR(50) DEFAULT 'bi-book',
            sort_order INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS guides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title VARCHAR(200) NOT NULL,
            slug VARCHAR(200) NOT NULL,
            content TEXT NOT NULL,
            excerpt TEXT,
            category_id INTEGER NOT NULL,
            featured_image VARCHAR(500),
            is_published BOOLEAN DEFAULT 1,
            is_featured BOOLEAN DEFAULT 0,
            view_count INTEGER DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, slug),
            FOREIGN KEY (category_id) REFERENCES guide_categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blacklist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            alliance_name VARCHAR(100),
            player_name VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    return user_db_path

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    username = current_user.username
    logout_user()
    flash(f'Goodbye, {username}!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/admin/users')
@login_required
def admin_users():
    """Admin panel for user management"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('auth/admin_users.html', users=users)

@auth_bp.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new user (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = 'is_admin' in request.form
        
        # Telegram configuration
        telegram_bot_token = request.form.get('telegram_bot_token', '').strip()
        telegram_chat_id = request.form.get('telegram_chat_id', '').strip()
        telegram_enabled = 'telegram_enabled' in request.form
        
        # Discord configuration
        discord_bot_token = request.form.get('discord_bot_token', '').strip()
        discord_channel_id = request.form.get('discord_channel_id', '').strip()
        discord_enabled = 'discord_enabled' in request.form
        
        if not username or not email or not password:
            flash('Username, email and password are required', 'error')
            return render_template('auth/create_user.html')
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/create_user.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('auth/create_user.html')
        
        # Get next user ID for database path
        max_id = db.session.query(db.func.max(User.id)).scalar() or 0
        next_user_id = max_id + 1
        
        # Create user database path using configuration
        user_db_path = Config.get_user_database_path(next_user_id, username)
        
        # Create new user
        user = User(
            username=username,
            email=email,
            is_admin=is_admin,
            database_path=user_db_path,
            telegram_bot_token=telegram_bot_token if telegram_bot_token else None,
            telegram_chat_id=telegram_chat_id if telegram_chat_id else None,
            telegram_enabled=telegram_enabled and bool(telegram_bot_token and telegram_chat_id),
            discord_bot_token=discord_bot_token if discord_bot_token else None,
            discord_channel_id=discord_channel_id if discord_channel_id else None,
            discord_enabled=discord_enabled and bool(discord_bot_token and discord_channel_id)
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Create user's database
            create_user_database(user.id, username)
            
            flash(f'User {username} created successfully!', 'success')
            return redirect(url_for('auth.admin_users'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('auth/create_user.html')

@auth_bp.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete user (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if user_id == current_user.id:
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('auth.admin_users'))
    
    user = User.query.get_or_404(user_id)
    
    try:
        # Delete user's database file
        if os.path.exists(user.database_path):
            os.remove(user.database_path)
        
        db.session.delete(user)
        db.session.commit()
        
        flash(f'User {user.username} deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/admin/toggle-user/<int:user_id>', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    """Toggle user active status (admin only)"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    if user_id == current_user.id:
        flash('Cannot deactivate your own account', 'error')
        return redirect(url_for('auth.admin_users'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} {status} successfully!', 'success')
    
    return redirect(url_for('auth.admin_users'))

@auth_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    """User settings page for Telegram and Discord configuration"""
    if request.method == 'POST':
        # Get form data
        telegram_bot_token = request.form.get('telegram_bot_token', '').strip()
        telegram_chat_id = request.form.get('telegram_chat_id', '').strip()
        telegram_enabled = 'telegram_enabled' in request.form
        
        discord_bot_token = request.form.get('discord_bot_token', '').strip()
        discord_channel_id = request.form.get('discord_channel_id', '').strip()
        discord_enabled = 'discord_enabled' in request.form
        
        try:
            # Update user settings
            current_user.telegram_bot_token = telegram_bot_token if telegram_bot_token else None
            current_user.telegram_chat_id = telegram_chat_id if telegram_chat_id else None
            current_user.telegram_enabled = telegram_enabled and bool(telegram_bot_token and telegram_chat_id)
            
            current_user.discord_bot_token = discord_bot_token if discord_bot_token else None
            current_user.discord_channel_id = discord_channel_id if discord_channel_id else None
            current_user.discord_enabled = discord_enabled and bool(discord_bot_token and discord_channel_id)
            
            db.session.commit()
            flash('Settings updated successfully!', 'success')
            return redirect(url_for('auth.user_settings'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating settings: {str(e)}', 'error')
    
    return render_template('auth/user_settings.html')