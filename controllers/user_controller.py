from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from models import db
from models.user import User


def get_me_controller():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 404

    return jsonify({
        'status': 'success',
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200


def update_me_controller():
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found!'}), 404

    data = request.json or {}
    new_username = data.get('username')
    new_email = data.get('email')

    if new_username and User.query.filter(User.username == new_username, User.id != user_id).first():
        return jsonify({'status': 'error', 'message': 'Username has been used'}), 400

    if new_email and User.query.filter(User.email == new_email, User.id != user_id).first():
        return jsonify({'status': 'error', 'message': 'Email has been used'}), 400

    if new_username:
        user.username = new_username
    if new_email:
        user.email = new_email

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Update Successfully'}), 200


def get_user_controller(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({
            'status': 'error',
            'message': 'User not found!'
        }), 404

    return jsonify({
        'status': 'success',
        'data': {
            'id': user.id,
            'username': user.username}
    })
