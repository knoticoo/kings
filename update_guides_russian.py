#!/usr/bin/env python3
"""
Simple script to update guide categories and content to Russian
This script directly updates the database without requiring Flask
"""

import sqlite3
import os

def update_guides_to_russian():
    """Update guide categories and content to Russian"""
    
    # Database file path
    db_path = 'kings_choice.db'
    
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update guide categories to Russian
        category_updates = [
            ("Рыцари", "Подробные руководства по всем типам рыцарей, включая списки уровней, сборки и стратегии.", "knights"),
            ("События", "Руководства и стратегии по событиям для Арены Альянса, Сумеречного Замка и других игровых событий.", "events"),
            ("Альянс", "Управление альянсом, стратегии и руководства по координации.", "alliance"),
            ("Ресурсы", "Управление ресурсами, руководства по фарму и советы по оптимизации.", "resources")
        ]
        
        for name, description, slug in category_updates:
            cursor.execute("""
                UPDATE guide_category 
                SET name = ?, description = ? 
                WHERE slug = ?
            """, (name, description, slug))
            print(f"Updated category: {slug} -> {name}")
        
        # Update guide titles and excerpts to Russian
        guide_updates = [
            ("Список уровней рыцарей силы", "Полный список уровней, ранжирующий всех рыцарей силы от EX+ до F уровня, с подробными объяснениями жизнеспособности каждого рыцаря.", "strength-knights"),
            ("Список уровней рыцарей интеллекта", "Подробный список уровней для всех рыцарей интеллекта, ранжирующий их на основе исследовательских способностей и развития королевства.", "intellect-knights"),
            ("Руководство по Арене Альянса", "Полное руководство по Арене Альянса, включая механику, стратегии и рекомендуемых рыцарей для соревновательной игры.", "alliance-arena"),
            ("Руководство по Сумеречному Замку", "Подробное руководство по событию Сумеречного Замка, включая механику этажей, советы по подготовке и рекомендуемые составы команд.", "twilight-castle")
        ]
        
        for title, excerpt, slug in guide_updates:
            cursor.execute("""
                UPDATE guide 
                SET title = ?, excerpt = ? 
                WHERE slug = ?
            """, (title, excerpt, slug))
            print(f"Updated guide: {slug} -> {title}")
        
        conn.commit()
        print("Russian translation completed successfully!")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    update_guides_to_russian()