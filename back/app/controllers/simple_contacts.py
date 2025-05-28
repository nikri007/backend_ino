from flask import Blueprint, request, jsonify
import json
from app import db
from app.models.contact import Contact
from app.models.user import User

simple_contacts_bp = Blueprint('simple_contacts', __name__)

# Helper function to get user from token
def get_user_from_token(request):
    """Simple function to get user from token for testing"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None, 'Authorization header is missing'
        
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = auth_header
        
    # For our simplified API, token is in format "test_token_{user_id}"
    if token.startswith('test_token_'):
        try:
            user_id = int(token.split('_')[2])
            user = User.query.get(user_id)
            if not user:
                return None, 'User not found'
            return user, None
        except Exception as e:
            return None, str(e)
    
    return None, 'Invalid token format'

@simple_contacts_bp.route('/', methods=['POST'])
def create_contact():
    """Create a new contact"""
    print("=== SIMPLE CREATE CONTACT ENDPOINT CALLED ===")
    
    # Authenticate user
    user, error = get_user_from_token(request)
    if not user:
        return jsonify({'error': error}), 401
    
    try:
        # Get post data
        post_data = request.get_json()
        if not post_data:
            return jsonify({'error': 'No input data provided'}), 400
            
        # Validate required fields
        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if field not in post_data or not post_data[field]:
                return jsonify({'error': f'Field {field} is required'}), 400
                
        # Create new contact
        new_contact = Contact(
            user_id=user.id,
            first_name=post_data['first_name'],
            last_name=post_data['last_name'],
            company=post_data.get('company'),
            address=post_data.get('address')
        )
        
        # Set phone numbers
        phone_numbers = post_data.get('phone_numbers', [])
        new_contact.set_phone_numbers(phone_numbers)
        
        # Save to database
        db.session.add(new_contact)
        db.session.commit()
        
        # Return response
        return jsonify({
            'id': new_contact.id,
            'first_name': new_contact.first_name,
            'last_name': new_contact.last_name,
            'company': new_contact.company,
            'address': new_contact.address,
            'phone_numbers': new_contact.get_phone_numbers(),
            'created_at': new_contact.created_at.isoformat()
        }), 201
            
    except Exception as e:
        print(f"Error creating contact: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_contacts_bp.route('/', methods=['GET'])
def get_contacts():
    """Get all contacts with pagination and search"""
    print("=== SIMPLE GET CONTACTS ENDPOINT CALLED ===")
    
    # Authenticate user
    user, error = get_user_from_token(request)
    if not user:
        return jsonify({'error': error}), 401
    
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        # Get contacts for this user
        query = Contact.query.filter_by(user_id=user.id)
        
        # Apply search if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Contact.first_name.ilike(search_term),
                    Contact.last_name.ilike(search_term),
                    Contact.company.ilike(search_term),
                    Contact.address.ilike(search_term)
                )
            )
            
        # Apply pagination
        total = query.count()
        contacts = query.order_by(Contact.first_name, Contact.last_name).offset((page-1)*per_page).limit(per_page).all()
        
        # Prepare response
        pages = (total + per_page - 1) // per_page  # ceiling division
        
        contact_list = []
        for contact in contacts:
            contact_list.append({
                'id': contact.id,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
                'company': contact.company,
                'address': contact.address,
                'phone_numbers': contact.get_phone_numbers(),
                'created_at': contact.created_at.isoformat()
            })
            
        return jsonify({
            'contacts': contact_list,
            'total': total,
            'pages': pages,
            'page': page,
            'per_page': per_page
        }), 200
            
    except Exception as e:
        print(f"Error getting contacts: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_contacts_bp.route('/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get a specific contact by ID"""
    print(f"=== SIMPLE GET CONTACT {contact_id} ENDPOINT CALLED ===")
    
    # Authenticate user
    user, error = get_user_from_token(request)
    if not user:
        return jsonify({'error': error}), 401
    
    try:
        # Find contact
        contact = Contact.query.filter_by(id=contact_id, user_id=user.id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
            
        # Return contact details
        return jsonify({
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'company': contact.company,
            'address': contact.address,
            'phone_numbers': contact.get_phone_numbers(),
            'created_at': contact.created_at.isoformat(),
            'updated_at': contact.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error getting contact: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_contacts_bp.route('/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete a contact"""
    print(f"=== SIMPLE DELETE CONTACT {contact_id} ENDPOINT CALLED ===")
    
    # Authenticate user
    user, error = get_user_from_token(request)
    if not user:
        return jsonify({'error': error}), 401
    
    try:
        # Find contact
        contact = Contact.query.filter_by(id=contact_id, user_id=user.id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
            
        # Delete contact
        db.session.delete(contact)
        db.session.commit()
        
        return jsonify({
            'message': 'Contact deleted successfully'
        }), 200
        
    except Exception as e:
        print(f"Error deleting contact: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_contacts_bp.route('/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update an existing contact"""
    print(f"=== SIMPLE UPDATE CONTACT {contact_id} ENDPOINT CALLED ===")
    
    # Authenticate user
    user, error = get_user_from_token(request)
    if not user:
        return jsonify({'error': error}), 401
    
    try:
        # Find contact
        contact = Contact.query.filter_by(id=contact_id, user_id=user.id).first()
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
            
        # Get post data
        post_data = request.get_json()
        if not post_data:
            return jsonify({'error': 'No input data provided'}), 400
            
        # Validate required fields
        required_fields = ['first_name', 'last_name']
        for field in required_fields:
            if field not in post_data or not post_data[field]:
                return jsonify({'error': f'Field {field} is required'}), 400
                
        # Update contact
        contact.first_name = post_data['first_name']
        contact.last_name = post_data['last_name']
        contact.company = post_data.get('company')
        contact.address = post_data.get('address')
        
        # Update phone numbers
        if 'phone_numbers' in post_data:
            contact.set_phone_numbers(post_data['phone_numbers'])
        
        # Save changes
        db.session.commit()
        
        # Return updated contact
        return jsonify({
            'id': contact.id,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'company': contact.company,
            'address': contact.address,
            'phone_numbers': contact.get_phone_numbers(),
            'created_at': contact.created_at.isoformat(),
            'updated_at': contact.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error updating contact: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500