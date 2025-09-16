"""
Player Routes Module

Handles all player-related operations:
- List all players with MVP status icons
- Add new players
- Edit/rename players
- Delete players
- Assign MVP with rotation logic
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import Player, Event, MVPAssignment
from database import db
from utils.rotation_logic import can_assign_mvp, get_eligible_players

# Create blueprint for player routes
bp = Blueprint('players', __name__, url_prefix='/players')

@bp.route('/')
def list_players():
    """
    Display all players with their MVP status and management options
    
    Shows:
    - List of all players
    - MVP icon for current MVP
    - MVP count for each player
    - Add/Edit/Delete buttons
    """
    try:
        players = Player.query.order_by(Player.name).all()
        
        # Check rotation status for MVP assignments
        can_assign = can_assign_mvp()
        eligible_players = get_eligible_players() if can_assign else []
        
        return render_template('players/list.html', 
                             players=players,
                             can_assign_mvp=can_assign,
                             eligible_players=eligible_players)
    except Exception as e:
        print(f"Error in list_players route: {str(e)}")
        return render_template('players/list.html', 
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
                return render_template('players/add.html')
            
            # Check if player already exists
            existing_player = Player.query.filter_by(name=player_name).first()
            if existing_player:
                flash(f'Player "{player_name}" already exists', 'error')
                return render_template('players/add.html')
            
            # Create new player
            new_player = Player(name=player_name)
            db.session.add(new_player)
            db.session.commit()
            
            flash(f'Player "{player_name}" added successfully', 'success')
            return redirect(url_for('players.list_players'))
            
        except Exception as e:
            print(f"Error adding player: {str(e)}")
            db.session.rollback()
            flash('Failed to add player', 'error')
            return render_template('players/add.html')
    
    return render_template('players/add.html')

@bp.route('/edit/<int:player_id>', methods=['GET', 'POST'])
def edit_player(player_id):
    """
    Edit/rename an existing player
    
    Args:
        player_id: ID of player to edit
    
    GET: Show edit form with current player data
    POST: Process player updates
    """
    player = Player.query.get_or_404(player_id)
    
    if request.method == 'POST':
        try:
            new_name = request.form.get('name', '').strip()
            
            if not new_name:
                flash('Player name is required', 'error')
                return render_template('players/edit.html', player=player)
            
            # Check if new name conflicts with existing player (excluding current)
            existing_player = Player.query.filter(
                Player.name == new_name,
                Player.id != player_id
            ).first()
            
            if existing_player:
                flash(f'Player name "{new_name}" is already taken', 'error')
                return render_template('players/edit.html', player=player)
            
            # Update player
            old_name = player.name
            player.name = new_name
            db.session.commit()
            
            flash(f'Player renamed from "{old_name}" to "{new_name}"', 'success')
            return redirect(url_for('players.list_players'))
            
        except Exception as e:
            print(f"Error editing player: {str(e)}")
            db.session.rollback()
            flash('Failed to update player', 'error')
            return render_template('players/edit.html', player=player)
    
    return render_template('players/edit.html', player=player)

@bp.route('/delete/<int:player_id>', methods=['POST'])
def delete_player(player_id):
    """
    Delete a player from the system
    
    Args:
        player_id: ID of player to delete
    
    This will also delete all MVP assignments for this player
    """
    try:
        player = Player.query.get_or_404(player_id)
        player_name = player.name
        
        # Remove current MVP status if this player is current MVP
        if player.is_current_mvp:
            player.is_current_mvp = False
        
        # Delete player (cascading will handle MVP assignments)
        db.session.delete(player)
        db.session.commit()
        
        flash(f'Player "{player_name}" deleted successfully', 'success')
        
    except Exception as e:
        print(f"Error deleting player: {str(e)}")
        db.session.rollback()
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
        player = Player.query.get_or_404(player_id)
        
        # Toggle exclusion status
        player.is_excluded = not player.is_excluded
        
        # If excluding the current MVP, remove their MVP status
        if player.is_excluded and player.is_current_mvp:
            player.is_current_mvp = False
            flash(f'Игрок "{player.name}" исключен из ротации MVP и снят с поста текущего MVP', 'warning')
        elif player.is_excluded:
            flash(f'Игрок "{player.name}" исключен из ротации MVP', 'info')
        else:
            flash(f'Игрок "{player.name}" включен в ротацию MVP', 'success')
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error toggling exclusion: {str(e)}")
        db.session.rollback()
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
            if not can_assign_mvp():
                flash('Cannot assign MVP: Not all players have been MVP yet', 'error')
                return redirect(url_for('players.assign_mvp'))
            
            eligible_players = get_eligible_players()
            if player_id not in [p.id for p in eligible_players]:
                flash('Selected player is not eligible for MVP assignment', 'error')
                return redirect(url_for('players.assign_mvp'))
            
            player = Player.query.get_or_404(player_id)
            event = Event.query.get_or_404(event_id)
            
            # Allow multiple MVP assignments per event for recurring events
            # No need to check if event already has MVP - we allow multiple assignments
            
            # Remove current MVP status from all players
            Player.query.update({'is_current_mvp': False})
            
            # Create MVP assignment
            assignment = MVPAssignment(player_id=player_id, event_id=event_id)
            db.session.add(assignment)
            
            # Update player status
            player.is_current_mvp = True
            player.mvp_count += 1
            
            # Update event status - mark as having at least one MVP
            event.has_mvp = True
            
            db.session.commit()
            
            # Send Telegram announcement
            try:
                from telegram_bot import send_mvp_announcement
                from flask_login import current_user
                send_mvp_announcement(event.name, player.name, current_user)
                print(f"Telegram MVP announcement sent: {event.name} -> {player.name}")
            except Exception as e:
                print(f"Failed to send Telegram MVP announcement: {e}")
                # Don't fail the assignment if Telegram fails
            
            flash(f'{player.name} assigned as MVP for "{event.name}"', 'success')
            return redirect(url_for('players.list_players'))
            
        except Exception as e:
            print(f"Error assigning MVP: {str(e)}")
            db.session.rollback()
            flash('Failed to assign MVP', 'error')
            return redirect(url_for('players.assign_mvp'))
    
    # GET request - show assignment form
    try:
        # Check if we can assign MVP
        can_assign = can_assign_mvp()
        eligible_players = get_eligible_players() if can_assign else []
        
        # Get all events - allow multiple MVP assignments per event for recurring events
        available_events = Event.query.order_by(Event.event_date.desc()).all()
        
        return render_template('players/assign_mvp.html',
                             can_assign_mvp=can_assign,
                             eligible_players=eligible_players,
                             available_events=available_events)
    except Exception as e:
        print(f"Error loading MVP assignment form: {str(e)}")
        return render_template('players/assign_mvp.html',
                             error="Failed to load assignment form")

# API Routes for AJAX operations

@bp.route('/api/list')
def api_list_players():
    """API endpoint to get all players as JSON"""
    try:
        players = Player.query.order_by(Player.name).all()
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
        player = Player.query.get_or_404(player_id)
        
        # Get all MVP assignments for this player with event details
        mvp_assignments = db.session.query(MVPAssignment, Event).join(
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