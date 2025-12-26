import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment
from webassets.bundle import Bundle
from config import config

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

    # Import models to ensure they are registered with SQLAlchemy
    with flask_app.app_context():
        import app.models

    def make_shell_context():
        from app.models import LearningNote
        return dict(db=db, LearningNote=LearningNote)

    flask_app.shell_context_processor(make_shell_context)

    return flask_app
