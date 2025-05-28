import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from app.config import config_by_name

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Updated CORS configuration with more permissive settings
    CORS(app, 
         resources={r"/api/*": {"origins": "*"}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization", "Accept"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Import and register blueprints
    from app.controllers.auth import auth_bp
    from app.controllers.contacts import contacts_bp
    from app.controllers.simple_auth import simple_auth_bp
    from app.controllers.simple_contacts import simple_contacts_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(contacts_bp, url_prefix='/api/contacts')
    app.register_blueprint(simple_auth_bp, url_prefix='/api/simple_auth')
    app.register_blueprint(simple_contacts_bp, url_prefix='/api/simple_contacts')
    
    # Shell context processor
    @app.shell_context_processor
    def shell_context():
        return {
            'db': db,
            'User': User,
            'Contact': Contact
        }
    
    # Import models for migrations
    from app.models.user import User
    from app.models.contact import Contact
    
    return app