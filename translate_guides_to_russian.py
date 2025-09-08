#!/usr/bin/env python3
"""
Script to translate guide categories and content to Russian
"""

from app import app, create_tables
from models import GuideCategory, Guide
from database import db

def translate_to_russian():
    """Translate guide categories and content to Russian"""
    
    with app.app_context():
        # Create tables if they don't exist
        create_tables()
        
        # Russian translations for categories
        category_translations = {
            'knights': {
                'name': 'Рыцари',
                'description': 'Подробные руководства по всем типам рыцарей, включая списки уровней, сборки и стратегии.'
            },
            'events': {
                'name': 'События',
                'description': 'Руководства и стратегии по событиям для Арены Альянса, Сумеречного Замка и других игровых событий.'
            },
            'alliance': {
                'name': 'Альянс',
                'description': 'Управление альянсом, стратегии и руководства по координации.'
            },
            'resources': {
                'name': 'Ресурсы',
                'description': 'Управление ресурсами, руководства по фарму и советы по оптимизации.'
            }
        }
        
        # Update categories with Russian translations
        for slug, translation in category_translations.items():
            category = GuideCategory.query.filter_by(slug=slug).first()
            if category:
                category.name = translation['name']
                category.description = translation['description']
                print(f"Updated category: {slug} -> {translation['name']}")
        
        # Russian translations for guides
        guide_translations = {
            'strength-knights': {
                'title': 'Список уровней рыцарей силы',
                'excerpt': 'Полный список уровней, ранжирующий всех рыцарей силы от EX+ до F уровня, с подробными объяснениями жизнеспособности каждого рыцаря.'
            },
            'intellect-knights': {
                'title': 'Список уровней рыцарей интеллекта',
                'excerpt': 'Подробный список уровней для всех рыцарей интеллекта, ранжирующий их на основе исследовательских способностей и развития королевства.'
            },
            'alliance-arena': {
                'title': 'Руководство по Арене Альянса',
                'excerpt': 'Полное руководство по Арене Альянса, включая механику, стратегии и рекомендуемых рыцарей для соревновательной игры.'
            },
            'twilight-castle': {
                'title': 'Руководство по Сумеречному Замку',
                'excerpt': 'Подробное руководство по событию Сумеречного Замка, включая механику этажей, советы по подготовке и рекомендуемые составы команд.'
            }
        }
        
        # Update guides with Russian translations
        for slug, translation in guide_translations.items():
            guide = Guide.query.filter_by(slug=slug).first()
            if guide:
                guide.title = translation['title']
                guide.excerpt = translation['excerpt']
                print(f"Updated guide: {slug} -> {translation['title']}")
        
        db.session.commit()
        print("Russian translation completed!")

if __name__ == '__main__':
    translate_to_russian()