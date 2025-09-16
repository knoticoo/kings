"""
User Settings Routes Module

Handles user-specific settings including bot configuration and management.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User
from database import db
from user_bot_manager import start_user_bots, stop_user_bots, get_bot_status

# Create blueprint for user settings routes
bp = Blueprint('user_settings', __name__, url_prefix='/settings')

@bp.route('/')
@login_required
def settings():
    """Display user settings page"""
    return render_template('user_settings/settings.html', user=current_user)

@bp.route('/bots', methods=['GET', 'POST'])
@login_required
def bot_settings():
    """Manage bot settings for the current user"""
    if request.method == 'POST':
        try:
            # Get form data
            discord_enabled = request.form.get('discord_enabled') == 'on'
            discord_token = request.form.get('discord_token', '').strip()
            discord_channel = request.form.get('discord_channel', '').strip()
            
            telegram_enabled = request.form.get('telegram_enabled') == 'on'
            telegram_token = request.form.get('telegram_token', '').strip()
            telegram_chat = request.form.get('telegram_chat', '').strip()
            
            # Update user settings
            current_user.discord_enabled = discord_enabled
            current_user.discord_bot_token = discord_token if discord_token else None
            current_user.discord_channel_id = discord_channel if discord_channel else None
            
            current_user.telegram_enabled = telegram_enabled
            current_user.telegram_bot_token = telegram_token if telegram_token else None
            current_user.telegram_chat_id = telegram_chat if telegram_chat else None
            
            db.session.commit()
            
            # Start/stop bots based on settings
            if discord_enabled and discord_token:
                result = start_user_bots(
                    current_user.id,
                    discord_token=discord_token,
                    discord_channel=discord_channel
                )
                if result.get('discord'):
                    flash('Discord bot started successfully', 'success')
                else:
                    flash('Failed to start Discord bot', 'error')
            elif not discord_enabled:
                stop_user_bots(current_user.id)
                flash('Discord bot stopped', 'info')
            
            if telegram_enabled and telegram_token:
                result = start_user_bots(
                    current_user.id,
                    telegram_token=telegram_token,
                    telegram_chat=telegram_chat
                )
                if result.get('telegram'):
                    flash('Telegram bot started successfully', 'success')
                else:
                    flash('Failed to start Telegram bot', 'error')
            elif not telegram_enabled:
                stop_user_bots(current_user.id)
                flash('Telegram bot stopped', 'info')
            
            flash('Bot settings updated successfully', 'success')
            return redirect(url_for('user_settings.bot_settings'))
            
        except Exception as e:
            print(f"Error updating bot settings: {str(e)}")
            db.session.rollback()
            flash('Failed to update bot settings', 'error')
    
    # GET request - show bot settings
    bot_status = get_bot_status()
    return render_template('user_settings/bot_settings.html', 
                         user=current_user,
                         bot_status=bot_status)

@bp.route('/bots/test-discord', methods=['POST'])
@login_required
def test_discord_bot():
    """Test Discord bot connection"""
    try:
        if not current_user.discord_bot_token:
            return jsonify({'success': False, 'error': 'No Discord token configured'})
        
        # Start bot if not running
        if not start_user_bots(current_user.id, 
                              discord_token=current_user.discord_bot_token,
                              discord_channel=current_user.discord_channel_id):
            return jsonify({'success': False, 'error': 'Failed to start Discord bot'})
        
        # Send test message
        from user_bot_manager import send_discord_message
        success = send_discord_message(current_user.id, "🤖 Discord bot connection test")
        
        if success:
            return jsonify({'success': True, 'message': 'Discord bot test successful'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send test message'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/bots/test-telegram', methods=['POST'])
@login_required
def test_telegram_bot():
    """Test Telegram bot connection"""
    try:
        if not current_user.telegram_bot_token or not current_user.telegram_chat_id:
            return jsonify({'success': False, 'error': 'No Telegram token or chat ID configured'})
        
        # Start bot if not running
        if not start_user_bots(current_user.id,
                              telegram_token=current_user.telegram_bot_token,
                              telegram_chat=current_user.telegram_chat_id):
            return jsonify({'success': False, 'error': 'Failed to start Telegram bot'})
        
        # Send test message
        from user_bot_manager import send_telegram_message
        success = send_telegram_message(current_user.id, "🤖 Telegram bot connection test")
        
        if success:
            return jsonify({'success': True, 'message': 'Telegram bot test successful'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send test message'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/bots/stop', methods=['POST'])
@login_required
def stop_bots():
    """Stop all bots for the current user"""
    try:
        result = stop_user_bots(current_user.id)
        
        # Update user settings
        current_user.discord_enabled = False
        current_user.telegram_enabled = False
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'All bots stopped successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@bp.route('/api/bot-status')
@login_required
def api_bot_status():
    """API endpoint to get bot status for current user"""
    try:
        from user_bot_manager import bot_manager
        
        status = {
            'discord_running': bot_manager.is_discord_bot_running(current_user.id),
            'telegram_running': bot_manager.is_telegram_bot_running(current_user.id),
            'discord_enabled': current_user.discord_enabled,
            'telegram_enabled': current_user.telegram_enabled,
            'has_discord_token': bool(current_user.discord_bot_token),
            'has_telegram_token': bool(current_user.telegram_bot_token)
        }
        
        return jsonify({'success': True, 'status': status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})