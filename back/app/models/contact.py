import json
from datetime import datetime
from app import db
from marshmallow import Schema, fields, validate

class Contact(db.Model):
    """Contact model for storing contact related details"""
    __tablename__ = "contacts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)
    phone_numbers = db.Column(db.Text, nullable=False)  # Stored as JSON string
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_phone_numbers(self):
        """Return phone numbers as a list"""
        return json.loads(self.phone_numbers)
    
    def set_phone_numbers(self, phone_list):
        """Set phone numbers from a list"""
        self.phone_numbers = json.dumps(phone_list)
    
    def __repr__(self):
        return f"<Contact {self.first_name} {self.last_name}>"


class ContactSchema(Schema):
    """Schema for Contact model serialization and validation"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    company = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    phone_numbers = fields.List(fields.Str())
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)