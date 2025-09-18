"""
Event Routes Module

Handles all event-related operations:
- List all events with their MVP and winner assignments
- Add new events
- Edit events
- Delete events
- View event details
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import Event, Player, Alliance, MVPAssignment, WinnerAssignment
from database import db
from database_manager import query_user_data, get_user_data_by_id, create_user_data, update_user_data, delete_user_data, user_database_context
from datetime import datetime

# Create blueprint for event routes
bp = Blueprint('events', __name__, url_prefix='/events')

def get_template_path(template_name):
    """Get template path based on user's template preference"""
    template = session.get('template', 'classic')
    return f'modern/{template_name}' if template == 'modern' else template_name

@bp.route('/')
@login_required
def list_events():
    """
    Display all events with their assignments
    
    Shows:
    - List of all events ordered by date (newest first)
    - MVP player for each event (if assigned)
    - Winning alliance for each event (if assigned)
    - Add/Edit/Delete buttons
    """
    try:
        events = query_user_data(Event, current_user.id)
        events.sort(key=lambda x: x.event_date, reverse=True)
        
        # Get assignment data for each event
        events_data = []
        for event in events:
            # Get all MVP assignments for this event (since events can be reused)
            mvp_assignments = query_user_data(MVPAssignment, current_user.id, event_id=event.id)
            mvp_assignments.sort(key=lambda x: x.assigned_at, reverse=True)
            
            # Get winner assignment for this event
            winner_assignments = query_user_data(WinnerAssignment, current_user.id, event_id=event.id)
            winner_assignment = winner_assignments[0] if winner_assignments else None
            
            # Load related data within session context to avoid detached instance errors
            from database_manager import user_database_context
            with user_database_context(current_user.id) as session:
                # Refresh MVP assignments with related data
                mvp_assignments_with_data = []
                for assignment in mvp_assignments:
                    # Get the assignment with its related player data
                    full_assignment = session.query(MVPAssignment).get(assignment.id)
                    if full_assignment:
                        # Eagerly load the player relationship
                        _ = full_assignment.player
                        mvp_assignments_with_data.append(full_assignment)
                
                # Refresh winner assignment with related data
                winner_assignment_with_data = None
                if winner_assignment:
                    winner_assignment_with_data = session.query(WinnerAssignment).get(winner_assignment.id)
                    if winner_assignment_with_data:
                        # Eagerly load the alliance relationship
                        _ = winner_assignment_with_data.alliance
            
            event_info = {
                'event': event,
                'mvp_assignments': mvp_assignments_with_data,
                'mvp_assignment': mvp_assignments_with_data[0] if mvp_assignments_with_data else None,  # Keep first for backward compatibility
                'winner_assignment': winner_assignment_with_data
            }
            events_data.append(event_info)
        
        return render_template(get_template_path('events/list.html'), events_data=events_data)
        
    except Exception as e:
        print(f"ERROR in list_events route: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template(get_template_path('events/list.html'), 
                             events_data=[],
                             error="Failed to load events")

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_event():
    """
    Add a new event to the system
    
    GET: Show add event form
    POST: Process new event creation
    """
    if request.method == 'POST':
        try:
            event_name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            event_date_str = request.form.get('event_date', '')
            
            if not event_name:
                flash('Event name is required', 'error')
                return render_template(get_template_path('events/add.html'))
            
            # Parse event date
            event_date = datetime.utcnow()  # Default to now
            if event_date_str:
                try:
                    event_date = datetime.fromisoformat(event_date_str.replace('T', ' '))
                except ValueError:
                    flash('Invalid date format', 'error')
                    return render_template(get_template_path('events/add.html'))
            
            # Create new event in user's database
            new_event = create_user_data(Event, current_user.id,
                name=event_name,
                description=description if description else None,
                event_date=event_date
            )
            
            flash(f'Event "{event_name}" added successfully', 'success')
            return redirect(url_for('events.list_events'))
            
        except Exception as e:
            print(f"Error adding event: {str(e)}")
            flash('Failed to add event', 'error')
            return render_template(get_template_path('events/add.html'))
    
    return render_template(get_template_path('events/add.html'))

@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """
    Edit an existing event
    
    Args:
        event_id: ID of event to edit
    
    GET: Show edit form with current event data
    POST: Process event updates
    """
    # Get event from user's database
    event = get_user_data_by_id(Event, current_user.id, event_id)
    if not event:
        flash('Event not found', 'error')
        return redirect(url_for('events.list_events'))
    
    if request.method == 'POST':
        try:
            new_name = request.form.get('name', '').strip()
            new_description = request.form.get('description', '').strip()
            event_date_str = request.form.get('event_date', '')
            
            if not new_name:
                flash('Event name is required', 'error')
                return render_template(get_template_path('events/edit.html'), event=event)
            
            # Update event in user's database
            with user_database_context(current_user.id) as session:
                event_to_update = session.query(Event).filter_by(id=event_id).first()
                if event_to_update:
                    event_to_update.name = new_name
                    event_to_update.description = new_description if new_description else None
                    if event_date_str:
                        try:
                            new_date = datetime.fromisoformat(event_date_str.replace('T', ' '))
                            event_to_update.event_date = new_date
                        except ValueError:
                            pass  # Date was already validated above
                    session.commit()
            
            flash(f'Event "{new_name}" updated successfully', 'success')
            return redirect(url_for('events.list_events'))
            
        except Exception as e:
            print(f"Error editing event: {str(e)}")
            flash('Failed to update event', 'error')
            return render_template(get_template_path('events/edit.html'), event=event)
    
    return render_template(get_template_path('events/edit.html'), event=event)

