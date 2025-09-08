"""
Event Routes Module

Handles all event-related operations:
- List all events with their MVP and winner assignments
- Add new events
- Edit events
- Delete events
- View event details
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import Event, Player, Alliance, MVPAssignment, WinnerAssignment, EventTemplate
from database import db
from datetime import datetime

# Create blueprint for event routes
bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
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
        events = Event.query.order_by(Event.event_date.desc()).all()
        
        # Get assignment data for each event
        events_data = []
        for event in events:
            event_info = {
                'event': event,
                'mvp_assignment': MVPAssignment.query.filter_by(event_id=event.id).first(),
                'winner_assignment': WinnerAssignment.query.filter_by(event_id=event.id).first()
            }
            events_data.append(event_info)
        
        return render_template('events/list.html', events_data=events_data)
        
    except Exception as e:
        print(f"Error in list_events route: {str(e)}")
        return render_template('events/list.html', 
                             events_data=[],
                             error="Failed to load events")

@bp.route('/add', methods=['GET', 'POST'])
def add_event():
    """
    Add a new event to the system
    
    GET: Show add event form (optionally with template data)
    POST: Process new event creation
    """
    # Get template data from URL parameters if available
    template_name = request.args.get('template_name', '')
    template_description = request.args.get('template_description', '')
    
    if request.method == 'POST':
        try:
            event_name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            event_date_str = request.form.get('event_date', '')
            
            if not event_name:
                flash('Event name is required', 'error')
                return render_template('events/add.html')
            
            # Parse event date
            event_date = datetime.utcnow()  # Default to now
            if event_date_str:
                try:
                    event_date = datetime.fromisoformat(event_date_str.replace('T', ' '))
                except ValueError:
                    flash('Invalid date format', 'error')
                    return render_template('events/add.html')
            
            # Create new event
            new_event = Event(
                name=event_name,
                description=description if description else None,
                event_date=event_date
            )
            db.session.add(new_event)
            db.session.commit()
            
            flash(f'Event "{event_name}" added successfully', 'success')
            return redirect(url_for('events.list_events'))
            
        except Exception as e:
            print(f"Error adding event: {str(e)}")
            db.session.rollback()
            flash('Failed to add event', 'error')
            return render_template('events/add.html', 
                                 template_name=template_name,
                                 template_description=template_description)
    
    return render_template('events/add.html', 
                         template_name=template_name,
                         template_description=template_description)

@bp.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    """
    Edit an existing event
    
    Args:
        event_id: ID of event to edit
    
    GET: Show edit form with current event data
    POST: Process event updates
    """
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        try:
            new_name = request.form.get('name', '').strip()
            new_description = request.form.get('description', '').strip()
            event_date_str = request.form.get('event_date', '')
            
            if not new_name:
                flash('Event name is required', 'error')
                return render_template('events/edit.html', event=event)
            
            # Parse event date
            if event_date_str:
                try:
                    new_date = datetime.fromisoformat(event_date_str.replace('T', ' '))
                    event.event_date = new_date
                except ValueError:
                    flash('Invalid date format', 'error')
                    return render_template('events/edit.html', event=event)
            
            # Update event
            event.name = new_name
            event.description = new_description if new_description else None
            db.session.commit()
            
            flash(f'Event "{new_name}" updated successfully', 'success')
            return redirect(url_for('events.list_events'))
            
        except Exception as e:
            print(f"Error editing event: {str(e)}")
            db.session.rollback()
            flash('Failed to update event', 'error')
            return render_template('events/edit.html', event=event)
    
    return render_template('events/edit.html', event=event)

@bp.route('/delete/<int:event_id>', methods=['POST'])
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
        mvp_assignment = MVPAssignment.query.filter_by(event_id=event_id).first()
        winner_assignment = WinnerAssignment.query.filter_by(event_id=event_id).first()
        
        # Update player MVP count if this event had an MVP
        if mvp_assignment:
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
def view_event(event_id):
    """
    View detailed information about a specific event
    
    Args:
        event_id: ID of event to view
    
    Shows:
    - Event details
    - MVP assignment (if any)
    - Winner assignment (if any)
    - Event history/timeline
    """
    try:
        event = Event.query.get_or_404(event_id)
        mvp_assignment = MVPAssignment.query.filter_by(event_id=event_id).first()
        winner_assignment = WinnerAssignment.query.filter_by(event_id=event_id).first()
        
        return render_template('events/view.html',
                             event=event,
                             mvp_assignment=mvp_assignment,
                             winner_assignment=winner_assignment)
        
    except Exception as e:
        print(f"Error viewing event: {str(e)}")
        flash('Failed to load event details', 'error')
        return redirect(url_for('events.list_events'))

# API Routes for AJAX operations

@bp.route('/api/list')
def api_list_events():
    """API endpoint to get all events with assignments as JSON"""
    try:
        events = Event.query.order_by(Event.event_date.desc()).all()
        events_data = []
        
        for event in events:
            event_dict = event.to_dict()
            
            # Add MVP assignment info
            mvp_assignment = MVPAssignment.query.filter_by(event_id=event.id).first()
            if mvp_assignment:
                event_dict['mvp_assignment'] = mvp_assignment.to_dict()
            
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
def api_available_for_mvp():
    """API endpoint to get all events for MVP assignment (including those with existing assignments)"""
    try:
        events = Event.query.order_by(Event.event_date.desc()).all()
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
def api_available_for_winner():
    """API endpoint to get all events for winner assignment (including those with existing assignments)"""
    try:
        events = Event.query.order_by(Event.event_date.desc()).all()
        return jsonify({
            'success': True,
            'events': [event.to_dict() for event in events]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Event Template Management Routes

@bp.route('/templates')
def list_templates():
    """Display all event templates"""
    try:
        templates = EventTemplate.query.filter_by(is_active=True).order_by(EventTemplate.usage_count.desc(), EventTemplate.name).all()
        return render_template('events/templates.html', templates=templates)
    except Exception as e:
        print(f"Error loading templates: {str(e)}")
        return render_template('events/templates.html', templates=[], error="Failed to load templates")

@bp.route('/templates/add', methods=['GET', 'POST'])
def add_template():
    """Add a new event template"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Template name is required', 'error')
                return render_template('events/add_template.html')
            
            # Check if template already exists
            existing_template = EventTemplate.query.filter_by(name=name).first()
            if existing_template:
                flash(f'Template "{name}" already exists', 'error')
                return render_template('events/add_template.html')
            
            # Create new template
            new_template = EventTemplate(
                name=name,
                description=description if description else None
            )
            db.session.add(new_template)
            db.session.commit()
            
            flash(f'Template "{name}" added successfully', 'success')
            return redirect(url_for('events.list_templates'))
            
        except Exception as e:
            print(f"Error adding template: {str(e)}")
            db.session.rollback()
            flash('Failed to add template', 'error')
            return render_template('events/add_template.html')
    
    return render_template('events/add_template.html')

