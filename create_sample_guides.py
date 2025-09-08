#!/usr/bin/env python3
"""
Script to create sample guide categories and content for King's Choice Management App
"""

from app import app, create_tables
from models import GuideCategory, Guide
from database import db

def create_sample_data():
    """Create sample guide categories and guides"""
    
    with app.app_context():
        # Create tables if they don't exist
        create_tables()
        
        # Create sample categories (Russian translations)
        categories_data = [
            {
                'name': 'Рыцари',
                'slug': 'knights',
                'description': 'Подробные руководства по всем типам рыцарей, включая списки уровней, сборки и стратегии.',
                'icon': 'bi-shield-fill',
                'sort_order': 1
            },
            {
                'name': 'События',
                'slug': 'events',
                'description': 'Руководства и стратегии по событиям для Арены Альянса, Сумеречного Замка и других игровых событий.',
                'icon': 'bi-calendar-event-fill',
                'sort_order': 2
            },
            {
                'name': 'Альянс',
                'slug': 'alliance',
                'description': 'Управление альянсом, стратегии и руководства по координации.',
                'icon': 'bi-people-fill',
                'sort_order': 3
            },
            {
                'name': 'Ресурсы',
                'slug': 'resources',
                'description': 'Управление ресурсами, руководства по фарму и советы по оптимизации.',
                'icon': 'bi-gem',
                'sort_order': 4
            }
        ]
        
        # Create categories
        for cat_data in categories_data:
            existing = GuideCategory.query.filter_by(slug=cat_data['slug']).first()
            if not existing:
                category = GuideCategory(**cat_data)
                db.session.add(category)
                print(f"Created category: {cat_data['name']}")
        
        db.session.commit()
        
        # Get created categories
        knights_cat = GuideCategory.query.filter_by(slug='knights').first()
        events_cat = GuideCategory.query.filter_by(slug='events').first()
        
        # Create sample guides (Russian translations)
        guides_data = [
            {
                'title': 'Список уровней рыцарей силы',
                'slug': 'strength-knights',
                'content': '''<h1><strong>STRENGTH KNIGHT TIER LIST</strong></h1>

<p>Typically, most Knights that have an Aura will rank high on any Tier List of the Best King's Choice Knights and this one is no different. However, it is also worth noting that many of the top Knights only become available to players after a few months in the game as certain unlock items, such as Crowns, begin to drop from Events. Therefore, in the early game, you will likely see yourself developing Knights in this list from ranks S. This is perfectly viable as many of these, especially the Arthurian Legends, will continue to be viable as you move forward.</p>

<p>In the Tier List below, we rank the Best Strength Knights in King's Choice from best to worst. EX+ represents the very best strength Knights, whilst F represents the absolute worst, and these will never be worth your time!</p>

<h2><strong>EX+</strong></h2>
<ul>
<li>Joan of Arc</li>
</ul>

<h2><strong>EX</strong></h2>
<ul>
<li>Queen Elizabeth</li>
</ul>

<h2><strong>SSS</strong></h2>
<ul>
<li>Frederick Barbarossa</li>
<li>Charlemagne</li>
<li>Richard I</li>
<li>William I</li>
<li>El Cid</li>
<li>Igor</li>
<li>Roland</li>
<li>Siegfried</li>
<li>Vlad Dracula</li>
</ul>

<h2><strong>S</strong></h2>
<ul>
<li>Guinevere</li>
<li>Lancelot</li>
<li>Mordred</li>
<li>Gawain</li>
<li>King Arthur</li>
<li>Leonardo da Vinci</li>
<li>Queen Christina</li>
</ul>

<h2><strong>A</strong></h2>
<ul>
<li>Thomas Aquinas</li>
<li>Aristotle</li>
<li>Homer</li>
<li>Nicolaus Copernicus</li>
</ul>

<h2><strong>B</strong></h2>
<ul>
<li>William Shakespeare</li>
<li>Madame de Pompadour</li>
<li>Jacques</li>
<li>Geoffrey Plantagenet</li>
<li>Robin Hood</li>
<li>Edward</li>
<li>Francis Drake</li>
</ul>

<h2><strong>C</strong></h2>
<ul>
<li>Ferdinand Magellan</li>
<li>Galileo Galilei</li>
<li>Bertrand du Guesclin</li>
<li>Ambrose</li>
<li>Charles Martel</li>
<li>Sundiata Keita</li>
</ul>

<h2><strong>F</strong></h2>
<ul>
<li>Duke of York</li>
<li>Rose</li>
<li>Bradamante</li>
<li>Hypatia</li>
<li>Merlin</li>
<li>Michelangelo</li>
<li>Earl of Warwick</li>
<li>Talbot</li>
<li>Roger Bacon</li>
<li>Old Hunter</li>
<li>Greg</li>
<li>Thomas Cromwell</li>
<li>Golyat</li>
<li>Dante Alighieri</li>
<li>Charles Brandon</li>
<li>Simon de Montfort</li>
<li>John Blanke</li>
<li>Harpagon</li>
<li>Marco Polo</li>
<li>Terrence</li>
<li>Johannes Gutenberg</li>
<li>Artemisia Gentileschi</li>
<li>Moremi Ajasoro</li>
<li>Roger</li>
<li>William Tell</li>
<li>Raphael</li>
<li>Andreas Vesalius</li>
<li>Thomas Boleyn</li>
<li>Andrew</li>
<li>Bontemps</li>
</ul>''',
                'excerpt': 'Полный список уровней, ранжирующий всех рыцарей силы от EX+ до F уровня, с подробными объяснениями жизнеспособности каждого рыцаря.',
                'category_id': knights_cat.id,
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Список уровней рыцарей интеллекта',
                'slug': 'intellect-knights',
                'content': '''<h1><strong>INTELLECT KNIGHT TIER LIST</strong></h1>

<p>Intellect Knights are crucial for your kingdom's development and research capabilities. This tier list ranks all Intellect Knights based on their effectiveness in various game modes and their overall utility.</p>

<h2><strong>EX+</strong></h2>
<ul>
<li>Leonardo da Vinci</li>
</ul>

<h2><strong>EX</strong></h2>
<ul>
<li>Nicolaus Copernicus</li>
<li>Galileo Galilei</li>
</ul>

<h2><strong>SSS</strong></h2>
<ul>
<li>Thomas Aquinas</li>
<li>Aristotle</li>
<li>Homer</li>
<li>Roger Bacon</li>
</ul>

<h2><strong>S</strong></h2>
<ul>
<li>William Shakespeare</li>
<li>Dante Alighieri</li>
<li>Johannes Gutenberg</li>
<li>Raphael</li>
</ul>

<h2><strong>A</strong></h2>
<ul>
<li>Michelangelo</li>
<li>Andreas Vesalius</li>
<li>Artemisia Gentileschi</li>
<li>Moremi Ajasoro</li>
</ul>

<h2><strong>B</strong></h2>
<ul>
<li>Hypatia</li>
<li>Marco Polo</li>
<li>William Tell</li>
</ul>

<h2><strong>C</strong></h2>
<ul>
<li>Merlin</li>
<li>Thomas Cromwell</li>
<li>Thomas Boleyn</li>
</ul>

<h2><strong>F</strong></h2>
<ul>
<li>All other Intellect Knights not listed above</li>
</ul>''',
                'excerpt': 'Подробный список уровней для всех рыцарей интеллекта, ранжирующий их на основе исследовательских способностей и развития королевства.',
                'category_id': knights_cat.id,
                'is_published': True,
                'is_featured': True
            },
            {
                'title': 'Руководство по Арене Альянса',
                'slug': 'alliance-arena',
                'content': '''<h1><strong>ALLIANCE ARENA GUIDE</strong></h1>

<p>Alliance Arena is one of the most competitive events in King's Choice. This guide will help you understand the mechanics and develop winning strategies.</p>

<h2><strong>Event Overview</strong></h2>
<p>Alliance Arena is a PvP event where alliances compete against each other for rewards and glory. The event typically lasts for several days and features multiple rounds of competition.</p>

<h2><strong>Key Mechanics</strong></h2>
<ul>
<li><strong>Matchmaking:</strong> Alliances are matched based on their power and previous performance</li>
<li><strong>Battle System:</strong> Each alliance can deploy multiple knights in strategic formations</li>
<li><strong>Rewards:</strong> Based on final ranking and individual performance</li>
</ul>

<h2><strong>Strategy Tips</strong></h2>
<ol>
<li><strong>Formation Planning:</strong> Arrange your strongest knights in optimal positions</li>
<li><strong>Resource Management:</strong> Save resources for key battles</li>
<li><strong>Communication:</strong> Coordinate with alliance members for maximum effectiveness</li>
<li><strong>Timing:</strong> Know when to attack and when to defend</li>
</ol>

<h2><strong>Recommended Knights</strong></h2>
<p>Focus on developing these knights for Alliance Arena:</p>
<ul>
<li>Joan of Arc (EX+)</li>
<li>Queen Elizabeth (EX)</li>
<li>Frederick Barbarossa (SSS)</li>
<li>Charlemagne (SSS)</li>
</ul>''',
                'excerpt': 'Полное руководство по Арене Альянса, включая механику, стратегии и рекомендуемых рыцарей для соревновательной игры.',
                'category_id': events_cat.id,
                'is_published': True,
                'is_featured': False
            },
            {
                'title': 'Руководство по Сумеречному Замку',
                'slug': 'twilight-castle',
                'content': '''<h1><strong>TWILIGHT CASTLE GUIDE</strong></h1>

<p>Twilight Castle is a challenging PvE event that requires careful planning and strong knights. This guide covers everything you need to know.</p>

<h2><strong>Event Structure</strong></h2>
<p>Twilight Castle consists of multiple floors, each with increasing difficulty. Players must clear each floor to progress to the next level.</p>

<h2><strong>Floor Mechanics</strong></h2>
<ul>
<li><strong>Boss Battles:</strong> Each floor has a powerful boss with unique abilities</li>
<li><strong>Resource Requirements:</strong> Different floors require different types of resources</li>
<li><strong>Time Limits:</strong> Some floors have time restrictions</li>
</ul>

<h2><strong>Preparation Tips</strong></h2>
<ol>
<li><strong>Level Up Knights:</strong> Ensure your main knights are at maximum level</li>
<li><strong>Equipment:</strong> Upgrade weapons and armor for better stats</li>
<li><strong>Formations:</strong> Experiment with different knight combinations</li>
<li><strong>Resources:</strong> Stock up on healing items and buffs</li>
</ol>

<h2><strong>Recommended Team Compositions</strong></h2>
<p>For different floor types:</p>
<ul>
<li><strong>Physical Floors:</strong> Focus on Strength and Leadership knights</li>
<li><strong>Magic Floors:</strong> Include Intellect knights for magical damage</li>
<li><strong>Balanced Floors:</strong> Mix of all knight types</li>
</ul>''',
                'excerpt': 'Подробное руководство по событию Сумеречного Замка, включая механику этажей, советы по подготовке и рекомендуемые составы команд.',
                'category_id': events_cat.id,
                'is_published': True,
                'is_featured': False
            }
        ]
        
        # Create guides
        for guide_data in guides_data:
            existing = Guide.query.filter_by(slug=guide_data['slug']).first()
            if not existing:
                guide = Guide(**guide_data)
                db.session.add(guide)
                print(f"Created guide: {guide_data['title']}")
        
        db.session.commit()
        print("Sample data creation completed!")

if __name__ == '__main__':
    create_sample_data()