@bp.route('/delete/<int:event_id>', methods=['POST'])
@login_required
def delete_event(event_id):
    """
    Delete an event from the system
    
    Args:
        event_id: ID of event to delete
    
    This will also delete all MVP and winner assignments for this event
    and update player/alliance counts accordingly
    """
    try:
        event = Event.query.get_or_404(event_id)
        event_name = event.name
        
        # Get assignments before deletion to update counts
        mvp_assignments = MVPAssignment.query.filter_by(event_id=event_id).all()
        winner_assignment = WinnerAssignment.query.filter_by(event_id=event_id).first()
        
        # Update player MVP counts if this event had MVPs
        for mvp_assignment in mvp_assignments:
            player = mvp_assignment.player
            player.mvp_count = max(0, player.mvp_count - 1)
            # Remove current MVP status if this was the current MVP
            if player.is_current_mvp:
                player.is_current_mvp = False
        
        # Update alliance win count if this event had a winner
        if winner_assignment:
            alliance = winner_assignment.alliance
            alliance.win_count = max(0, alliance.win_count - 1)
            # Remove current winner status if this was the current winner
            if alliance.is_current_winner:
                alliance.is_current_winner = False
        
        # Delete event (cascading will handle assignments)
        db.session.delete(event)
        db.session.commit()
        
        flash(f'Event "{event_name}" deleted successfully', 'success')
        
    except Exception as e:
        print(f"Error deleting event: {str(e)}")
        db.session.rollback()
        flash('Failed to delete event', 'error')
    
    return redirect(url_for('events.list_events'))

@bp.route('/view/<int:event_id>')
@login_required
def view_event(event_id):
    """
    View detailed information about a specific event
    
    Args:
        event_id: ID of event to view
    
    Shows:
    - Event details
    - All MVP assignments (since events can be reused)
    - Winner assignment (if any)
    - Event history/timeline
    """
    try:
        # Get event from user's database
        event = get_user_data_by_id(Event, current_user.id, event_id)
        if not event:
            flash('Event not found', 'error')
            return redirect(url_for('events.list_events'))
        
        # Get ALL MVP assignments for this event from user's database
        with user_database_context(current_user.id) as session:
            mvp_assignments = session.query(MVPAssignment).filter_by(event_id=event_id).order_by(MVPAssignment.assigned_at.desc()).all()
            
            # Load player relationships to avoid lazy loading issues
            for assignment in mvp_assignments:
                _ = assignment.player  # Trigger lazy loading within session
            
            # Get winner assignment (still only one per event)
            winner_assignment = session.query(WinnerAssignment).filter_by(event_id=event_id).first()
            
            # Load alliance relationship if winner assignment exists
            if winner_assignment:
                _ = winner_assignment.alliance  # Trigger lazy loading within session
        
        return render_template(get_template_path('events/view.html'),
                             event=event,
                             mvp_assignments=mvp_assignments,
                             winner_assignment=winner_assignment)
        
    except Exception as e:
        print(f"Error viewing event: {str(e)}")
        flash('Failed to load event details', 'error')
        return redirect(url_for('events.list_events'))

# API Routes for AJAX operations

@bp.route('/api/list')
@login_required
def api_list_events():
    """API endpoint to get all events with assignments as JSON"""
    try:
        events = Event.query.order_by(Event.event_date.desc()).all()
        events_data = []
        
        for event in events:
            event_dict = event.to_dict()
            
            # Add ALL MVP assignment info (since events can be reused)
            mvp_assignments = MVPAssignment.query.filter_by(event_id=event.id).order_by(MVPAssignment.assigned_at.desc()).all()
            if mvp_assignments:
                event_dict['mvp_assignments'] = [assignment.to_dict() for assignment in mvp_assignments]
                event_dict['mvp_assignment'] = mvp_assignments[0].to_dict()  # Keep first for backward compatibility
            
            # Add winner assignment info
            winner_assignment = WinnerAssignment.query.filter_by(event_id=event.id).first()
            if winner_assignment:
                event_dict['winner_assignment'] = winner_assignment.to_dict()
            
            events_data.append(event_dict)
        
        return jsonify({
            'success': True,
            'events': events_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/available-for-mvp')
@login_required
def api_available_for_mvp():
    """API endpoint to get events available for MVP assignment"""
    try:
        events = Event.query.filter_by(has_mvp=False).order_by(Event.event_date.desc()).all()
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/available-for-winner')
@login_required
def api_available_for_winner():
    """API endpoint to get events available for winner assignment"""
    try:
        events = Event.query.filter_by(has_winner=False).order_by(Event.event_date.desc()).all()
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500