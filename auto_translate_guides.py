#!/usr/bin/env python3
"""
Script to automatically translate existing guides to Russian
"""

from app import app
from models import Guide
from database import db
from deep_translator import GoogleTranslator

def translate_guides():
    """Translate all existing guides to Russian"""
    
    with app.app_context():
        guides = Guide.query.all()
        translator = GoogleTranslator(source='en', target='ru')
        
        for guide in guides:
            try:
                print(f"Translating: {guide.title}")
                
                # Translate title
                translated_title = translator.translate(guide.title)
                
                # Translate content (split into chunks if too long)
                content_chunks = [guide.content[i:i+4000] for i in range(0, len(guide.content), 4000)]
                translated_content = ""
                for chunk in content_chunks:
                    translated_chunk = translator.translate(chunk)
                    translated_content += translated_chunk
                
                # Translate excerpt if exists
                translated_excerpt = None
                if guide.excerpt:
                    translated_excerpt = translator.translate(guide.excerpt)
                
                # Create Russian version
                russian_guide = Guide(
                    title=translated_title,
                    slug=f"{guide.slug}-ru",
                    content=translated_content,
                    excerpt=translated_excerpt,
                    category_id=guide.category_id,
                    featured_image=guide.featured_image,
                    is_published=guide.is_published,
                    is_featured=guide.is_featured
                )
                
                db.session.add(russian_guide)
                print(f"Created Russian version: {translated_title}")
                
            except Exception as e:
                print(f"Error translating {guide.title}: {str(e)}")
        
        db.session.commit()
        print("Translation completed!")

if __name__ == '__main__':
    translate_guides()