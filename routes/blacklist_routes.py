"""
Blacklist Routes Module

Handles blacklist management for alliances and players.
Allows adding, viewing, and removing blacklisted entries.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_babel import gettext as _
from flask_login import login_required, current_user
from models import Blacklist
from database import db
from database_manager import query_user_data, get_user_data_by_id, create_user_data, update_user_data, delete_user_data

# Create blueprint for blacklist routes
bp = Blueprint('blacklist', __name__, url_prefix='/blacklist')

def get_template_path(template_name):
    """Get template path based on user's template preference"""
    template = session.get('template', 'classic')
    return f'modern/{template_name}' if template == 'modern' else template_name

@bp.route('/')
@login_required
def list_blacklist():
    """
    List all blacklisted entries
    
    Shows both alliance and player blacklists in a single interface
    """
    try:
        # Get all blacklist entries from user's database ordered by creation date
        blacklist_entries = query_user_data(Blacklist, current_user.id)
        blacklist_entries.sort(key=lambda x: x.created_at, reverse=True)
        
        # Separate into alliances and players for display
        alliance_entries = [entry for entry in blacklist_entries if entry.alliance_name and not entry.player_name]
        player_entries = [entry for entry in blacklist_entries if entry.player_name]
        
        return render_template(get_template_path('blacklist/list.html'), 
                             alliance_entries=alliance_entries,
                             player_entries=player_entries,
                             total_entries=len(blacklist_entries))
    except Exception as e:
        print(f"Error in blacklist list route: {str(e)}")
        flash(_('Failed to load blacklist data'), 'error')
        return render_template(get_template_path('blacklist/list.html'), 
                             alliance_entries=[], 
                             player_entries=[],
                             total_entries=0)

@bp.route('/add', methods=['GET', 'POST'])
def add_entry():
    """
    Add new blacklist entry
    
    GET: Show form to add new entry
    POST: Process form submission and add entry
    """
    if request.method == 'POST':
        try:
            alliance_name = request.form.get('alliance_name', '').strip()
            player_name = request.form.get('player_name', '').strip()
            
            # Validate input
            if not alliance_name and not player_name:
                flash(_('Either alliance name or player name is required'), 'error')
                return render_template(get_template_path('blacklist/add.html'))
            
            # Check for duplicates in user's database
            existing_entries = query_user_data(Blacklist, current_user.id,
                alliance_name=alliance_name if alliance_name else None,
                player_name=player_name if player_name else None
            )
            
            if existing_entries:
                flash(_('This entry already exists in the blacklist'), 'error')
                return render_template(get_template_path('blacklist/add.html'))
            
            # Create new blacklist entry in user's database
            new_entry = create_user_data(Blacklist, current_user.id,
                alliance_name=alliance_name if alliance_name else None,
                player_name=player_name if player_name else None
            )
            
            flash(_('Blacklist entry added successfully!'), 'success')
            return redirect(url_for('blacklist.list_blacklist'))
            
        except Exception as e:
            print(f"Error adding blacklist entry: {str(e)}")
            flash(_('Failed to add blacklist entry'), 'error')
            return render_template(get_template_path('blacklist/add.html'))
    
    return render_template(get_template_path('blacklist/add.html'))

@bp.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit_entry(entry_id):
    """
    Edit existing blacklist entry
    
    GET: Show form to edit entry
    POST: Process form submission and update entry
    """
    entry = Blacklist.query.get_or_404(entry_id)
    
    if request.method == 'POST':
        try:
            alliance_name = request.form.get('alliance_name', '').strip()
            player_name = request.form.get('player_name', '').strip()
            
            # Validate input
            if not alliance_name and not player_name:
                flash(_('Either alliance name or player name is required'), 'error')
                return render_template(get_template_path('blacklist/edit.html'), entry=entry)
            
            # Check for duplicates (excluding current entry)
            existing_entry = Blacklist.query.filter(
                Blacklist.id != entry_id,
                Blacklist.alliance_name == (alliance_name if alliance_name else None),
                Blacklist.player_name == (player_name if player_name else None)
            ).first()
            
            if existing_entry:
                flash(_('This entry already exists in the blacklist'), 'error')
                return render_template(get_template_path('blacklist/edit.html'), entry=entry)
            
            # Update entry
            entry.alliance_name = alliance_name if alliance_name else None
            entry.player_name = player_name if player_name else None
            
            db.session.commit()
            
            flash(_('Blacklist entry updated successfully!'), 'success')
            return redirect(url_for('blacklist.list_blacklist'))
            
        except Exception as e:
            print(f"Error updating blacklist entry: {str(e)}")
            db.session.rollback()
            flash(_('Failed to update blacklist entry'), 'error')
            return render_template(get_template_path('blacklist/edit.html'), entry=entry)
    
    return render_template(get_template_path('blacklist/edit.html'), entry=entry)

@bp.route('/delete/<int:entry_id>', methods=['POST'])
def delete_entry(entry_id):
    """
    Delete blacklist entry
    
    POST: Remove entry from blacklist
    """
    try:
        entry = Blacklist.query.get_or_404(entry_id)
        
        db.session.delete(entry)
        db.session.commit()
        
        flash(_('Blacklist entry deleted successfully!'), 'success')
        
    except Exception as e:
        print(f"Error deleting blacklist entry: {str(e)}")
        db.session.rollback()
        flash(_('Failed to delete blacklist entry'), 'error')
    
    return redirect(url_for('blacklist.list_blacklist'))

@bp.route('/api/entries')
def api_entries():
    """
    API endpoint to get all blacklist entries in JSON format
    """
    try:
        entries = Blacklist.query.order_by(Blacklist.created_at.desc()).all()
        return jsonify({
            'success': True,
            'entries': [entry.to_dict() for entry in entries]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500