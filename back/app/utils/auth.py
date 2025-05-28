import jwt
import datetime
import traceback
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User

def generate_token(user_id):
    """
    Generate JWT token for authentication
    """
    try:
        # Generate a JWT token with expiration
        payload = {
            'exp': datetime.datetime.utcnow() + current_app.config['JWT_ACCESS_TOKEN_EXPIRES'],
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        return jwt.encode(
            payload,
            current_app.config['JWT_SECRET_KEY'],
            algorithm='HS256'
        )
    except Exception as e:
        print(f"Token generation error: {str(e)}")
        print(traceback.format_exc())
        return str(e)

def decode_token(auth_token):
    """
    Decode the JWT token
    """
    try:
        payload = jwt.decode(
            auth_token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload['sub']
    except jwt.ExpiredSignatureError:
        print("Token expired")
        return 'Token expired. Please log in again.'
    except jwt.InvalidTokenError:
        print("Invalid token")
        return 'Invalid token. Please log in again.'

def token_required(f):
    """
    Decorator for routes that require authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        print(f"Auth header: {auth_header}")
        
        if auth_header:
            # Check if token has Bearer prefix
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                print(f"Found Bearer token: {token[:10]}...")
            else:
                token = auth_header  # For backward compatibility
                print(f"Found raw token: {token[:10]}...")
                
        if not token:
            print("No token provided")
            return jsonify({
                'error': 'Token is missing'
            }), 401
            
        try:
            user_id = decode_token(token)
            # Check if token decoded to a string error message
            if isinstance(user_id, str):
                print(f"Token decode error: {user_id}")
                return jsonify({
                    'error': user_id
                }), 401
                
            # Get current user
            current_user = User.query.get(user_id)
            if not current_user:
                print(f"User not found for id: {user_id}")
                return jsonify({
                    'error': 'User not found'
                }), 401
                
            print(f"Authentication successful for user: {current_user.email}")
                
        except Exception as e:
            print(f"Authentication exception: {str(e)}")
            print(traceback.format_exc())
            return jsonify({
                'error': 'Invalid token'
            }), 401
            
        # Pass the current user to the route
        return f(current_user, *args, **kwargs)
        
    return decorated