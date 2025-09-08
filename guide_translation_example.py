# Example of how to add translation support to guides

# Option 2A: Separate translation fields
class Guide(db.Model):
    # ... existing fields ...
    title_en = db.Column(db.String(200))
    title_ru = db.Column(db.String(200))
    content_en = db.Column(db.Text)
    content_ru = db.Column(db.Text)
    excerpt_en = db.Column(db.Text)
    excerpt_ru = db.Column(db.Text)
    
    def get_title(self, locale='en'):
        return getattr(self, f'title_{locale}', self.title_en)
    
    def get_content(self, locale='en'):
        return getattr(self, f'content_{locale}', self.content_en)

# Option 2B: JSON translation field
class Guide(db.Model):
    # ... existing fields ...
    translations = db.Column(db.JSON)  # {"en": {"title": "...", "content": "..."}, "ru": {...}}
    
    def get_translation(self, field, locale='en'):
        if self.translations and locale in self.translations:
            return self.translations[locale].get(field, self.translations.get('en', {}).get(field, ''))
        return getattr(self, field, '')

# Option 3: Automatic Translation API
def translate_guide_content(guide, target_language):
    """Use translation API to automatically translate guide content"""
    from deep_translator import GoogleTranslator
    
    translator = GoogleTranslator(source='en', target=target_language)
    
    translated_title = translator.translate(guide.title)
    translated_content = translator.translate(guide.content)
    translated_excerpt = translator.translate(guide.excerpt) if guide.excerpt else None
    
    return {
        'title': translated_title,
        'content': translated_content,
        'excerpt': translated_excerpt
    }