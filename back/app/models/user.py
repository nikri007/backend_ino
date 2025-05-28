import json
from datetime import datetime
from app import db, bcrypt
from marshmallow import Schema, fields, validate, validates, ValidationError
from email_validator import validate_email, EmailNotValidError

class User(db.Model):
    """User model for storing user related details"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    phone_numbers = db.Column(db.Text, nullable=False)  # Stored as JSON string
    address = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.String(255), nullable=True)
    registered_on = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    contacts = db.relationship('Contact', backref='user', lazy=True, cascade='all, delete-orphan')
    
    @property
    def password(self):
        raise AttributeError('password: write-only field')
    
    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_phone_numbers(self):
        """Return phone numbers as a list"""
        return json.loads(self.phone_numbers)
    
    def set_phone_numbers(self, phone_list):
        """Set phone numbers from a list"""
        self.phone_numbers = json.dumps(phone_list)
    
    def __repr__(self):
        return f"<User {self.email}>"


class UserSchema(Schema):
    """Schema for User model serialization and validation"""
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    confirm_password = fields.Str(required=True, load_only=True)
    date_of_birth = fields.Date(required=True)
    gender = fields.Str(required=True, validate=validate.OneOf(['Male', 'Female', 'Other']))
    phone_numbers = fields.List(fields.Str(), required=True)
    address = fields.Str(required=True)
    profile_picture = fields.Str(dump_only=True)
    registered_on = fields.DateTime(dump_only=True)
    
    @validates('email')
    def validate_email(self, email):
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValidationError('Invalid email address.')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            raise ValidationError('Email address already registered.')
    
    @validates('confirm_password')
    def validate_confirm_password(self, confirm_password, **kwargs):
        """
        Validate that confirm_password matches password.
        Fixed to handle marshmallow 3.x properly.
        """
        data = kwargs.get('data', {})
        
        if data and 'password' in data:
            password = data['password']
            if confirm_password != password:
                raise ValidationError('Passwords must match.')
        else:
            # Try to get it from the schema's context
            password = self.context.get('password', '')
            if confirm_password != password:
                raise ValidationError('Passwords must match.')