"""
Blacklist Routes Module

Handles blacklist management for alliances and players.
Allows adding, viewing, and removing blacklisted entries.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_babel import gettext as _
from models import Blacklist
from database import db

# Create blueprint for blacklist routes
bp = Blueprint('blacklist', __name__, url_prefix='/blacklist')

@bp.route('/')
def list_blacklist():
    """
    List all blacklisted entries
    
    Shows both alliance and player blacklists in a single interface
    """
    try:
        # Get all blacklist entries ordered by creation date
        blacklist_entries = Blacklist.query.order_by(Blacklist.created_at.desc()).all()
        
        # Separate into alliances and players for display
        alliance_entries = [entry for entry in blacklist_entries if entry.alliance_name and not entry.player_name]
        player_entries = [entry for entry in blacklist_entries if entry.player_name]
        
        return render_template('blacklist/list.html', 
                             alliance_entries=alliance_entries,
                             player_entries=player_entries,
                             total_entries=len(blacklist_entries))
    except Exception as e:
        print(f"Error in blacklist list route: {str(e)}")
        flash(_('Failed to load blacklist data'), 'error')
        return render_template('blacklist/list.html', 
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
                return render_template('blacklist/add.html')
            
            # Check for duplicates
            existing_entry = Blacklist.query.filter_by(
                alliance_name=alliance_name if alliance_name else None,
                player_name=player_name if player_name else None
            ).first()
            
            if existing_entry:
                flash(_('This entry already exists in the blacklist'), 'error')
                return render_template('blacklist/add.html')
            
            # Create new blacklist entry
            new_entry = Blacklist(
                alliance_name=alliance_name if alliance_name else None,
                player_name=player_name if player_name else None
            )
            
            db.session.add(new_entry)
            db.session.commit()
            
            flash(_('Blacklist entry added successfully!'), 'success')
            return redirect(url_for('blacklist.list_blacklist'))
            
        except Exception as e:
            print(f"Error adding blacklist entry: {str(e)}")
            db.session.rollback()
            flash(_('Failed to add blacklist entry'), 'error')
            return render_template('blacklist/add.html')
    
    return render_template('blacklist/add.html')

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
                return render_template('blacklist/edit.html', entry=entry)
            
            # Check for duplicates (excluding current entry)
            existing_entry = Blacklist.query.filter(
                Blacklist.id != entry_id,
                Blacklist.alliance_name == (alliance_name if alliance_name else None),
                Blacklist.player_name == (player_name if player_name else None)
            ).first()
            
            if existing_entry:
                flash(_('This entry already exists in the blacklist'), 'error')
                return render_template('blacklist/edit.html', entry=entry)
            
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
            return render_template('blacklist/edit.html', entry=entry)
    
    return render_template('blacklist/edit.html', entry=entry)

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