from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
import pdb

from src.database import User, db

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth');

# Register new user
@auth.post('/register')
def register():
  username = request.json['username']
  email = request.json['email']
  password = request.json['password']

  if len(password) < 6:
    return jsonify({'error': 'Password is too short'}), HTTP_400_BAD_REQUEST
  
  if len(username) < 3:
    return jsonify({'error': 'Username is too short'}), HTTP_400_BAD_REQUEST
  
  if not username.isalnum() or " " in username:
    return jsonify({'error': 'Username should be alphanumeric, also no spaces'}), HTTP_400_BAD_REQUEST
  
  if not validators.email(email):
    return jsonify({'error': 'Email is not valid'}), HTTP_400_BAD_REQUEST
  
  if User.query.filter_by(email=email).first() is not None:
    return jsonify({'error': 'User with this email already exists.'}), HTTP_409_CONFLICT
  
  if User.query.filter_by(username=username).first() is not None:
    return jsonify({'error': 'User with this username already exists.'}), HTTP_409_CONFLICT
  
  pwd_hash = generate_password_hash(password)

  user = User(username = username, password = pwd_hash, email = email)
  db.session.add(user)
  db.session.commit()
  
  return jsonify({
    'message' : 'User created',
    'user': {
      'username': username,
      'email': email
    }
    }), HTTP_201_CREATED

# Login new user
@auth.post('/login')
def login():
  email = request.json.get('email', '')
  password = request.json.get('password', '')

  user = User.query.filter_by(email = email).first()

  if(user):
    is_password_corect = check_password_hash(user.password, password)

    if is_password_corect:
      refresh = create_refresh_token(identity=user.id)
      access = create_access_token(identity=user.id)

      return jsonify({
        'user': {
          'refresh': refresh,
          'access': access,
          'username': user.username,
          'email': user.email
        }
      }), HTTP_200_OK
    
  return jsonify({
    'error': 'Wrong credentials.'
  }), HTTP_401_UNAUTHORIZED

# User profile
@auth.get('/me')
@jwt_required()
def me():
  user_id = get_jwt_identity()

  user = User.query.filter_by(id = user_id).first()

  return jsonify({
    'username': user.username,
    'email': user.email
  }), HTTP_200_OK

# Refresh token
@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_tokens():
  identity = get_jwt_identity()
  access = create_access_token(identity = identity)

  return jsonify({
    'access': access
  }), HTTP_200_OK