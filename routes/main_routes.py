"""
Main Routes Module

Handles the main dashboard and navigation routes.
Shows current MVP player and winning alliance information.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist, Guide
from database import db
from database_manager import query_user_data, get_user_data_by_id
from telegram_bot import send_manual_message

# Create blueprint for main routes
bp = Blueprint('main', __name__)

@bp.route('/')
@login_required
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
        # Get current MVP player (user-specific)
        current_mvp = query_user_data(Player, current_user.id, is_current_mvp=True)
        current_mvp = current_mvp[0] if current_mvp else None
        
        # Get current winning alliance (user-specific)
        current_winner = query_user_data(Alliance, current_user.id, is_current_winner=True)
        current_winner = current_winner[0] if current_winner else None
        
        # Get all events with MVP assignments (user-specific)
        recent_events = []
        events = query_user_data(Event, current_user.id)
        events_with_mvp = [e for e in events if e.has_mvp]
        events_with_mvp.sort(key=lambda x: x.event_date, reverse=True)
        
        for event in events_with_mvp:
            # Get all MVP assignments for this event (since events can be reused)
            mvp_assignments = query_user_data(MVPAssignment, current_user.id, event_id=event.id)
            mvp_assignments.sort(key=lambda x: x.assigned_at, reverse=True)
            
            # Add MVP data to event object for template access
            event.mvp_assignments = mvp_assignments
            event.mvp_players = [assignment.player.name for assignment in mvp_assignments if hasattr(assignment, 'player')]
            event.mvp_count = len(mvp_assignments)
            
            recent_events.append(event)
        
        # Get total counts for stats (user-specific)
        total_players = len(query_user_data(Player, current_user.id))
        total_alliances = len(query_user_data(Alliance, current_user.id))
        total_events = len(query_user_data(Event, current_user.id))
        total_blacklist_entries = len(query_user_data(Blacklist, current_user.id))
        total_guides = len(query_user_data(Guide, current_user.id))
        
        return render_template('dashboard.html', 
                             current_mvp=current_mvp,
                             current_winner=current_winner,
                             recent_events=recent_events,
                             total_players=total_players,
                             total_alliances=total_alliances,
                             total_events=total_events,
                             total_blacklist_entries=total_blacklist_entries,
                             total_guides=total_guides)
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        return render_template('dashboard.html', 
                             error="Failed to load dashboard data",
                             current_mvp=None,
                             current_winner=None,
                             recent_events=[],
                             total_players=0,
                             total_alliances=0,
                             total_events=0,
                             total_blacklist_entries=0,
                             total_guides=0)

@bp.route('/api/dashboard-data')
@login_required
def dashboard_data():
    """
    API endpoint to get dashboard data in JSON format
    
    Returns current MVP, winning alliance, and stats as JSON
    Useful for AJAX updates or mobile apps
    """
    try:
        # Get current MVP player (user-specific)
        current_mvp = query_user_data(Player, current_user.id, is_current_mvp=True)
        current_mvp = current_mvp[0] if current_mvp else None
        
        # Get current winning alliance (user-specific)
        current_winner = query_user_data(Alliance, current_user.id, is_current_winner=True)
        current_winner = current_winner[0] if current_winner else None
        
        # Get all events with MVP assignments (user-specific)
        recent_events = []
        events = query_user_data(Event, current_user.id)
        events_with_mvp = [e for e in events if e.has_mvp]
        events_with_mvp.sort(key=lambda x: x.event_date, reverse=True)
        
        for event in events_with_mvp:
            event_data = event.to_dict()
            
            # Add ALL MVP assignments for this event (since events can be reused)
            mvp_assignments = query_user_data(MVPAssignment, current_user.id, event_id=event.id)
            mvp_assignments.sort(key=lambda x: x.assigned_at, reverse=True)
            
            if mvp_assignments:
                event_data['mvp_assignments'] = [assignment.to_dict() for assignment in mvp_assignments]
                event_data['mvp_players'] = [assignment.player.name for assignment in mvp_assignments if hasattr(assignment, 'player')]
                event_data['mvp_count'] = len(mvp_assignments)
            else:
                event_data['mvp_assignments'] = []
                event_data['mvp_players'] = []
                event_data['mvp_count'] = 0
            
            # Add winner info if exists
            winner_assignments = query_user_data(WinnerAssignment, current_user.id, event_id=event.id)
            if winner_assignments:
                event_data['winning_alliance'] = winner_assignments[0].alliance.name if hasattr(winner_assignments[0], 'alliance') else None
            
            recent_events.append(event_data)
        
        # Get total counts for stats (user-specific)
        stats = {
            'total_players': len(query_user_data(Player, current_user.id)),
            'total_alliances': len(query_user_data(Alliance, current_user.id)),
            'total_events': len(query_user_data(Event, current_user.id)),
            'mvp_assignments': len(query_user_data(MVPAssignment, current_user.id)),
            'winner_assignments': len(query_user_data(WinnerAssignment, current_user.id))
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
@login_required
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