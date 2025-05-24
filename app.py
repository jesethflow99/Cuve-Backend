from flask import Flask
import config
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from flask_migrate import Migrate
import os
from importlib import import_module
from logger import setup_logger
from flask_marshmallow import Marshmallow


logger = setup_logger(__name__)

def load_blueprints(app):
    for filename in os.listdir('blueprints'):
        dir_path = f'blueprints/{filename}'
        if not os.path.isdir(dir_path):
            continue
        import_path = f'blueprints.{filename}.routes'
        try:
            module = import_module(import_path)
            if hasattr(module, 'blueprint'):
                # Usa el nombre del folder como prefix
                app.register_blueprint(module.blueprint, url_prefix=f'/{filename}')
                print(f"Registered blueprint: {import_path} with prefix '/{filename}'")
        except ImportError as e:
            logger.error(f"Could not import {import_path}: {e}")

        
# Create the Flask application
def create_app():
    app = Flask(__name__)
    
    
    # Load configuration
    app.config.from_object(config.get_config())
    # Load blueprints
    load_blueprints(app)
    # Initialize extensions
    ma = Marshmallow(app)
    CORS(app)
    db.init_app(app)
    jwt = JWTManager()
    jwt.init_app(app)
    migrate = Migrate()
    migrate.init_app(app, db)
    
    return app