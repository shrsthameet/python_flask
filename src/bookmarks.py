from flask import Blueprint, request, jsonify
from src.constants.http_status_code import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
import validators
from flask_jwt_extended import get_jwt_identity, jwt_required

from src.database import Bookmark, db

bookmarks = Blueprint('bookmarks', __name__, url_prefix='/api/v1/bookmarks');

# Create new book and get all bookamrks created by a current user
@bookmarks.route('/', methods = ['POST', 'GET'])
@jwt_required()
def handle_bookmarks():
  current_user = get_jwt_identity()
  if request.method == 'POST':
    body = request.get_json().get('body', '')
    url = request.get_json().get('url', '')

    if not validators.url(url):
      return jsonify({'error': 'Enter a valid url.'}), HTTP_400_BAD_REQUEST
    
    if Bookmark.query.filter_by(url = url).first():
      return jsonify({
        'error': 'URL already exists.'
      }), HTTP_409_CONFLICT
    
    bookmark = Bookmark(url = url, body = body, user_id = current_user)
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
      'id': bookmark.id,
      'url': bookmark.url,
      'short_url': bookmark.short_url,
      'visit': bookmark.visits,
      'body': bookmark.body,
      'created_at': bookmark.created_at,
      'updated_at': bookmark.updated_at
    }), HTTP_201_CREATED
  
  if request.method == 'GET':

    page = request.args.get('page', 1, type = int)
    per_page = request.args.get('per_page', 5, type = int) 

    bookmarks = Bookmark.query.filter_by(user_id = current_user).paginate(page = page, per_page = per_page)

    data = []

    for bookmark in bookmarks:
      data.append({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at
      })

    meta = {
      'page': bookmarks.page,
      'pages': bookmarks.pages,
      'total_count': bookmarks.total,
      'prev_page': bookmarks.prev_num,
      'next_page': bookmarks.next_num,
      'has_next': bookmarks.has_next,
      'has_prev': bookmarks.has_prev
    }

    return jsonify({
      'data': data,
      'meta': meta
    }), HTTP_200_OK

# Get one bookmark of a current user
@bookmarks.get('/<int:id>')
@jwt_required()
def get_bookmark(id):
  current_user = get_jwt_identity()

  bookmark = Bookmark.query.filter_by(user_id = current_user, id = id).first()

  if not bookmark:
    return jsonify({
      'error': 'Item with this id not found.'
    }), HTTP_404_NOT_FOUND
  
  return jsonify({
    'id': bookmark.id,
    'url': bookmark.url,
    'short_url': bookmark.short_url,
    'visit': bookmark.visits,
    'body': bookmark.body,
    'created_at': bookmark.created_at,
    'updated_at': bookmark.updated_at
  }), HTTP_200_OK

# Update bookmark of a current user
@bookmarks.put('/<int:id>')
@bookmarks.patch('/<int:id>')
@jwt_required()
def update_bookmark(id):
  current_user = get_jwt_identity()

  bookmark = Bookmark.query.filter_by(user_id = current_user, id = id).first()

  if not bookmark:
    return jsonify({
      'error': 'Item with this id not found.'
    }), HTTP_404_NOT_FOUND
  
  body = request.get_json().get('body', '')
  url = request.get_json().get('url', '')
  
  if not validators.url(url):
      return jsonify({'error': 'Enter a valid url.'}), HTTP_400_BAD_REQUEST
    
  if Bookmark.query.filter_by(url = url).first():
    return jsonify({
      'error': 'URL already exists.'
    }), HTTP_409_CONFLICT
  
  bookmark.url = url
  bookmark.body = body

  db.session.commit()

  return jsonify({
      'id': bookmark.id,
      'url': bookmark.url,
      'short_url': bookmark.short_url,
      'visit': bookmark.visits,
      'body': bookmark.body,
      'created_at': bookmark.created_at,
      'updated_at': bookmark.updated_at
  }), HTTP_200_OK

# Update bookmark of a current user
@bookmarks.delete('/<int:id>')
@jwt_required()
def delete_bookmark(id):
  current_user = get_jwt_identity()

  bookmark = Bookmark.query.filter_by(user_id = current_user, id = id).first()

  if not bookmark:
    return jsonify({
      'error': 'Item with this id not found.'
    }), HTTP_404_NOT_FOUND

  db.session.delete(bookmark)
  db.session.commit()

  return jsonify({}), HTTP_204_NO_CONTENT



