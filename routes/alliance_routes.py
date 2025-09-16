"""
Alliance Routes Module

Handles all alliance-related operations:
- List all alliances with winner status icons
- Add new alliances
- Edit/rename alliances
- Delete alliances
- Assign winners with rotation logic
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import Alliance, Event, WinnerAssignment
from database import db
from utils.rotation_logic import can_assign_winner, get_eligible_alliances

# Create blueprint for alliance routes
bp = Blueprint('alliances', __name__, url_prefix='/alliances')

@bp.route('/')
def list_alliances():
    """
    Display all alliances with their winner status and management options
    
    Shows:
    - List of all alliances
    - Winner icon for current winning alliance
    - Win count for each alliance
    - Add/Edit/Delete buttons
    """
    try:
        alliances = Alliance.query.order_by(Alliance.name).all()
        
        # Check rotation status for winner assignments
        can_assign = can_assign_winner()
        eligible_alliances = get_eligible_alliances() if can_assign else []
        
        return render_template('alliances/list.html', 
                             alliances=alliances,
                             can_assign_winner=can_assign,
                             eligible_alliances=eligible_alliances)
    except Exception as e:
        print(f"Error in list_alliances route: {str(e)}")
        return render_template('alliances/list.html', 
                             alliances=[],
                             error="Failed to load alliances")

@bp.route('/add', methods=['GET', 'POST'])
def add_alliance():
    """
    Add a new alliance to the system
    
    GET: Show add alliance form
    POST: Process new alliance creation
    """
    if request.method == 'POST':
        try:
            alliance_name = request.form.get('name', '').strip()
            
            if not alliance_name:
                flash('Alliance name is required', 'error')
                return render_template('alliances/add.html')
            
            # Check if alliance already exists
            existing_alliance = Alliance.query.filter_by(name=alliance_name).first()
            if existing_alliance:
                flash(f'Alliance "{alliance_name}" already exists', 'error')
                return render_template('alliances/add.html')
            
            # Create new alliance
            new_alliance = Alliance(name=alliance_name)
            db.session.add(new_alliance)
            db.session.commit()
            
            flash(f'Alliance "{alliance_name}" added successfully', 'success')
            return redirect(url_for('alliances.list_alliances'))
            
        except Exception as e:
            print(f"Error adding alliance: {str(e)}")
            db.session.rollback()
            flash('Failed to add alliance', 'error')
            return render_template('alliances/add.html')
    
    return render_template('alliances/add.html')

@bp.route('/edit/<int:alliance_id>', methods=['GET', 'POST'])
def edit_alliance(alliance_id):
    """
    Edit/rename an existing alliance
    
    Args:
        alliance_id: ID of alliance to edit
    
    GET: Show edit form with current alliance data
    POST: Process alliance updates
    """
    alliance = Alliance.query.get_or_404(alliance_id)
    
    if request.method == 'POST':
        try:
            new_name = request.form.get('name', '').strip()
            
            if not new_name:
                flash('Alliance name is required', 'error')
                return render_template('alliances/edit.html', alliance=alliance)
            
            # Check if new name conflicts with existing alliance (excluding current)
            existing_alliance = Alliance.query.filter(
                Alliance.name == new_name,
                Alliance.id != alliance_id
            ).first()
            
            if existing_alliance:
                flash(f'Alliance name "{new_name}" is already taken', 'error')
                return render_template('alliances/edit.html', alliance=alliance)
            
            # Update alliance
            old_name = alliance.name
            alliance.name = new_name
            db.session.commit()
            
            flash(f'Alliance renamed from "{old_name}" to "{new_name}"', 'success')
            return redirect(url_for('alliances.list_alliances'))
            
        except Exception as e:
            print(f"Error editing alliance: {str(e)}")
            db.session.rollback()
            flash('Failed to update alliance', 'error')
            return render_template('alliances/edit.html', alliance=alliance)
    
    return render_template('alliances/edit.html', alliance=alliance)

@bp.route('/delete/<int:alliance_id>', methods=['POST'])
def delete_alliance(alliance_id):
    """
    Delete an alliance from the system
    
    Args:
        alliance_id: ID of alliance to delete
    
    This will also delete all winner assignments for this alliance
    """
    try:
        alliance = Alliance.query.get_or_404(alliance_id)
        alliance_name = alliance.name
        
        # Remove current winner status if this alliance is current winner
        if alliance.is_current_winner:
            alliance.is_current_winner = False
        
        # Delete alliance (cascading will handle winner assignments)
        db.session.delete(alliance)
        db.session.commit()
        
        flash(f'Alliance "{alliance_name}" deleted successfully', 'success')
        
    except Exception as e:
        print(f"Error deleting alliance: {str(e)}")
        db.session.rollback()
        flash('Failed to delete alliance', 'error')
    
    return redirect(url_for('alliances.list_alliances'))

@bp.route('/assign-winner', methods=['GET', 'POST'])
def assign_winner():
    """
    Assign winning alliance for an event
    
    Implements rotation logic: can only assign winner when all alliances have won
    
    GET: Show assignment form with eligible alliances and events
    POST: Process winner assignment
    """
    if request.method == 'POST':
        try:
            alliance_id = request.form.get('alliance_id', type=int)
            event_id = request.form.get('event_id', type=int)
            
            if not alliance_id or not event_id:
                flash('Both alliance and event must be selected', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            # Check rotation logic
            if not can_assign_winner():
                flash('Cannot assign winner: Not all alliances have won yet', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            eligible_alliances = get_eligible_alliances()
            if alliance_id not in [a.id for a in eligible_alliances]:
                flash('Selected alliance is not eligible for winner assignment', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            alliance = Alliance.query.get_or_404(alliance_id)
            event = Event.query.get_or_404(event_id)
            
            # Check if event already has winner
            existing_assignment = WinnerAssignment.query.filter_by(event_id=event_id).first()
            if existing_assignment:
                flash(f'Event "{event.name}" already has a winning alliance assigned', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            # Remove current winner status from all alliances
            Alliance.query.update({'is_current_winner': False})
            
            # Create winner assignment
            assignment = WinnerAssignment(alliance_id=alliance_id, event_id=event_id)
            db.session.add(assignment)
            
            # Update alliance status
            alliance.is_current_winner = True
            alliance.win_count += 1
            
            # Update event status
            event.has_winner = True
            
            db.session.commit()
            
            # Send Telegram announcement
            try:
                from telegram_bot import send_winner_announcement
                from flask_login import current_user
                send_winner_announcement(event.name, alliance.name, current_user)
                print(f"Telegram winner announcement sent: {event.name} -> {alliance.name}")
            except Exception as e:
                print(f"Failed to send Telegram winner announcement: {e}")
                # Don't fail the assignment if Telegram fails
            
            flash(f'{alliance.name} assigned as winner for "{event.name}"', 'success')
            return redirect(url_for('alliances.list_alliances'))
            
        except Exception as e:
            print(f"Error assigning winner: {str(e)}")
            db.session.rollback()
            flash('Failed to assign winner', 'error')
            return redirect(url_for('alliances.assign_winner'))
    
    # GET request - show assignment form
    try:
        # Check if we can assign winner
        can_assign = can_assign_winner()
        eligible_alliances = get_eligible_alliances() if can_assign else []
        
        # Get events that don't have winner assigned yet
        available_events = Event.query.filter_by(has_winner=False).order_by(Event.event_date.desc()).all()
        
        return render_template('alliances/assign_winner.html',
                             can_assign_winner=can_assign,
                             eligible_alliances=eligible_alliances,
                             available_events=available_events)
    except Exception as e:
        print(f"Error loading winner assignment form: {str(e)}")
        return render_template('alliances/assign_winner.html',
                             error="Failed to load assignment form")

# API Routes for AJAX operations

@bp.route('/api/list')
def api_list_alliances():
    """API endpoint to get all alliances as JSON"""
    try:
        alliances = Alliance.query.order_by(Alliance.name).all()
        return jsonify({
            'success': True,
            'alliances': [alliance.to_dict() for alliance in alliances]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/rotation-status')
def api_rotation_status():
    """API endpoint to check winner rotation status"""
    try:
        can_assign = can_assign_winner()
        eligible_alliances = get_eligible_alliances() if can_assign else []
        
        return jsonify({
            'success': True,
            'can_assign_winner': can_assign,
            'eligible_alliances': [alliance.to_dict() for alliance in eligible_alliances]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500