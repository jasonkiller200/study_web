import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment
from webassets.bundle import Bundle
from config import config
import markdown
import bleach

db = SQLAlchemy()
assets = Environment()

def create_app(config_name):
    flask_app = Flask(__name__, instance_relative_config=True)
    flask_app.config.from_object(config[config_name])

    # Ensure the instance folder exists
    try:
        os.makedirs(flask_app.instance_path)
    except OSError:
        pass

    db.init_app(flask_app)
    assets.init_app(flask_app)

    # Define asset bundles
    js_bundle = Bundle(
        'js/bootstrap.bundle.min.js',
        'js/prism-core.min.js',
        'js/prism-autoloader.min.js',
        'js/quill.js',
        'js/tagify.min.js',
        'js/tagify.polyfills.min.js',
        output='gen/packed.js')
    assets.register('js_all', js_bundle)

    css_bundle = Bundle(
        'css/bootstrap.min.css',
        'css/all.min.css',
        'css/prism.min.css',
        'css/tagify.css',
        'css/quill.snow.css',
        'css/custom.css', # Assuming you might have custom CSS
        filters='cssrewrite', output='gen/packed.css')
    assets.register('css_all', css_bundle)

    from .main import main as main_blueprint
    flask_app.register_blueprint(main_blueprint)

    from .notes import notes as notes_blueprint
    flask_app.register_blueprint(notes_blueprint, url_prefix='/notes')

    # Register Markdown filter
    @flask_app.template_filter('markdown')
    def markdown_filter(text):
        """Convert Markdown to HTML with syntax highlighting support."""
        if not text:
            return ''
        
        # Configure markdown extensions
        md = markdown.Markdown(extensions=[
            'extra',  # Tables, fenced code blocks, etc.
            'codehilite',  # Syntax highlighting
            'nl2br',  # New line to <br>
            'sane_lists'  # Better list handling
        ])
        
        # Convert markdown to HTML
        html = md.convert(text)
        
        # Sanitize HTML to prevent XSS (allow common tags)
        allowed_tags = [
            'a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 
            'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'span', 'div', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
            'img', 'del', 'ins', 'mark', 'sub', 'sup'
        ]
        allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title', 'target', 'rel'],
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'code': ['class'],
            'pre': ['class'],
            'span': ['class'],
            'div': ['class']
        }
        
        safe_html = bleach.clean(
            html,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=False
        )
        
        return safe_html

    # Import models to ensure they are registered with SQLAlchemy
    with flask_app.app_context():
        import app.models

    def make_shell_context():
        from app.models import LearningNote
        return dict(db=db, LearningNote=LearningNote)

    flask_app.shell_context_processor(make_shell_context)

    return flask_app
