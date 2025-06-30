from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError

from models import db, Post, PostLikes
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
            'full_name': user.full_name,
            'desc': user.desc
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
    new_desc = data.get('desc')

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
    if new_desc:
        user.desc = new_desc

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
            'full_name': user.full_name,
            'desc': user.desc
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
            db.session.query(User.id, User.username, User.full_name)
            .join(Follow, Follow.following_id == User.id)  # 將following id和user id做連結
            .filter(Follow.follower_id == user_id)
        )
        following_users = query.paginate(page=page, per_page=limit, error_out=False)

        data = [{'id': user_id, 'username': username, 'full_name': full_name} for user_id, username, full_name in
                following_users]

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
            db.session.query(User.id, User.username, User.full_name)
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.following_id == user_id)
        )

        followers = query.paginate(page=page, per_page=limit, error_out=False)

        data = [{'id': uid, 'username': uname, 'full_name': full_name} for uid, uname, full_name in followers]

        return jsonify({
            'status': 'success',
            'page': page,
            'per_page': limit,
            'total': query.count(),
            'data': data
        }), 200

    except SQLAlchemyError:
        return jsonify({'status': 'error', 'message': 'Database error.'}), 500


def get_user_posts_controller(user_id):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid page or limit'}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User does not exist'}), 404

    posts_query = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=limit, error_out=False)

    current_user_id = get_jwt_identity()
    liked_post_ids = set()
    if current_user_id:
        post_ids = [post.id for post in posts.items]
        liked = PostLikes.query.filter(
            PostLikes.user_id == current_user_id,
            PostLikes.post_id.in_(post_ids)
        ).all()
        liked_post_ids = {like.post_id for like in liked}

    return jsonify({
        'status': 'success',
        'data': {
            'page': page,
            'total_post': posts.total,
            'posts': [
                {
                    'id': post.id,
                    'user_id': post.user_id,
                    'username': post.user.username,
                    'content': post.content,
                    'created_at': post.created_at.isoformat(),
                    'likes': len(post.likes),
                    'is_liked': post.id in liked_post_ids,
                    'comment_count': len(post.comments)
                } for post in posts.items
            ]
        }
    }), 200


def get_follow_stats_controller(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User does not exist'}), 404

    followers_count = Follow.query.filter_by(following_id=user_id).count()  # 誰追蹤我
    following_count = Follow.query.filter_by(follower_id=user_id).count()  # 我追蹤誰

    return jsonify({
        'status': 'success',
        'data': {
            'followers': followers_count,
            'following': following_count
        }
    }), 200


def is_following_user_controller(target_user_id):
    current_user_id = int(get_jwt_identity())

    if current_user_id == target_user_id:
        return jsonify({"status": "success", 'data': {"is_followed": False}}), 200

    is_following = Follow.query.filter_by(
        follower_id=current_user_id, following_id=target_user_id
    ).first()

    return jsonify({
        "status": "success",
        'data': {"is_followed": bool(is_following)}

    }), 200
