from flask import Blueprint, request, jsonify
import json
from datetime import datetime
from app import db, bcrypt
from app.models.user import User
from app.utils.validators import save_image

# Create the blueprint
simple_auth_bp = Blueprint('simple_auth', __name__)

@simple_auth_bp.route('/register', methods=['POST'])
def register():
    """
    Simplified user registration endpoint with profile picture support
    """
    print("=== SIMPLE REGISTER ENDPOINT CALLED ===")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Check if request is multipart (with profile picture) or regular JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle multipart form data (with profile picture)
            print("Processing multipart form data (with profile picture)")
            
            # Extract form data
            data = {
                'first_name': request.form.get('first_name'),
                'last_name': request.form.get('last_name'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'confirm_password': request.form.get('confirm_password'),
                'date_of_birth': request.form.get('date_of_birth'),
                'gender': request.form.get('gender'),
                'phone_numbers': json.loads(request.form.get('phone_numbers', '[]')),
                'address': request.form.get('address')
            }
            
            print(f"Form data received: {data}")
            
            # Manual validation for multipart form data
            required_fields = ['first_name', 'last_name', 'email', 'password', 
                             'confirm_password', 'date_of_birth', 'gender', 'address']
            
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'Field {field} is required'}), 400
            
            # Check password confirmation
            if data['password'] != data['confirm_password']:
                return jsonify({'error': 'Passwords must match'}), 400
            
            # Check if email already exists
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user:
                return jsonify({'error': 'Email address already registered'}), 400
            
            # Validate and parse date of birth
            try:
                if data['date_of_birth']:
                    # Handle YYYY-MM-DD format (from HTML date input)
                    date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                else:
                    return jsonify({'error': 'Date of birth is required'}), 400
            except ValueError as e:
                print(f"Date parsing error: {e}")
                return jsonify({'error': 'Invalid date format. Please use a valid date.'}), 400
            
            # Validate phone numbers
            phone_numbers = data.get('phone_numbers', [])
            if not phone_numbers or all(not phone.strip() for phone in phone_numbers):
                return jsonify({'error': 'At least one phone number is required'}), 400
            
            # Filter out empty phone numbers
            phone_numbers = [phone.strip() for phone in phone_numbers if phone.strip()]
            
            # Create new user directly
            new_user = User(
                first_name=data['first_name'].strip(),
                last_name=data['last_name'].strip(),
                email=data['email'].strip().lower(),
                date_of_birth=date_of_birth,
                gender=data['gender'],
                address=data['address'].strip()
            )
            
            # Set password (this will hash it)
            new_user.password = data['password']
            
            # Set phone numbers
            new_user.set_phone_numbers(phone_numbers)
            
            # Handle profile picture if provided
            if 'profile_picture' in request.files:
                profile_pic = request.files['profile_picture']
                if profile_pic and profile_pic.filename:
                    print(f"Processing profile picture: {profile_pic.filename}")
                    filename = save_image(profile_pic)
                    if filename:
                        new_user.profile_picture = filename
                        print(f"Profile picture saved as: {filename}")
                    else:
                        print("Profile picture save failed")
            
            # Save user to database
            db.session.add(new_user)
            db.session.commit()
            
            # Generate a simple token
            token = f"test_token_{new_user.id}"
            
            print("Registration successful with profile picture support")
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'id': new_user.id,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                    'email': new_user.email,
                    'profile_picture': new_user.profile_picture,
                    'date_of_birth': new_user.date_of_birth.isoformat() if new_user.date_of_birth else None,
                    'gender': new_user.gender,
                    'address': new_user.address,
                    'phone_numbers': new_user.get_phone_numbers()
                },
                'token': token
            }), 201
            
        else:
            # Handle JSON data (without profile picture)
            print("Processing JSON data")
            post_data = request.get_json()
            print(f"JSON data: {post_data}")
            
            if not post_data:
                return jsonify({'error': 'No input data provided'}), 400
            
            # Manual validation - check required fields
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
            
            # Generate a simple token
            token = f"test_token_{new_user.id}"
            
            print("Registration successful (JSON)")
            return jsonify({
                'message': 'User registered successfully',
                'user': {
                    'id': new_user.id,
                    'first_name': new_user.first_name,
                    'last_name': new_user.last_name,
                    'email': new_user.email,
                    'profile_picture': new_user.profile_picture,
                    'date_of_birth': new_user.date_of_birth.isoformat() if new_user.date_of_birth else None,
                    'gender': new_user.gender,
                    'address': new_user.address,
                    'phone_numbers': new_user.get_phone_numbers()
                },
                'token': token
            }), 201
            
    except json.JSONDecodeError as e:
        print(f"JSON decode error in phone numbers: {e}")
        return jsonify({'error': 'Invalid phone numbers format'}), 400
    except Exception as e:
        print(f"Exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_auth_bp.route('/login', methods=['POST'])
def login():
    """
    Simplified user login endpoint - NOW INCLUDES PROFILE PICTURE
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
        
        # Prepare COMPLETE response including profile picture
        user_data = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_picture': user.profile_picture,  # ← THIS WAS MISSING!
            'date_of_birth': user.date_of_birth.isoformat() if user.date_of_birth else None,
            'gender': user.gender,
            'address': user.address,
            'phone_numbers': user.get_phone_numbers()
        }
        
        print(f"Login successful for user: {user.email}")
        print(f"User has profile picture: {user.profile_picture is not None}")
        if user.profile_picture:
            print(f"Profile picture filename: {user.profile_picture}")
        
        return jsonify({
            'message': 'Successfully logged in',
            'user': user_data,
            'token': token
        }), 200
            
    except Exception as e:
        print(f"Login exception: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@simple_auth_bp.route('/test-token', methods=['GET'])
def test_token():
    """
    Simple token test endpoint
    """
    print("=== SIMPLE TEST TOKEN ENDPOINT CALLED ===")
    
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({'error': 'Authorization header is missing'}), 401
        
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
                return jsonify({'error': 'User not found'}), 401
            
            return jsonify({
                'message': 'Token is valid',
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'profile_picture': user.profile_picture  # Include profile picture in token test too
                }
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return jsonify({'error': 'Invalid token format'}), 401