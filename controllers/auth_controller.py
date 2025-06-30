import re

from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    unset_jwt_cookies, get_jwt_identity,
    jwt_required
)
from sqlalchemy import or_

from controllers import bcrypt
from models import db
from models.user import User


def register_controller():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'Username must be 3-20 characters'}), 400
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        return jsonify({'error': 'Username can only contain letters, numbers and _'}), 400
    if not re.match(r'^\S+@\S+\.\S+$', email):
        return jsonify({'error': 'Invalid email format'}), 400
    if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return jsonify({'error': 'Password must contain both letters and numbers'}), 400

    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({'error': 'Username or email already exists'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


def login_controller():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = User.query.filter(or_(User.username == username, User.email == username)).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    resp = jsonify({'access_token': access_token, 'refresh_token': refresh_token})
    return resp, 200


@jwt_required(refresh=True)
def refresh_controller():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_access_token}), 200


@jwt_required(refresh=True)
def logout_controller():
    resp = jsonify({'msg': 'Logout successful'})
    unset_jwt_cookies(resp)
    return resp, 200
