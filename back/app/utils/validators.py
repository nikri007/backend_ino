import os
from werkzeug.utils import secure_filename
from flask import current_app
from dateutil import parser

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Check if file has an allowed extension
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """
    Save an image file to the upload folder
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Create a unique filename to avoid overwriting
        unique_filename = f"{os.urandom(8).hex()}_{filename}"
        
        # Ensure upload folder exists
        os.makedirs(os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER']), exist_ok=True)
        
        # Save the file
        file_path = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def validate_date(date_string):
    """
    Validate and parse a date string
    """
    try:
        return parser.parse(date_string).date()
    except (ValueError, TypeError):
        return None