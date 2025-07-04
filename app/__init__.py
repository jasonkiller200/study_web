import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_assets import Environment, Bundle
from config import config

db = SQLAlchemy()
assets = Environment()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    assets.init_app(app)

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
    app.register_blueprint(main_blueprint)

    from .notes import notes as notes_blueprint
    app.register_blueprint(notes_blueprint, url_prefix='/notes')

    return app
