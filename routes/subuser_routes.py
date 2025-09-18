"""
SubUser management routes for King's Choice Management App

Handles creation, listing, editing, and deletion of sub-users (alliance leader helpers).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from database import db
from models import User, SubUser
from auth import get_effective_user_id, is_sub_user, has_sub_user_permission
from functools import wraps

# Create blueprint for sub-user routes
subuser_bp = Blueprint('subuser', __name__)

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin privileges required', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def owner_required(f):
    """Decorator to require ownership of sub-user (admin or parent user)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Login required', 'error')
            return redirect(url_for('auth.login'))
        
        # Admin can manage all sub-users
        if current_user.is_admin:
            return f(*args, **kwargs)
        
        # Regular users can only manage their own sub-users
        if is_sub_user():
            flash('Sub-users cannot manage other sub-users', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@subuser_bp.route('/subusers')
@login_required
@owner_required
def list_subusers():
    """List all sub-users for the current user (or all if admin)"""
    if current_user.is_admin:
        # Admin can see all sub-users
        subusers = SubUser.query.all()
    else:
        # Regular users can only see their own sub-users
        subusers = SubUser.query.filter_by(parent_user_id=current_user.id).all()
    
    return render_template('auth/subusers.html', subusers=subusers)

@subuser_bp.route('/subusers/create', methods=['GET', 'POST'])
@login_required
@owner_required
def create_subuser():
    """Create a new sub-user"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Basic validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('auth/create_subuser.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/create_subuser.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'error')
            return render_template('auth/create_subuser.html')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first() or SubUser.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/create_subuser.html')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first() or SubUser.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('auth/create_subuser.html')
        
        try:
            # Create sub-user
            subuser = SubUser(
                username=username,
                email=email,
                parent_user_id=current_user.id if not current_user.is_admin else int(request.form.get('parent_user_id', current_user.id)),
                is_active=True
            )
            subuser.set_password(password)
            
            # Set permissions based on form data
            permissions = {}
            for key in ['can_view_players', 'can_view_alliances', 'can_view_events', 
                       'can_assign_mvp', 'can_assign_winner', 'can_manage_players', 
                       'can_manage_alliances', 'can_manage_events', 'can_view_dashboard']:
                permissions[key] = key in request.form
            
            subuser.permissions = permissions
            
            db.session.add(subuser)
            db.session.commit()
            
            flash(f'Sub-user "{username}" created successfully!', 'success')
            return redirect(url_for('subuser.list_subusers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating sub-user: {str(e)}', 'error')
    
    # Get all users for admin to select parent
    users = User.query.all() if current_user.is_admin else [current_user]
    
    return render_template('auth/create_subuser.html', users=users)

@subuser_bp.route('/subusers/<int:subuser_id>/edit', methods=['GET', 'POST'])
@login_required
@owner_required
def edit_subuser(subuser_id):
    """Edit a sub-user"""
    subuser = SubUser.query.get_or_404(subuser_id)
    
    # Check ownership
    if not current_user.is_admin and subuser.parent_user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('subuser.list_subusers'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        is_active = 'is_active' in request.form
        
        # Basic validation
        if not username or not email:
            flash('Username and email are required', 'error')
            return render_template('auth/edit_subuser.html', subuser=subuser)
        
        # Check if username already exists (excluding current subuser)
        existing_user = User.query.filter_by(username=username).first()
        existing_subuser = SubUser.query.filter(SubUser.username == username, SubUser.id != subuser_id).first()
        
        if existing_user or existing_subuser:
            flash('Username already exists', 'error')
            return render_template('auth/edit_subuser.html', subuser=subuser)
        
        # Check if email already exists (excluding current subuser)
        existing_user = User.query.filter_by(email=email).first()
        existing_subuser = SubUser.query.filter(SubUser.email == email, SubUser.id != subuser_id).first()
        
        if existing_user or existing_subuser:
            flash('Email already exists', 'error')
            return render_template('auth/edit_subuser.html', subuser=subuser)
        
        try:
            # Update sub-user
            subuser.username = username
            subuser.email = email
            subuser.is_active = is_active
            
            # Update permissions
            permissions = {}
            for key in ['can_view_players', 'can_view_alliances', 'can_view_events', 
                       'can_assign_mvp', 'can_assign_winner', 'can_manage_players', 
                       'can_manage_alliances', 'can_manage_events', 'can_view_dashboard']:
                permissions[key] = key in request.form
            
            subuser.permissions = permissions
            
            # Update parent user if admin
            if current_user.is_admin and 'parent_user_id' in request.form:
                subuser.parent_user_id = int(request.form.get('parent_user_id'))
            
            db.session.commit()
            
            flash(f'Sub-user "{username}" updated successfully!', 'success')
            return redirect(url_for('subuser.list_subusers'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating sub-user: {str(e)}', 'error')
    
    # Get all users for admin to select parent
    users = User.query.all() if current_user.is_admin else [subuser.parent_user]
    
    return render_template('auth/edit_subuser.html', subuser=subuser, users=users)

@subuser_bp.route('/subusers/<int:subuser_id>/delete', methods=['POST'])
@login_required
@owner_required
def delete_subuser(subuser_id):
    """Delete a sub-user"""
    subuser = SubUser.query.get_or_404(subuser_id)
    
    # Check ownership
    if not current_user.is_admin and subuser.parent_user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('subuser.list_subusers'))
    
    try:
        username = subuser.username
        db.session.delete(subuser)
        db.session.commit()
        
        flash(f'Sub-user "{username}" deleted successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting sub-user: {str(e)}', 'error')
    
    return redirect(url_for('subuser.list_subusers'))

@subuser_bp.route('/subusers/<int:subuser_id>/reset_password', methods=['POST'])
@login_required
@owner_required
def reset_subuser_password(subuser_id):
    """Reset a sub-user's password"""
    subuser = SubUser.query.get_or_404(subuser_id)
    
    # Check ownership
    if not current_user.is_admin and subuser.parent_user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('subuser.list_subusers'))
    
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if not new_password or not confirm_password:
        flash('Password fields are required', 'error')
        return redirect(url_for('subuser.edit_subuser', subuser_id=subuser_id))
    
    if new_password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('subuser.edit_subuser', subuser_id=subuser_id))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'error')
        return redirect(url_for('subuser.edit_subuser', subuser_id=subuser_id))
    
    try:
        subuser.set_password(new_password)
        db.session.commit()
        
        flash(f'Password for "{subuser.username}" reset successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error resetting password: {str(e)}', 'error')
    
    return redirect(url_for('subuser.edit_subuser', subuser_id=subuser_id))
