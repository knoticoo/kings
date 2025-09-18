"""
Feedback Routes Module

Handles user feedback submission and admin feedback management.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import Feedback, User
from database import db
from datetime import datetime

# Create blueprint for feedback routes
bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@bp.route('/submit', methods=['POST'])
@login_required
def submit_feedback():
    """Submit user feedback"""
    try:
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        category = request.form.get('category', 'suggestion')
        
        if not title or not message:
            flash('Please fill in all required fields', 'error')
            return redirect(request.referrer or url_for('main.dashboard'))
        
        # Create feedback entry
        feedback = Feedback(
            user_id=current_user.id,
            title=title,
            message=message,
            category=category,
            status='pending'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback! We\'ll review it and get back to you if needed.', 'success')
        return redirect(request.referrer or url_for('main.dashboard'))
        
    except Exception as e:
        print(f"Error submitting feedback: {str(e)}")
        flash('Failed to submit feedback. Please try again.', 'error')
        return redirect(request.referrer or url_for('main.dashboard'))

@bp.route('/admin')
@login_required
def admin_feedback():
    """Admin page to view and manage all feedback"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get all feedback with user information
        feedback_list = db.session.query(Feedback, User).join(
            User, Feedback.user_id == User.id
        ).order_by(Feedback.created_at.desc()).all()
        
        # Get feedback statistics
        total_feedback = Feedback.query.count()
        pending_feedback = Feedback.query.filter_by(status='pending').count()
        reviewed_feedback = Feedback.query.filter_by(status='reviewed').count()
        implemented_feedback = Feedback.query.filter_by(status='implemented').count()
        
        stats = {
            'total': total_feedback,
            'pending': pending_feedback,
            'reviewed': reviewed_feedback,
            'implemented': implemented_feedback
        }
        
        return render_template('admin/feedback.html', 
                             feedback_list=feedback_list,
                             stats=stats)
        
    except Exception as e:
        print(f"Error loading admin feedback page: {str(e)}")
        flash('Failed to load feedback data', 'error')
        return redirect(url_for('main.dashboard'))

@bp.route('/admin/<int:feedback_id>/update', methods=['POST'])
@login_required
def update_feedback_status(feedback_id):
    """Update feedback status and add admin notes"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        status = request.form.get('status')
        admin_notes = request.form.get('admin_notes', '').strip()
        
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({'success': False, 'message': 'Feedback not found'})
        
        # Update feedback
        feedback.status = status
        feedback.admin_notes = admin_notes
        feedback.reviewed_at = datetime.utcnow()
        feedback.reviewed_by = current_user.id
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feedback updated successfully'})
        
    except Exception as e:
        print(f"Error updating feedback: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to update feedback'})

@bp.route('/admin/<int:feedback_id>/delete', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    """Delete feedback (admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({'success': False, 'message': 'Feedback not found'})
        
        db.session.delete(feedback)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Feedback deleted successfully'})
        
    except Exception as e:
        print(f"Error deleting feedback: {str(e)}")
        return jsonify({'success': False, 'message': 'Failed to delete feedback'})

@bp.route('/my-feedback')
@login_required
def my_feedback():
    """View user's own feedback submissions"""
    try:
        # Get user's feedback
        feedback_list = Feedback.query.filter_by(user_id=current_user.id).order_by(
            Feedback.created_at.desc()
        ).all()
        
        return render_template('feedback/my_feedback.html', feedback_list=feedback_list)
        
    except Exception as e:
        print(f"Error loading user feedback: {str(e)}")
        flash('Failed to load your feedback', 'error')
        return redirect(url_for('main.dashboard'))
