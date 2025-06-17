from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from models import db
from models.follow import Follow
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
            'email': user.email,
            'full_name': user.full_name
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
    new_full_name = data.get('full_name')

    if new_username and User.query.filter(User.username == new_username, User.id != user_id).first():
        return jsonify({'status': 'error', 'message': 'Username has been used'}), 400

    if new_email and User.query.filter(User.email == new_email, User.id != user_id).first():
        return jsonify({'status': 'error', 'message': 'Email has been used'}), 400

    if new_username:
        user.username = new_username
    if new_email:
        user.email = new_email
    if new_full_name:
        user.full_name = new_full_name

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
            'username': user.username,
            'full_name': user.full_name
        }
    })


def follow_user_controller(user_id):
    follower_id = int(get_jwt_identity())

    if follower_id == user_id:
        return jsonify({'status': 'error', 'message': 'You cannot follow your self.'}), 400

    target_user = db.session.get(User, user_id)
    if not target_user:
        return jsonify({'status': 'error', 'message': 'User does not exist.'}), 404

    following = Follow.query.filter_by(follower_id=follower_id, following_id=user_id).first()
    if following:
        return jsonify({'status': 'error', 'message': 'Already followed.'}), 400

    follow = Follow(follower_id=follower_id, following_id=user_id)
    db.session.add(follow)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Follow successfully.'}), 201


def unfollow_user_controller(user_id):
    follower_id = int(get_jwt_identity())

    if follower_id == user_id:
        return jsonify({'status': 'error', 'message': 'You cannot follow your self.'}), 400

    target_user = db.session.get(User, user_id)
    if not target_user:
        return jsonify({'status': 'error', 'message': 'User does not exist.'}), 404

    following = Follow.query.filter_by(follower_id=follower_id, following_id=user_id).first()
    if not following:
        return jsonify({'status': 'error', 'message': 'You are not following the user.'}), 400

    db.session.delete(following)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Unfollow successfully.'}), 200


def get_following_user_controller(user_id):
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'status': 'error', 'message': 'User does not exist.'}), 404

        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('per_page', default=10, type=int)

        query = (
            db.session.query(User.id, User.username)
            .join(Follow, Follow.following_id == User.id)  # 將following id和user id做連結
            .filter(Follow.follower_id == user_id)
        )
        following_users = query.paginate(page=page, per_page=limit, error_out=False)

        if page > following_users.pages:
            return jsonify({
                'status': 'error',
                'message': f'Page {page} exceeds total pages {following_users.pages}.'
            }), 400

        data = [{'id': user_id, 'username': username} for user_id, username in following_users]

        return jsonify({
            'status': 'success',
            'page': page,
            'per_page': limit,
            'total': query.count(),
            'data': data
        }), 200

    except SQLAlchemyError:
        return jsonify({'status': 'error', 'message': 'Database error.'}), 500


def get_user_follower_controller(user_id):
    try:
        target_user = db.session.get(User, user_id)
        if not target_user:
            return jsonify({'status': 'error', 'message': 'User does not exist.'}), 404

        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('per_page', default=10, type=int)

        query = (
            db.session.query(User.id, User.username)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.following_id == user_id)
        )

        followers = query.paginate(page=page, per_page=limit, error_out=False)
        if page > followers.pages:
            return jsonify({
                'status': 'error',
                'message': f'Page {page} exceeds total pages {followers.pages}.'
            }), 400

        data = [{'id': uid, 'username': uname} for uid, uname in followers]

        return jsonify({
            'status': 'success',
            'page': page,
            'per_page': limit,
            'total': query.count(),
            'data': data
        }), 200

    except SQLAlchemyError:
        return jsonify({'status': 'error', 'message': 'Database error.'}), 500
