"""
Alliance Routes Module

Handles all alliance-related operations:
- List all alliances with winner status icons
- Add new alliances
- Edit/rename alliances
- Delete alliances
- Assign winners with rotation logic
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Alliance, Event, WinnerAssignment
from database import db
from database_manager import query_user_data, get_user_data_by_id, create_user_data, update_user_data, delete_user_data, user_database_context
from utils.rotation_logic import can_assign_winner, get_eligible_alliances

# Create blueprint for alliance routes
bp = Blueprint('alliances', __name__, url_prefix='/alliances')

def get_template_path(template_name):
    """Get template path based on user's template preference"""
    template = session.get('template', 'classic')
    return f'modern/{template_name}' if template == 'modern' else template_name

@bp.route('/')
@login_required
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
        alliances = query_user_data(Alliance, current_user.id)
        alliances.sort(key=lambda x: x.name)
        
        # Check rotation status for winner assignments
        can_assign = can_assign_winner(current_user.id)
        eligible_alliances = get_eligible_alliances(current_user.id) if can_assign else []
        
        return render_template(get_template_path('alliances/list.html'), 
                             alliances=alliances,
                             can_assign_winner=can_assign,
                             eligible_alliances=eligible_alliances)
    except Exception as e:
        print(f"Error in list_alliances route: {str(e)}")
        return render_template(get_template_path('alliances/list.html'), 
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
                return render_template(get_template_path('alliances/add.html'))
            
            # Check if alliance already exists for this user
            existing_alliance = query_user_data(Alliance, current_user.id, name=alliance_name)
            if existing_alliance:
                flash(f'Alliance "{alliance_name}" already exists', 'error')
                return render_template(get_template_path('alliances/add.html'))
            
            # Create new alliance in user's database
            new_alliance = create_user_data(Alliance, current_user.id, name=alliance_name)
            
            flash(f'Alliance "{alliance_name}" added successfully', 'success')
            return redirect(url_for('alliances.list_alliances'))
            
        except Exception as e:
            print(f"Error adding alliance: {str(e)}")
            flash('Failed to add alliance', 'error')
            return render_template(get_template_path('alliances/add.html'))
    
    return render_template(get_template_path('alliances/add.html'))

@bp.route('/edit/<int:alliance_id>', methods=['GET', 'POST'])
def edit_alliance(alliance_id):
    """
    Edit/rename an existing alliance
    
    Args:
        alliance_id: ID of alliance to edit
    
    GET: Show edit form with current alliance data
    POST: Process alliance updates
    """
    alliance = get_user_data_by_id(Alliance, current_user.id, alliance_id)
    if not alliance:
        flash('Alliance not found', 'error')
        return redirect(url_for('alliances.list_alliances'))
    
    if request.method == 'POST':
        try:
            new_name = request.form.get('name', '').strip()
            
            if not new_name:
                flash('Alliance name is required', 'error')
                return render_template(get_template_path('alliances/edit.html'), alliance=alliance)
            
            # Check if new name conflicts with existing alliance (excluding current)
            existing_alliances = query_user_data(Alliance, current_user.id, name=new_name)
            existing_alliance = None
            for a in existing_alliances:
                if a.id != alliance_id:
                    existing_alliance = a
                    break
            
            if existing_alliance:
                flash(f'Alliance name "{new_name}" is already taken', 'error')
                return render_template(get_template_path('alliances/edit.html'), alliance=alliance)
            
            # Update alliance in user's database
            old_name = alliance.name
            update_user_data(Alliance, current_user.id, alliance_id, name=new_name)
            
            flash(f'Alliance renamed from "{old_name}" to "{new_name}"', 'success')
            return redirect(url_for('alliances.list_alliances'))
            
        except Exception as e:
            print(f"Error editing alliance: {str(e)}")
            flash('Failed to update alliance', 'error')
            return render_template(get_template_path('alliances/edit.html'), alliance=alliance)
    
    return render_template(get_template_path('alliances/edit.html'), alliance=alliance)

@bp.route('/delete/<int:alliance_id>', methods=['POST'])
def delete_alliance(alliance_id):
    """
    Delete an alliance from the system
    
    Args:
        alliance_id: ID of alliance to delete
    
    This will also delete all winner assignments for this alliance
    """
    try:
        alliance = get_user_data_by_id(Alliance, current_user.id, alliance_id)
        if not alliance:
            flash('Alliance not found', 'error')
            return redirect(url_for('alliances.list_alliances'))
        alliance_name = alliance.name
        
        # Remove current winner status if this alliance is current winner
        if alliance.is_current_winner:
            update_user_data(Alliance, current_user.id, alliance_id, is_current_winner=False)
        
        # Delete alliance from user's database
        success = delete_user_data(Alliance, current_user.id, alliance_id)
        
        if success:
            flash(f'Alliance "{alliance_name}" deleted successfully', 'success')
        else:
            flash('Failed to delete alliance', 'error')
        
    except Exception as e:
        print(f"Error deleting alliance: {str(e)}")
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
            if not can_assign_winner(current_user.id):
                flash('Cannot assign winner: Not all alliances have won yet', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            eligible_alliances = get_eligible_alliances(current_user.id)
            if alliance_id not in [a.id for a in eligible_alliances]:
                flash('Selected alliance is not eligible for winner assignment', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            alliance = get_user_data_by_id(Alliance, current_user.id, alliance_id)
            event = get_user_data_by_id(Event, current_user.id, event_id)
            if not alliance or not event:
                flash('Alliance or event not found', 'error')
                return redirect(url_for('alliances.assign_winner'))
            
            # Allow multiple winner assignments per event for recurring events
            # No need to check if event already has winner - we allow multiple assignments
            
            # Remove current winner status from all alliances for this user
            with user_database_context(current_user.id) as session:
                session.query(Alliance).update({'is_current_winner': False})
                session.commit()
            
            # Create winner assignment in user's database
            assignment = create_user_data(WinnerAssignment, current_user.id, 
                                        alliance_id=alliance_id, event_id=event_id)
            
            # Update alliance status in user's database
            update_user_data(Alliance, current_user.id, alliance_id, 
                           is_current_winner=True, win_count=alliance.win_count + 1)
            
            # Update event status in user's database
            update_user_data(Event, current_user.id, event_id, has_winner=True)
            
            # Send winner announcement
            try:
                from telegram_bot import send_winner_announcement
                success = send_winner_announcement(event.name, alliance.name, current_user)
                if success:
                    print(f"Winner announcement sent: {event.name} -> {alliance.name}")
                else:
                    print(f"Failed to send winner announcement: {event.name} -> {alliance.name}")
            except Exception as e:
                print(f"Failed to send winner announcement: {e}")
                # Don't fail the assignment if notification fails
            
            flash(f'{alliance.name} assigned as winner for "{event.name}"', 'success')
            return redirect(url_for('alliances.list_alliances'))
            
        except Exception as e:
            print(f"Error assigning winner: {str(e)}")
            flash('Failed to assign winner', 'error')
            return redirect(url_for('alliances.assign_winner'))
    
    # GET request - show assignment form
    try:
        # Check if we can assign winner
        can_assign = can_assign_winner(current_user.id)
        eligible_alliances = get_eligible_alliances(current_user.id) if can_assign else []
        
        # Get events that don't have winner assigned yet for this user
        user_events = query_user_data(Event, current_user.id)
        available_events = [e for e in user_events if not e.has_winner]
        available_events.sort(key=lambda x: x.event_date, reverse=True)
        
        return render_template(get_template_path('alliances/assign_winner.html'),
                             can_assign_winner=can_assign,
                             eligible_alliances=eligible_alliances,
                             available_events=available_events)
    except Exception as e:
        print(f"Error loading winner assignment form: {str(e)}")
        return render_template(get_template_path('alliances/assign_winner.html'),
                             error="Failed to load assignment form")

# API Routes for AJAX operations

@bp.route('/api/list')
@login_required
def api_list_alliances():
    """API endpoint to get all alliances as JSON"""
    try:
        alliances = query_user_data(Alliance, current_user.id)
        alliances.sort(key=lambda x: x.name)
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
        can_assign = can_assign_winner(current_user.id)
        eligible_alliances = get_eligible_alliances(current_user.id) if can_assign else []
        
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