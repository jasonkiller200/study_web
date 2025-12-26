from . import db
from datetime import datetime
import json

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class LearningNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    
    # Replaced original category string field
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('notes', lazy=True))

    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<LearningNote {self.title}>'

    @property
    def processed_tags(self):
        if not self.tags: # If tags is None or empty string
            return []
        try:
            tags_list = json.loads(self.tags)
            if isinstance(tags_list, list) and all(isinstance(tag, dict) and 'value' in tag for tag in tags_list):
                return [tag['value'] for tag in tags_list]
            else:
                # Fallback for non-Tagify JSON or other formats
                return [tag.strip() for tag in self.tags.split(',')]
        except json.JSONDecodeError:
            # If not valid JSON, treat as comma-separated string
            return [tag.strip() for tag in self.tags.split(',')]