@bp.route('/templates/delete/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    """Delete an event template"""
    try:
        template = EventTemplate.query.get_or_404(template_id)
        template_name = template.name
        
        # Soft delete by setting is_active to False
        template.is_active = False
        db.session.commit()
        
        flash(f'Template "{template_name}" deleted successfully', 'success')
        
    except Exception as e:
        print(f"Error deleting template: {str(e)}")
        db.session.rollback()
        flash('Failed to delete template', 'error')
    
    return redirect(url_for('events.list_templates'))

@bp.route('/templates/use/<int:template_id>')
def use_template(template_id):
    """Use a template to create a new event"""
    try:
        template = EventTemplate.query.get_or_404(template_id)
        
        # Increment usage count
        template.usage_count += 1
        db.session.commit()
        
        # Redirect to add event page with template data
        return redirect(url_for('events.add_event', 
                              template_name=template.name,
                              template_description=template.description))
        
    except Exception as e:
        print(f"Error using template: {str(e)}")
        flash('Failed to use template', 'error')
        return redirect(url_for('events.list_templates'))

# API Routes for Event Templates

@bp.route('/api/templates')
def api_list_templates():
    """API endpoint to get all active event templates as JSON"""
    try:
        templates = EventTemplate.query.filter_by(is_active=True).order_by(EventTemplate.usage_count.desc(), EventTemplate.name).all()
        return jsonify({
            'success': True,
            'templates': [template.to_dict() for template in templates]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500