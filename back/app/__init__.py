import os
from flask import Flask, send_from_directory
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
    
    # Import and register blueprints - ONLY the simple ones that exist
    from app.controllers.simple_auth import simple_auth_bp
    from app.controllers.simple_contacts import simple_contacts_bp
    
    # Register only the existing blueprints
    app.register_blueprint(simple_auth_bp, url_prefix='/api/simple_auth')
    app.register_blueprint(simple_contacts_bp, url_prefix='/api/simple_contacts')
    
    # Route to serve uploaded profile pictures
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        """Serve uploaded files (profile pictures)"""
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        return send_from_directory(upload_folder, filename)
    
    # Route to test image serving
    @app.route('/api/test-upload')
    def test_upload():
        """Test endpoint to check upload functionality"""
        upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
        upload_path = os.path.join(app.root_path, upload_folder)
        
        # Ensure upload folder exists
        os.makedirs(upload_path, exist_ok=True)
        
        return {
            'message': 'Upload functionality is working',
            'upload_folder': upload_folder,
            'upload_path': upload_path,
            'folder_exists': os.path.exists(upload_path),
            'max_content_length': app.config.get('MAX_CONTENT_LENGTH', 'Not set')
        }
    
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