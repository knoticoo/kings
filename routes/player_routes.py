"""
Player Routes Module

Handles all player-related operations:
- List all players with MVP status icons
- Add new players
- Edit/rename players
- Delete players
- Assign MVP with rotation logic
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Player, Event, MVPAssignment
from database import db
from database_manager import query_user_data, get_user_data_by_id, create_user_data, update_user_data, delete_user_data, user_database_context
from utils.rotation_logic import can_assign_mvp, get_eligible_players
from auth import get_effective_user_id, has_sub_user_permission

# Create blueprint for player routes
bp = Blueprint('players', __name__, url_prefix='/players')

def get_template_path(template_name):
    """Get template path based on user's template preference"""
    template = session.get('template', 'classic')
    return f'modern/{template_name}' if template == 'modern' else template_name

@bp.route('/')
@login_required
def list_players():
    """
    Display all players with their MVP status and management options
    
    Shows:
    - List of all players
    - MVP icon for current MVP
    - MVP count for each player
    - Add/Edit/Delete buttons
    """
    # Check permission
    if not has_sub_user_permission('can_view_players'):
        flash('You do not have permission to view players', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get effective user ID (handles sub-users)
        effective_user_id = get_effective_user_id()
        if not effective_user_id:
            flash('User data not found', 'error')
            return redirect(url_for('auth.login'))
        
        with user_database_context(effective_user_id) as session:
            players = query_user_data(Player, effective_user_id)
            players.sort(key=lambda x: x.name)
            
            # Add MVP assignment information to each player
            for player in players:
                # Get current MVP assignment for this player (only if they are current MVP)
                if player.is_current_mvp:
                    current_mvp_assignment = session.query(MVPAssignment).filter(
                        MVPAssignment.player_id == player.id
                    ).order_by(MVPAssignment.assigned_at.desc()).first()
                    
                    # Add assignment ID to player object for template use
                    player.mvp_assignment_id = current_mvp_assignment.id if current_mvp_assignment else None
                else:
                    player.mvp_assignment_id = None
            
            # Check rotation status for MVP assignments
            can_assign = can_assign_mvp(current_user.id)
            eligible_players = get_eligible_players(current_user.id) if can_assign else []
            
            return render_template(get_template_path('players/list.html'), 
                                 players=players,
                                 can_assign_mvp=can_assign,
                                 eligible_players=eligible_players)
    except Exception as e:
        print(f"Error in list_players route: {str(e)}")
        return render_template(get_template_path('players/list.html'), 
                             players=[],
                             error="Failed to load players")

@bp.route('/add', methods=['GET', 'POST'])
def add_player():
    """
    Add a new player to the system
    
    GET: Show add player form
    POST: Process new player creation
    """
    if request.method == 'POST':
        try:
            player_name = request.form.get('name', '').strip()
            
            if not player_name:
                flash('Player name is required', 'error')
                return render_template(get_template_path('players/add.html'))
            
            # Check if player already exists for this user
            existing_player = query_user_data(Player, current_user.id, name=player_name)
            if existing_player:
                flash(f'Player "{player_name}" already exists', 'error')
                return render_template(get_template_path('players/add.html'))
            
            # Create new player in user's database
            new_player = create_user_data(Player, current_user.id, name=player_name)
            
            flash(f'Player "{player_name}" added successfully', 'success')
            return redirect(url_for('players.list_players'))
            
        except Exception as e:
            print(f"Error adding player: {str(e)}")
            flash('Failed to add player', 'error')
            return render_template(get_template_path('players/add.html'))
    
    return render_template(get_template_path('players/add.html'))

@bp.route('/edit/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    """
    Edit/rename an existing player
    
    Args:
        player_id: ID of player to edit
    
    GET: Show edit form with current player data
    POST: Process player updates
    """
    player = get_user_data_by_id(Player, current_user.id, player_id)
    if not player:
        flash('Player not found', 'error')
        return redirect(url_for('players.list_players'))
    
    if request.method == 'POST':
        try:
            new_name = request.form.get('name', '').strip()
            
            if not new_name:
                flash('Player name is required', 'error')
                return render_template(get_template_path('players/edit.html'), player=player)
            
            # Check if new name conflicts with existing player (excluding current)
            existing_players = query_user_data(Player, current_user.id, name=new_name)
            existing_player = None
            for p in existing_players:
                if p.id != player_id:
                    existing_player = p
                    break
            
            if existing_player:
                flash(f'Player name "{new_name}" is already taken', 'error')
                return render_template(get_template_path('players/edit.html'), player=player)
            
            # Update player in user's database
            old_name = player.name
            update_user_data(Player, current_user.id, player_id, name=new_name)
            
            flash(f'Player renamed from "{old_name}" to "{new_name}"', 'success')
            return redirect(url_for('players.list_players'))
            
        except Exception as e:
            print(f"Error editing player: {str(e)}")
            flash('Failed to update player', 'error')
            return render_template(get_template_path('players/edit.html'), player=player)
    
    return render_template(get_template_path('players/edit.html'), player=player)

@bp.route('/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    """
    Delete a player from the system
    
    Args:
        player_id: ID of player to delete
    
    This will also delete all MVP assignments for this player
    """
    try:
        player = get_user_data_by_id(Player, current_user.id, player_id)
        if not player:
            flash('Player not found', 'error')
            return redirect(url_for('players.list_players'))
        
        player_name = player.name
        
        # Remove current MVP status if this player is current MVP
        if player.is_current_mvp:
            update_user_data(Player, current_user.id, player_id, is_current_mvp=False)
        
        # Delete player from user's database
        success = delete_user_data(Player, current_user.id, player_id)
        
        if success:
            flash(f'Player "{player_name}" deleted successfully', 'success')
        else:
            flash('Failed to delete player', 'error')
        
    except Exception as e:
        print(f"Error deleting player: {str(e)}")
        flash('Failed to delete player', 'error')
    
    return redirect(url_for('players.list_players'))

@bp.route('/toggle-exclusion/<int:player_id>', methods=['POST'])
def toggle_exclusion(player_id):
    """
    Toggle exclusion status for a player
    
    Args:
        player_id: ID of player to toggle exclusion for
    
    Excludes/includes player from MVP rotation while keeping them visible in the list
    """
    try:
        player = get_user_data_by_id(Player, current_user.id, player_id)
        if not player:
            flash('Player not found', 'error')
            return redirect(url_for('players.list_players'))
        
        # Toggle exclusion status
        new_exclusion_status = not player.is_excluded
        
        # If excluding the current MVP, remove their MVP status
        if new_exclusion_status and player.is_current_mvp:
            update_user_data(Player, current_user.id, player_id, 
                           is_excluded=new_exclusion_status, is_current_mvp=False)
            flash(f'Игрок "{player.name}" исключен из ротации MVP и снят с поста текущего MVP', 'warning')
        elif new_exclusion_status:
            update_user_data(Player, current_user.id, player_id, is_excluded=new_exclusion_status)
            flash(f'Игрок "{player.name}" исключен из ротации MVP', 'info')
        else:
            update_user_data(Player, current_user.id, player_id, is_excluded=new_exclusion_status)
            flash(f'Игрок "{player.name}" включен в ротацию MVP', 'success')
        
    except Exception as e:
        print(f"Error toggling exclusion: {str(e)}")
        flash('Не удалось изменить статус исключения', 'error')
    
    return redirect(url_for('players.list_players'))

@bp.route('/assign-mvp', methods=['GET', 'POST'])
def assign_mvp():
    """
    Assign MVP to a player for an event
    
    Implements rotation logic: can only assign MVP when all players have been MVP
    
    GET: Show assignment form with eligible players and events
    POST: Process MVP assignment
    """
    if request.method == 'POST':
        try:
            player_id = request.form.get('player_id', type=int)
            event_id = request.form.get('event_id', type=int)
            
            if not player_id or not event_id:
                flash('Both player and event must be selected', 'error')
                return redirect(url_for('players.assign_mvp'))
            
            # Check rotation logic
            if not can_assign_mvp(current_user.id):
                flash('Cannot assign MVP: Not all players have been MVP yet', 'error')
                return redirect(url_for('players.assign_mvp'))
            
            eligible_players = get_eligible_players(current_user.id)
            if player_id not in [p.id for p in eligible_players]:
                flash('Selected player is not eligible for MVP assignment', 'error')
                return redirect(url_for('players.assign_mvp'))
            
            player = get_user_data_by_id(Player, current_user.id, player_id)
            event = get_user_data_by_id(Event, current_user.id, event_id)
            
            if not player or not event:
                flash('Player or event not found', 'error')
                return redirect(url_for('players.assign_mvp'))
            
            # Allow multiple MVP assignments per event for recurring events
            # No need to check if event already has MVP - we allow multiple assignments
            
            # Remove current MVP status from all players in user's database
            with user_database_context(current_user.id) as session:
                session.query(Player).update({'is_current_mvp': False})
                session.commit()
            
            # Create MVP assignment in user's database
            assignment = create_user_data(MVPAssignment, current_user.id, 
                                        player_id=player_id, event_id=event_id)
            
            # Update player status in user's database
            update_user_data(Player, current_user.id, player_id, 
                           is_current_mvp=True, mvp_count=player.mvp_count + 1)
            
            # Update event status in user's database
            update_user_data(Event, current_user.id, event_id, has_mvp=True)
            
            # Send MVP announcement
            try:
                from telegram_bot import send_mvp_announcement
                success = send_mvp_announcement(event.name, player.name, current_user)
                if success:
                    print(f"MVP announcement sent: {event.name} -> {player.name}")
                else:
                    print(f"Failed to send MVP announcement: {event.name} -> {player.name}")
            except Exception as e:
                print(f"Failed to send MVP announcement: {e}")
                # Don't fail the assignment if notification fails
            
            flash(f'{player.name} assigned as MVP for "{event.name}"', 'success')
            return redirect(url_for('players.list_players'))
            
        except Exception as e:
            print(f"Error assigning MVP: {str(e)}")
            flash('Failed to assign MVP', 'error')
            return redirect(url_for('players.assign_mvp'))
    
    # GET request - show assignment form
    try:
        # Check if we can assign MVP
        can_assign = can_assign_mvp(current_user.id)
        eligible_players = get_eligible_players(current_user.id) if can_assign else []
        
        # Get all events from user's database - allow multiple MVP assignments per event for recurring events
        available_events = query_user_data(Event, current_user.id)
        available_events.sort(key=lambda x: x.event_date, reverse=True)
        
        return render_template(get_template_path('players/assign_mvp.html'),
                             can_assign_mvp=can_assign,
                             eligible_players=eligible_players,
                             available_events=available_events)
    except Exception as e:
        print(f"Error loading MVP assignment form: {str(e)}")
        return render_template(get_template_path('players/assign_mvp.html'),
                             error="Failed to load assignment form")

# API Routes for AJAX operations

@bp.route('/api/list')
@login_required
def api_list_players():
    """API endpoint to get all players as JSON"""
    try:
        players = query_user_data(Player, current_user.id)
        players.sort(key=lambda x: x.name)
        return jsonify({
            'success': True,
            'players': [player.to_dict() for player in players]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/rotation-status')
def api_rotation_status():
    """API endpoint to check MVP rotation status"""
    try:
        can_assign = can_assign_mvp()
        eligible_players = get_eligible_players() if can_assign else []
        
        return jsonify({
            'success': True,
            'can_assign_mvp': can_assign,
            'eligible_players': [player.to_dict() for player in eligible_players]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/mvp-history/<int:player_id>')
def api_mvp_history(player_id):
    """API endpoint to get player's MVP history"""
    try:
        # Get player from user's database
        player = get_user_data_by_id(Player, current_user.id, player_id)
        if not player:
            return jsonify({
                'success': False,
                'error': 'Player not found'
            }), 404
        
        # Get all MVP assignments for this player with event details from user's database
        with user_database_context(current_user.id) as session:
            mvp_assignments = session.query(MVPAssignment, Event).join(
                Event, MVPAssignment.event_id == Event.id
            ).filter(
                MVPAssignment.player_id == player_id
            ).order_by(MVPAssignment.assigned_at.desc()).all()
            
            history = []
            for assignment, event in mvp_assignments:
                history.append({
                    'event_name': event.name,
                    'event_date': event.event_date.isoformat() if event.event_date else None,
                    'assigned_at': assignment.assigned_at.isoformat() if assignment.assigned_at else None,
                    'event_description': event.description
                })
        
        return jsonify({
            'success': True,
            'player_name': player.name,
            'mvp_count': player.mvp_count,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/unassign-mvp/<int:assignment_id>', methods=['POST'])
@login_required
def unassign_mvp(assignment_id):
    """Unassign MVP from an event"""
    try:
        with user_database_context(current_user.id) as session:
            # Get the MVP assignment
            assignment = session.query(MVPAssignment).get(assignment_id)
            if not assignment:
                flash('MVP assignment not found', 'error')
                return redirect(url_for('players.list_players'))
            
            # Get the player and event for logging
            player = session.query(Player).get(assignment.player_id)
            event = session.query(Event).get(assignment.event_id)
            
            if not player or not event:
                flash('Player or event not found', 'error')
                return redirect(url_for('players.list_players'))
            
            # Delete the MVP assignment
            session.delete(assignment)
            
            # Update player's MVP count and remove current MVP status
            player.mvp_count = max(0, player.mvp_count - 1)
            player.is_current_mvp = False
            
            # Update event's MVP assignment status
            event.has_mvp = False
            
            session.commit()
            
            # Send unassign notification
            try:
                from telegram_bot import send_mvp_unassign_announcement
                success = send_mvp_unassign_announcement(event.name, player.name, current_user)
                if success:
                    print(f"MVP unassign announcement sent: {event.name} -> {player.name}")
                else:
                    print(f"Failed to send MVP unassign announcement: {event.name} -> {player.name}")
            except Exception as e:
                print(f"Failed to send MVP unassign announcement: {e}")
                # Don't fail the unassignment if notification fails
            
            flash(f'Successfully unassigned {player.name} as MVP for "{event.name}"', 'success')
            
    except Exception as e:
        print(f"Error unassigning MVP: {str(e)}")
        flash('Failed to unassign MVP', 'error')
    
    return redirect(url_for('players.list_players'))