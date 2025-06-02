import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, create_refresh_token, \
    set_refresh_cookies, unset_jwt_cookies
from sqlalchemy import or_

from models import db
from models.user import User
from routes import bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    # username 格式
    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'Username must be 3-20 characters'}), 400
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        return jsonify({'error': 'Username can only contain letters, numbers and _'}), 400

    # email 格式
    if not re.match(r'^\S+@\S+\.\S+$', email):
        return jsonify({'error': 'Invalid email format'}), 400

    # 密碼格式
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return jsonify({'error': 'Password must contain both letters and numbers'}), 400

    # 確認username 和 email是否重複
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'username or email are already exists'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter(or_(User.username == username, User.email == username)).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'The username or password is invalid'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    resp = jsonify({'access_token': access_token})
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({'access_token': new_access_token}), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    resp = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(resp)
    return resp, 200
