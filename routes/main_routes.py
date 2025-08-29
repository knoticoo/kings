"""
Main Routes Module

Handles the main dashboard and navigation routes.
Shows current MVP player and winning alliance information.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment
from database import db
from telegram_bot import send_manual_message

# Create blueprint for main routes
bp = Blueprint('main', __name__)

@bp.route('/')
def dashboard():
    """
    Main dashboard route - shows current MVP and winning alliance
    
    This is the home page that displays:
    - Current MVP player with icon
    - Current winning alliance with icon
    - Recent events summary
    - Quick stats
    """
    try:
        # Get current MVP player
        current_mvp = Player.query.filter_by(is_current_mvp=True).first()
        
        # Get current winning alliance
        current_winner = Alliance.query.filter_by(is_current_winner=True).first()
        
        # Get recent events (last 10)
        recent_events = Event.query.order_by(Event.event_date.desc()).limit(10).all()
        
        # Get total counts for stats
        total_players = Player.query.count()
        total_alliances = Alliance.query.count()
        total_events = Event.query.count()
        
        return render_template('dashboard.html', 
                             current_mvp=current_mvp,
                             current_winner=current_winner,
                             recent_events=recent_events,
                             total_players=total_players,
                             total_alliances=total_alliances,
                             total_events=total_events)
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        return render_template('dashboard.html', 
                             error="Failed to load dashboard data")

@bp.route('/api/dashboard-data')
def dashboard_data():
    """
    API endpoint to get dashboard data in JSON format
    
    Returns current MVP, winning alliance, and stats as JSON
    Useful for AJAX updates or mobile apps
    """
    try:
        # Get current MVP player
        current_mvp = Player.query.filter_by(is_current_mvp=True).first()
        
        # Get current winning alliance
        current_winner = Alliance.query.filter_by(is_current_winner=True).first()
        
        # Get recent events with their assignments
        recent_events = []
        events = Event.query.order_by(Event.event_date.desc()).limit(10).all()
        
        for event in events:
            event_data = event.to_dict()
            
            # Add MVP info if exists
            mvp_assignment = MVPAssignment.query.filter_by(event_id=event.id).first()
            if mvp_assignment:
                event_data['mvp_player'] = mvp_assignment.player.name
            
            # Add winner info if exists
            winner_assignment = WinnerAssignment.query.filter_by(event_id=event.id).first()
            if winner_assignment:
                event_data['winning_alliance'] = winner_assignment.alliance.name
            
            recent_events.append(event_data)
        
        # Get total counts for stats
        stats = {
            'total_players': Player.query.count(),
            'total_alliances': Alliance.query.count(),
            'total_events': Event.query.count(),
            'mvp_assignments': MVPAssignment.query.count(),
            'winner_assignments': WinnerAssignment.query.count()
        }
        
        return jsonify({
            'success': True,
            'current_mvp': current_mvp.to_dict() if current_mvp else None,
            'current_winner': current_winner.to_dict() if current_winner else None,
            'recent_events': recent_events,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/telegram-message', methods=['GET', 'POST'])
def telegram_message():
    """
    Manual Telegram message posting interface
    
    GET: Show form to enter text
    POST: Translate text to Russian and send to Telegram channel
    """
    if request.method == 'POST':
        try:
            message_text = request.form.get('message', '').strip()
            
            if not message_text:
                flash('Message text is required', 'error')
                return render_template('telegram_message.html')
            
            # Send message via Telegram (will be auto-translated to Russian)
            success = send_manual_message(message_text)
            
            if success:
                flash('Message sent successfully to Telegram channel!', 'success')
                print(f"Manual Telegram message sent: {message_text[:50]}...")
            else:
                flash('Failed to send message to Telegram channel', 'error')
                
            return render_template('telegram_message.html')
            
        except Exception as e:
            print(f"Error sending manual Telegram message: {str(e)}")
            flash('An error occurred while sending the message', 'error')
            return render_template('telegram_message.html')
    
    return render_template('telegram_message.html')