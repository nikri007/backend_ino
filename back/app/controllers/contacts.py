from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import or_
import json
import traceback
from app import db
from app.models.contact import Contact, ContactSchema
from app.utils.auth import token_required

contacts_bp = Blueprint('contacts', __name__)
contact_schema = ContactSchema()
contacts_schema = ContactSchema(many=True)

@contacts_bp.route('/', methods=['POST'])
@token_required
def create_contact(current_user):
    """
    Create a new contact
    """
    print("=== CREATE CONTACT ENDPOINT CALLED ===")
    print(f"User: {current_user.email}")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Get post data
        post_data = request.get_json()
        print(f"Contact data: {post_data}")
        
        if not post_data:
            print("No input data provided")
            return jsonify({'error': 'No input data provided'}), 400
            
        # Validate and deserialize input
        contact_data = contact_schema.load(post_data)
        
        # Create new contact
        new_contact = Contact(
            user_id=current_user.id,
            first_name=contact_data['first_name'],
            last_name=contact_data['last_name'],
            company=contact_data.get('company'),
            address=contact_data.get('address')
        )
        
        # Set phone numbers as JSON string
        new_contact.set_phone_numbers(contact_data.get('phone_numbers', []))
        
        # Save contact to database
        db.session.add(new_contact)
        db.session.commit()
        
        print("Contact created successfully")
        # Return created contact
        return jsonify(contact_schema.dump(new_contact)), 201
        
    except ValidationError as err:
        print(f"Validation error: {err.messages}")
        return jsonify({'error': err.messages}), 400
    except Exception as e:
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@contacts_bp.route('/', methods=['GET'])
@token_required
def get_contacts(current_user):
    """
    Get all contacts with pagination and search
    """
    print("=== GET CONTACTS ENDPOINT CALLED ===")
    print(f"User: {current_user.email}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Query params: {dict(request.args)}")
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        print(f"Page: {page}, Per page: {per_page}, Search: '{search}'")
        
        # Cap per_page to avoid excessive loads
        if per_page > 50:
            per_page = 50
            
        # Create base query
        query = Contact.query.filter_by(user_id=current_user.id)
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    Contact.first_name.ilike(search_term),
                    Contact.last_name.ilike(search_term),
                    Contact.company.ilike(search_term),
                    Contact.address.ilike(search_term)
                )
            )
            
        # Apply pagination
        pagination = query.order_by(Contact.first_name, Contact.last_name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Prepare response
        contacts = pagination.items
        total = pagination.total
        pages = pagination.pages
        
        print(f"Found {total} contacts over {pages} pages")
        
        # Transform contacts list
        result = contacts_schema.dump(contacts)
        
        return jsonify({
            'contacts': result,
            'total': total,
            'pages': pages,
            'page': page,
            'per_page': per_page
        }), 200
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@contacts_bp.route('/<int:contact_id>', methods=['GET'])
@token_required
def get_contact(current_user, contact_id):
    """
    Get a specific contact by ID
    """
    print(f"=== GET CONTACT {contact_id} ENDPOINT CALLED ===")
    print(f"User: {current_user.email}")
    
    try:
        # Find contact
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            print(f"Contact {contact_id} not found")
            return jsonify({'error': 'Contact not found'}), 404
            
        print(f"Contact found: {contact.first_name} {contact.last_name}")
        # Return contact details
        return jsonify(contact_schema.dump(contact)), 200
        
    except Exception as e:
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@contacts_bp.route('/<int:contact_id>', methods=['PUT'])
@token_required
def update_contact(current_user, contact_id):
    """
    Update an existing contact
    """
    print(f"=== UPDATE CONTACT {contact_id} ENDPOINT CALLED ===")
    print(f"User: {current_user.email}")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Find contact
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            print(f"Contact {contact_id} not found")
            return jsonify({'error': 'Contact not found'}), 404
            
        # Get post data
        post_data = request.get_json()
        print(f"Update data: {post_data}")
        
        if not post_data:
            print("No input data provided")
            return jsonify({'error': 'No input data provided'}), 400
            
        # Validate and deserialize input
        contact_data = contact_schema.load(post_data)
        
        # Update contact
        contact.first_name = contact_data['first_name']
        contact.last_name = contact_data['last_name']
        contact.company = contact_data.get('company')
        contact.address = contact_data.get('address')
        
        # Update phone numbers
        if 'phone_numbers' in contact_data:
            contact.set_phone_numbers(contact_data['phone_numbers'])
        
        # Save changes
        db.session.commit()
        
        print(f"Contact {contact_id} updated successfully")
        # Return updated contact
        return jsonify(contact_schema.dump(contact)), 200
        
    except ValidationError as err:
        print(f"Validation error: {err.messages}")
        return jsonify({'error': err.messages}), 400
    except Exception as e:
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
@token_required
def delete_contact(current_user, contact_id):
    """
    Delete a contact
    """
    print(f"=== DELETE CONTACT {contact_id} ENDPOINT CALLED ===")
    print(f"User: {current_user.email}")
    
    try:
        # Find contact
        contact = Contact.query.filter_by(id=contact_id, user_id=current_user.id).first()
        if not contact:
            print(f"Contact {contact_id} not found")
            return jsonify({'error': 'Contact not found'}), 404
            
        # Delete contact
        db.session.delete(contact)
        db.session.commit()
        
        print(f"Contact {contact_id} deleted successfully")
        return jsonify({
            'message': 'Contact deleted successfully'
        }), 200
        
    except Exception as e:
        print(f"Exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500