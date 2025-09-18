"""
Main Routes Module

Handles the main dashboard and navigation routes.
Shows current MVP player and winning alliance information.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Player, Alliance, Event, MVPAssignment, WinnerAssignment, Blacklist
from database import db
from database_manager import query_user_data, get_user_data_by_id, get_user_data_optimized
from utils.cache import cache_response
from datetime import datetime, timedelta

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
        # Use optimized single query to get all dashboard data
        data = get_user_data_optimized(current_user.id, include_stats=True)
        
        # Get feedback statistics for admin users
        feedback_stats = {}
        if current_user.is_admin:
            try:
                from models import Feedback
                feedback_stats = {
                    'total_feedback': Feedback.query.count(),
                    'pending_feedback': Feedback.query.filter_by(status='pending').count(),
                    'recent_feedback': Feedback.query.filter(
                        Feedback.created_at >= datetime.now() - timedelta(days=7)
                    ).count()
                }
            except ImportError:
                # Feedback model not available, skip feedback stats
                feedback_stats = {
                    'total_feedback': 0,
                    'pending_feedback': 0,
                    'recent_feedback': 0
                }
        
        # Use classic template
        return render_template('dashboard.html', 
                             current_mvp=data['current_mvp'],
                             current_winner=data['current_winner'],
                             recent_events=data['recent_events'],
                             recent_assignments=data.get('recent_assignments', []),
                             total_players=data['stats']['total_players'],
                             total_alliances=data['stats']['total_alliances'],
                             total_events=data['stats']['total_events'],
                             total_assignments=data['stats'].get('total_assignments', 0),
                             active_players=data['stats'].get('active_players', 0),
                             excluded_players=data['stats'].get('excluded_players', 0),
                             recent_events_count=data['stats'].get('recent_events', 0),
                             total_blacklist_entries=data['stats']['total_blacklist_entries'],
                             feedback_stats=feedback_stats)
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
)

@bp.route('/api/dashboard-data')
@login_required
@cache_response(timeout_seconds=30)
def dashboard_data():
    """
    API endpoint to get dashboard data in JSON format
    
    Returns current MVP, winning alliance, and stats as JSON
    Useful for AJAX updates or mobile apps
    """
    try:
        # Use optimized single query to get all dashboard data
        data = get_user_data_optimized(current_user.id, include_stats=True)
        
        # Convert events to dict format for JSON response
        recent_events = []
        for event in data['recent_events']:
            event_data = event.to_dict()
            event_data['mvp_assignments'] = [assignment.to_dict() for assignment in event.mvp_assignments]
            event_data['mvp_players'] = event.mvp_players
            event_data['mvp_count'] = event.mvp_count
            recent_events.append(event_data)
        
        return jsonify({
            'success': True,
            'current_mvp': data['current_mvp'].to_dict() if data['current_mvp'] else None,
            'current_winner': data['current_winner'].to_dict() if data['current_winner'] else None,
            'recent_events': recent_events,
            'stats': data['stats']
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
