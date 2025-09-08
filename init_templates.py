#!/usr/bin/env python3
"""
Initialize default event templates for King's Choice Management App

This script creates some common event templates that users can use
to quickly create events without typing them every time.
"""

import sys
import os

# Add the workspace directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import EventTemplate
from database import db

def init_default_templates():
    """Initialize default event templates"""
    
    # Default templates for common events
    default_templates = [
        {
            'name': 'Ежедневное событие',
            'description': 'Стандартное ежедневное событие для всех игроков'
        },
        {
            'name': 'Турнир выходного дня',
            'description': 'Специальный турнир, проводимый по выходным'
        },
        {
            'name': 'Специальное событие',
            'description': 'Особое событие с уникальными правилами и наградами'
        },
        {
            'name': 'Событие альянса',
            'description': 'Событие, в котором участвуют только члены альянсов'
        },
        {
            'name': 'Быстрое событие',
            'description': 'Короткое событие с быстрыми результатами'
        },
        {
            'name': 'Сезонное событие',
            'description': 'Событие, приуроченное к определенному сезону или празднику'
        },
        {
            'name': 'Событие новичков',
            'description': 'Событие специально для новых игроков'
        },
        {
            'name': 'VIP событие',
            'description': 'Эксклюзивное событие для опытных игроков'
        }
    ]
    
    app = create_app()
    
    with app.app_context():
        try:
            # Check if templates already exist
            existing_templates = EventTemplate.query.count()
            if existing_templates > 0:
                print(f"Found {existing_templates} existing templates. Skipping initialization.")
                return
            
            # Create default templates
            created_count = 0
            for template_data in default_templates:
                # Check if template already exists
                existing = EventTemplate.query.filter_by(name=template_data['name']).first()
                if not existing:
                    template = EventTemplate(
                        name=template_data['name'],
                        description=template_data['description']
                    )
                    db.session.add(template)
                    created_count += 1
            
            db.session.commit()
            print(f"Successfully created {created_count} default event templates.")
            
        except Exception as e:
            print(f"Error initializing templates: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("Initializing default event templates...")
    if init_default_templates():
        print("Template initialization completed successfully!")
    else:
        print("Template initialization failed!")
        sys.exit(1)