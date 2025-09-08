"""
Guide Routes Module

Handles all guide-related routes including:
- Guide listing and viewing
- Guide category management
- Guide creation and editing
- Guide search and filtering
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from models import Guide, GuideCategory
from database import db
from datetime import datetime
import re

# Create blueprint for guide routes
bp = Blueprint('guides', __name__, url_prefix='/guides')

def slugify(text):
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

@bp.route('/')
def list_guides():
    """
    Main guides page - shows all categories and featured guides
    """
    try:
        # Get all active categories with their guides
        categories = GuideCategory.query.filter_by(is_active=True).order_by(GuideCategory.sort_order).all()
        
        # Get recent guides
        recent_guides = Guide.query.filter_by(is_published=True).order_by(Guide.created_at.desc()).limit(6).all()
        
        return render_template('guides/list.html', 
                             categories=categories,
                             recent_guides=recent_guides)
    except Exception as e:
        print(f"Error in list_guides route: {str(e)}")
        return render_template('guides/list.html', 
                             error="Failed to load guides")

@bp.route('/category/<slug>')
def category_guides(slug):
    """
    Show guides for a specific category
    """
    try:
        category = GuideCategory.query.filter_by(slug=slug, is_active=True).first()
        if not category:
            abort(404)
        
        # Get guides for this category
        guides = Guide.query.filter_by(category_id=category.id, is_published=True).order_by(Guide.sort_order, Guide.created_at.desc()).all()
        
        return render_template('guides/category.html', 
                             category=category,
                             guides=guides)
    except Exception as e:
        print(f"Error in category_guides route: {str(e)}")
        abort(404)

@bp.route('/<slug>')
def view_guide(slug):
    """
    View a specific guide
    """
    try:
        guide = Guide.query.filter_by(slug=slug, is_published=True).first()
        if not guide:
            abort(404)
        
        # Increment view count
        guide.increment_view_count()
        
        # Get related guides from the same category
        related_guides = Guide.query.filter(
            Guide.category_id == guide.category_id,
            Guide.id != guide.id,
            Guide.is_published == True
        ).order_by(Guide.created_at.desc()).limit(4).all()
        
        return render_template('guides/view.html', 
                             guide=guide,
                             related_guides=related_guides)
    except Exception as e:
        print(f"Error in view_guide route: {str(e)}")
        abort(404)


@bp.route('/search')
def search_guides():
    """
    Search guides by title and content
    """
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return redirect(url_for('guides.list_guides'))
        
        # Search in title and content
        guides = Guide.query.filter(
            Guide.is_published == True,
            db.or_(
                Guide.title.contains(query),
                Guide.content.contains(query),
                Guide.excerpt.contains(query)
            )
        ).order_by(Guide.created_at.desc()).all()
        
        return render_template('guides/search.html', 
                             query=query,
                             guides=guides)
    except Exception as e:
        print(f"Error in search_guides route: {str(e)}")
        return render_template('guides/search.html', 
                             query=query,
                             guides=[],
                             error="Search failed")

# Admin routes for guide management
@bp.route('/admin')
def admin_guides():
    """
    Admin page for managing guides
    """
    try:
        guides = Guide.query.order_by(Guide.created_at.desc()).all()
        categories = GuideCategory.query.order_by(GuideCategory.sort_order).all()
        
        return render_template('guides/admin/list.html', 
                             guides=guides,
                             categories=categories)
    except Exception as e:
        print(f"Error in admin_guides route: {str(e)}")
        return render_template('guides/admin/list.html', 
                             guides=[],
                             categories=[],
                             error="Failed to load admin page")

@bp.route('/admin/add', methods=['GET', 'POST'])
def add_guide():
    """
    Add a new guide
    """
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            category_id = request.form.get('category_id')
            featured_image = request.form.get('featured_image', '').strip()
            is_published = 'is_published' in request.form
            is_featured = 'is_featured' in request.form
            
            if not title or not content or not category_id:
                flash('Title, content, and category are required', 'error')
                return render_template('guides/admin/add.html', categories=GuideCategory.query.all())
            
            # Create slug from title
            slug = slugify(title)
            
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while Guide.query.filter_by(slug=slug).first():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            guide = Guide(
                title=title,
                slug=slug,
                content=content,
                excerpt=excerpt,
                category_id=int(category_id),
                featured_image=featured_image,
                is_published=is_published,
                is_featured=is_featured
            )
            
            db.session.add(guide)
            db.session.commit()
            
            flash('Guide created successfully!', 'success')
            return redirect(url_for('guides.view_guide', slug=slug))
            
        except Exception as e:
            print(f"Error creating guide: {str(e)}")
            flash('Failed to create guide', 'error')
            return render_template('guides/admin/add.html', categories=GuideCategory.query.all())
    
    categories = GuideCategory.query.order_by(GuideCategory.sort_order).all()
    return render_template('guides/admin/add.html', categories=categories)

@bp.route('/admin/edit/<int:guide_id>', methods=['GET', 'POST'])
def edit_guide(guide_id):
    """
    Edit an existing guide
    """
    guide = Guide.query.get_or_404(guide_id)
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            category_id = request.form.get('category_id')
            featured_image = request.form.get('featured_image', '').strip()
            is_published = 'is_published' in request.form
            is_featured = 'is_featured' in request.form
            
            if not title or not content or not category_id:
                flash('Title, content, and category are required', 'error')
                return render_template('guides/admin/edit.html', guide=guide, categories=GuideCategory.query.all())
            
            # Update guide
            guide.title = title
            guide.content = content
            guide.excerpt = excerpt
            guide.category_id = int(category_id)
            guide.featured_image = featured_image
            guide.is_published = is_published
            guide.is_featured = is_featured
            guide.updated_at = datetime.utcnow()
            
            # Update slug if title changed
            new_slug = slugify(title)
            if new_slug != guide.slug:
                # Ensure new slug is unique
                counter = 1
                original_slug = new_slug
                while Guide.query.filter(Guide.slug == new_slug, Guide.id != guide.id).first():
                    new_slug = f"{original_slug}-{counter}"
                    counter += 1
                guide.slug = new_slug
            
            db.session.commit()
            
            flash('Guide updated successfully!', 'success')
            return redirect(url_for('guides.view_guide', slug=guide.slug))
            
        except Exception as e:
            print(f"Error updating guide: {str(e)}")
            flash('Failed to update guide', 'error')
            return render_template('guides/admin/edit.html', guide=guide, categories=GuideCategory.query.all())
    
    categories = GuideCategory.query.order_by(GuideCategory.sort_order).all()
    return render_template('guides/admin/edit.html', guide=guide, categories=categories)

@bp.route('/admin/delete/<int:guide_id>', methods=['POST'])
def delete_guide(guide_id):
    """
    Delete a guide
    """
    try:
        guide = Guide.query.get_or_404(guide_id)
        db.session.delete(guide)
        db.session.commit()
        flash('Guide deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting guide: {str(e)}")
        flash('Failed to delete guide', 'error')
    
    return redirect(url_for('guides.admin_guides'))

# Category management routes
@bp.route('/admin/categories')
def admin_categories():
    """
    Admin page for managing categories
    """
    try:
        categories = GuideCategory.query.order_by(GuideCategory.sort_order).all()
        return render_template('guides/admin/categories.html', categories=categories)
    except Exception as e:
        print(f"Error in admin_categories route: {str(e)}")
        return render_template('guides/admin/categories.html', categories=[], error="Failed to load categories")

@bp.route('/admin/categories/add', methods=['GET', 'POST'])
def add_category():
    """
    Add a new category
    """
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', 'bi-book').strip()
            sort_order = request.form.get('sort_order', 0)
            
            if not name:
                flash('Category name is required', 'error')
                return render_template('guides/admin/add_category.html')
            
            # Create slug from name
            slug = slugify(name)
            
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while GuideCategory.query.filter_by(slug=slug).first():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            category = GuideCategory(
                name=name,
                slug=slug,
                description=description,
                icon=icon,
                sort_order=int(sort_order) if sort_order else 0
            )
            
            db.session.add(category)
            db.session.commit()
            
            flash('Category created successfully!', 'success')
            return redirect(url_for('guides.admin_categories'))
            
        except Exception as e:
            print(f"Error creating category: {str(e)}")
            flash('Failed to create category', 'error')
            return render_template('guides/admin/add_category.html')
    
    return render_template('guides/admin/add_category.html')

@bp.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    """
    Edit an existing category
    """
    category = GuideCategory.query.get_or_404(category_id)
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            icon = request.form.get('icon', 'bi-book').strip()
            sort_order = request.form.get('sort_order', 0)
            is_active = 'is_active' in request.form
            
            if not name:
                flash('Category name is required', 'error')
                return render_template('guides/admin/edit_category.html', category=category)
            
            # Update category
            category.name = name
            category.description = description
            category.icon = icon
            category.sort_order = int(sort_order) if sort_order else 0
            category.is_active = is_active
            category.updated_at = datetime.utcnow()
            
            # Update slug if name changed
            new_slug = slugify(name)
            if new_slug != category.slug:
                # Ensure new slug is unique
                counter = 1
                original_slug = new_slug
                while GuideCategory.query.filter(GuideCategory.slug == new_slug, GuideCategory.id != category.id).first():
                    new_slug = f"{original_slug}-{counter}"
                    counter += 1
                category.slug = new_slug
            
            db.session.commit()
            
            flash('Category updated successfully!', 'success')
            return redirect(url_for('guides.admin_categories'))
            
        except Exception as e:
            print(f"Error updating category: {str(e)}")
            flash('Failed to update category', 'error')
            return render_template('guides/admin/edit_category.html', category=category)
    
    return render_template('guides/admin/edit_category.html', category=category)

@bp.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    """
    Delete a category
    """
    try:
        category = GuideCategory.query.get_or_404(category_id)
        
        # Check if category has guides
        if category.guides:
            flash('Cannot delete category with existing guides. Please move or delete the guides first.', 'error')
            return redirect(url_for('guides.admin_categories'))
        
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting category: {str(e)}")
        flash('Failed to delete category', 'error')
    
    return redirect(url_for('guides.admin_categories'))