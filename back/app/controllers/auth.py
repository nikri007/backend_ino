from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
import json
import traceback
from app import db
from app.models.user import User, UserSchema
from app.utils.auth import token_required, generate_token
from app.utils.validators import save_image, validate_date

auth_bp = Blueprint('auth', __name__)
user_schema = UserSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User Registration endpoint
    """
    print("=== REGISTER ENDPOINT CALLED ===")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    # Check if request is multipart (with profile picture) or regular JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Handle multipart form data
        print("Processing multipart form data")
        try:
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
            
            print(f"Form data: {data}")
            
            # Validate date of birth
            date_of_birth = validate_date(data['date_of_birth'])
            if not date_of_birth:
                return jsonify({'error': 'Invalid date format for date_of_birth'}), 400
            
            data['date_of_birth'] = date_of_birth
            
            # Validate user data
            user_data = user_schema.load(data)
            
            # Create new user
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                date_of_birth=user_data['date_of_birth'],
                gender=user_data['gender'],
                address=user_data['address']
            )
            
            # Set password (this will hash it)
            new_user.password = user_data['password']
            
            # Set phone numbers
            new_user.set_phone_numbers(user_data['phone_numbers'])
            
            # Save profile picture if provided
            if 'profile_picture' in request.files:
                profile_pic = request.files['profile_picture']
                if profile_pic.filename:
                    filename = save_image(profile_pic)
                    if filename:
                        new_user.profile_picture = filename
            
            # Save user to database
            db.session.add(new_user)
            db.session.commit()
            
            # Generate auth token
            token = generate_token(new_user.id)
            
            # Prepare response
            response_data = user_schema.dump(new_user)
            response_data['token'] = token
            
            print("Registration successful")
            return jsonify({
                'message': 'User registered successfully',
                'user': response_data,
                'token': token
            }), 201
            
        except ValidationError as err:
            print(f"Validation error: {err.messages}")
            return jsonify({'error': err.messages}), 400
        except Exception as e:
            print(f"Exception: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    else:
        # Handle JSON data
        print("Processing JSON data")
        try:
            # Get the post data
            post_data = request.get_json()
            print(f"JSON data: {post_data}")
            
            if not post_data:
                print("No input data provided")
                return jsonify({'error': 'No input data provided'}), 400
                
            # Validate date of birth
            if 'date_of_birth' in post_data:
                date_of_birth = validate_date(post_data['date_of_birth'])
                if not date_of_birth:
                    return jsonify({'error': 'Invalid date format for date_of_birth'}), 400
                post_data['date_of_birth'] = date_of_birth
                
            # Validate and deserialize input
            user_data = user_schema.load(post_data)
            
            # Create new user
            new_user = User(
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                date_of_birth=user_data['date_of_birth'],
                gender=user_data['gender'],
                address=user_data['address']
            )
            
            # Set password (this will hash it)
            new_user.password = user_data['password']
            
            # Set phone numbers
            new_user.set_phone_numbers(user_data['phone_numbers'])
            
            # Save user to database
            db.session.add(new_user)
            db.session.commit()
            
            # Generate auth token
            token = generate_token(new_user.id)
            
            # Prepare response
            response_data = user_schema.dump(new_user)
            
            print("Registration successful")
            return jsonify({
                'message': 'User registered successfully',
                'user': response_data,
                'token': token
            }), 201
            
        except ValidationError as err:
            print(f"Validation error: {err.messages}")
            return jsonify({'error': err.messages}), 400
        except Exception as e:
            print(f"Exception: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User Login endpoint
    """
    print("=== LOGIN ENDPOINT CALLED ===")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    try:
        # Get post data
        post_data = request.get_json()
        print(f"Login data: {post_data}")
        
        if not post_data:
            print("No input data provided")
            return jsonify({'error': 'No input data provided'}), 400
            
        email = post_data.get('email')
        password = post_data.get('password')
        
        if not email or not password:
            print("Email or password missing")
            return jsonify({'error': 'Email and password are required'}), 400
            
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            print(f"User not found for email: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Check password
        if not user.check_password(password):
            print("Invalid password")
            return jsonify({'error': 'Invalid email or password'}), 401
            
        # Generate auth token
        token = generate_token(user.id)
        
        # Prepare response
        response_data = user_schema.dump(user)
        
        print("Login successful")
        return jsonify({
            'message': 'Successfully logged in',
            'user': response_data,
            'token': token
        }), 200
            
    except Exception as e:
        print(f"Login exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/test-token', methods=['GET'])
@token_required
def test_token(current_user):
    """
    Test token validity endpoint
    """
    print("=== TEST TOKEN ENDPOINT CALLED ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"User: {current_user.email}")
    
    return jsonify({
        'message': 'Token is valid',
        'user': user_schema.dump(current_user)
    }), 200