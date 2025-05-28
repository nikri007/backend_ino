from flask import Blueprint, request, jsonify
import json
from datetime import datetime
from app import db, bcrypt
from app.models.user import User

simple_auth_bp = Blueprint('simple_auth', __name__)

@simple_auth_bp.route('/register', methods=['POST'])
def register():
    """
    Simplified user registration endpoint
    """
    print("=== SIMPLE REGISTER ENDPOINT CALLED ===")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Get post data
        post_data = request.get_json()
        print(f"JSON data: {post_data}")
        
        if not post_data:
            return jsonify({'error': 'No input data provided'}), 400
        
        # Manual validation - just check required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 
                          'gender', 'phone_numbers', 'address']
        
        for field in required_fields:
            if field not in post_data or not post_data[field]:
                return jsonify({'error': f'Field {field} is required'}), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=post_data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Parse date of birth - accept multiple formats
        try:
            # Try directly as ISO format
            date_of_birth = datetime.strptime(post_data['date_of_birth'], '%Y-%m-%d').date()
        except ValueError:
            try:
                # Try MM-DD-YYYY format
                date_of_birth = datetime.strptime(post_data['date_of_birth'], '%m-%d-%Y').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create new user directly
        new_user = User(
            first_name=post_data['first_name'],
            last_name=post_data['last_name'],
            email=post_data['email'],
            date_of_birth=date_of_birth,
            gender=post_data['gender'],
            address=post_data['address']
        )
        
        # Set password (this will hash it)
        new_user.password = post_data['password']
        
        # Set phone numbers
        new_user.set_phone_numbers(post_data['phone_numbers'])
        
        # Save user to database
        db.session.add(new_user)
        db.session.commit()
        
        # Generate a simple token (just for testing)
        token = f"test_token_{new_user.id}"
        
        print("Registration successful")
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'id': new_user.id,
                'first_name': new_user.first_name,
                'last_name': new_user.last_name,
                'email': new_user.email
            },
            'token': token
        }), 201
            
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_auth_bp.route('/login', methods=['POST'])
def login():
    """
    Simplified user login endpoint
    """
    print("=== SIMPLE LOGIN ENDPOINT CALLED ===")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Get post data
        post_data = request.get_json()
        print(f"Login data: {post_data}")
        
        if not post_data:
            return jsonify({'error': 'No input data provided'}), 400
            
        email = post_data.get('email')
        password = post_data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
            
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Check password
        if not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Generate simple token for testing
        token = f"test_token_{user.id}"
        
        # Prepare response
        return jsonify({
            'message': 'Successfully logged in',
            'user': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            },
            'token': token
        }), 200
            
    except Exception as e:
        print(f"Login exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500