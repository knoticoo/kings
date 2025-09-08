#!/usr/bin/env python3
"""
Script to create the Intellect Knight Tier List guide from Discord text
"""

from app import app, create_tables
from models import GuideCategory, Guide
from database import db

def create_intellect_tier_list():
    """Create the Intellect Knight Tier List guide"""
    
    with app.app_context():
        # Create tables if they don't exist
        create_tables()
        
        # Get or create Knights category
        knights_cat = GuideCategory.query.filter_by(slug='knights').first()
        if not knights_cat:
            knights_cat = GuideCategory(
                name='Knights',
                slug='knights',
                description='Comprehensive guides for all types of knights including tier lists, builds, and strategies.',
                icon='bi-shield-fill',
                sort_order=1
            )
            db.session.add(knights_cat)
            db.session.commit()
            print("Created Knights category")
        
        # Check if guide already exists
        existing_guide = Guide.query.filter_by(slug='intellect-tier-knight-list').first()
        if existing_guide:
            print("Intellect Tier Knight List guide already exists")
            return
        
        # Create the guide with formatted content
        guide = Guide(
            title='INTELLECT TIER KNIGHT LIST',
            slug='intellect-tier-knight-list',
            content='''<h1><strong>INTELLECT TIER KNIGHT LIST</strong></h1>

<p>Typically, most Knights that have an Aura will rank high on any Tier List of the Best King's Choice Knights and this one is no different. However, it is also worth noting that many of the top Knights only become available to players after a few months in the game as certain unlock items, such as Crowns, begin to drop from Events. Therefore, in the early game, you will likely see yourself developing Dante Alighieri in this list from rank C. This is perfectly viable for the first couple of months however once you have access to the Rank S Knights, you should make the switch!</p>

<p>In the Tier List below, we rank the Best Intellect Knights in King's Choice from best to worst. EX+ represents the very best intellect Knights, whilst F represents the absolute worst, and these will never be worth your time!</p>

<div class="tier-list">
    <div class="tier-row ex-plus">
        <div class="tier-label"><strong>EX+</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Joan of Arc</li>
            </ul>
        </div>
    </div>

    <div class="tier-row ex">
        <div class="tier-label"><strong>EX</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Queen Elizabeth</li>
            </ul>
        </div>
    </div>

    <div class="tier-row sss">
        <div class="tier-label"><strong>SSS</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Vlad Dracula</li>
            </ul>
        </div>
    </div>

    <div class="tier-row s">
        <div class="tier-label"><strong>S</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Frederick Barbarossa</li>
                <li>Charlemagne</li>
                <li>Richard I</li>
                <li>William I</li>
                <li>Queen Christina</li>
            </ul>
        </div>
    </div>

    <div class="tier-row a">
        <div class="tier-label"><strong>A</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Nicolaus Copernicus</li>
                <li>Roger Bacon</li>
            </ul>
        </div>
    </div>

    <div class="tier-row b">
        <div class="tier-label"><strong>B</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Raphael</li>
                <li>William Shakespeare</li>
                <li>El Cid</li>
                <li>Siegfried</li>
                <li>Guinevere</li>
                <li>Rose</li>
                <li>Geoffrey Plantagenet</li>
            </ul>
        </div>
    </div>

    <div class="tier-row c">
        <div class="tier-label"><strong>C</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Dante Alighieri</li>
                <li>Igor</li>
                <li>Roland</li>
                <li>Mordred</li>
                <li>Gawain</li>
                <li>King Arthur</li>
                <li>Merlin</li>
                <li>Thomas Boleyn</li>
                <li>Ferdinand Magellan</li>
                <li>Andreas Vesalius</li>
            </ul>
        </div>
    </div>

    <div class="tier-row f">
        <div class="tier-label"><strong>F</strong></div>
        <div class="tier-knights">
            <ul>
                <li>Lancelot</li>
                <li>Michelangelo</li>
                <li>Bradamante</li>
                <li>Earl of Warwick</li>
                <li>Hypatia</li>
                <li>Johannes Gutenberg</li>
                <li>Artemisia Gentileschi</li>
                <li>Thomas Aquinas</li>
                <li>Homer</li>
                <li>Marco Polo</li>
                <li>Greg</li>
                <li>Roger</li>
                <li>Golyat</li>
                <li>Madame de Pompadour</li>
                <li>Edward</li>
                <li>Francis Drake</li>
                <li>Galileo Galilei</li>
                <li>Bertrand du Guesclin</li>
                <li>Sundiata Keita</li>
                <li>Jacques</li>
                <li>Robin Hood</li>
                <li>Simon de Montfort</li>
                <li>Moremi Ajasoro</li>
                <li>Harpagon</li>
                <li>Leonardo da Vinci</li>
                <li>Aristotle</li>
                <li>Charles Brandon</li>
                <li>Terrence</li>
                <li>Duke of York</li>
                <li>John Blanke</li>
                <li>Andrew</li>
                <li>Bontemps</li>
                <li>William Tell</li>
                <li>Old Hunter</li>
            </ul>
        </div>
    </div>
</div>

<style>
.tier-list {
    margin: 2rem 0;
}

.tier-row {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    border-radius: 0.5rem;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tier-label {
    min-width: 80px;
    padding: 1rem;
    font-weight: bold;
    text-align: center;
    color: white;
    font-size: 1.2rem;
}

.tier-knights {
    flex: 1;
    padding: 1rem;
    background: white;
}

.tier-knights ul {
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tier-knights li {
    background: #f8f9fa;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    border: 1px solid #dee2e6;
    font-size: 0.9rem;
}

.ex-plus .tier-label { background: linear-gradient(135deg, #ff6b6b, #ee5a24); }
.ex .tier-label { background: linear-gradient(135deg, #ff9ff3, #f368e0); }
.sss .tier-label { background: linear-gradient(135deg, #ffd93d, #ff6b6b); }
.s .tier-label { background: linear-gradient(135deg, #ff9ff3, #f368e0); }
.a .tier-label { background: linear-gradient(135deg, #74b9ff, #0984e3); }
.b .tier-label { background: linear-gradient(135deg, #00b894, #00a085); }
.c .tier-label { background: linear-gradient(135deg, #fdcb6e, #e17055); }
.f .tier-label { background: linear-gradient(135deg, #636e72, #2d3436); }
</style>''',
            excerpt='Complete tier list ranking all Intellect Knights from EX+ to F tier, with detailed explanations of each knight\'s viability and early game recommendations.',
            category_id=knights_cat.id,
            is_published=True,
            is_featured=True
        )
        
        db.session.add(guide)
        db.session.commit()
        print("Created Intellect Tier Knight List guide successfully!")

if __name__ == '__main__':
    create_intellect_tier_list()