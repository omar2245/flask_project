from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from models import Post, db


def create_post_controller():
    user_id = get_jwt_identity()
    data = request.json
    content = data.get('content')

    if not content or len(content.strip()) == 0:
        return jsonify({
            'status': 'error',
            'message': 'content is empty'
        }), 400

    new_post = Post(user_id=user_id, content=content)
    db.session.add(new_post)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'details': str(e)
        }), 500

    return jsonify({
        'status': 'success',
        'msg': 'create post successfully.'
    }), 201


def get_all_posts_controller():
    try:
        page = int(request.args.get('page', 1))
        offset = int(request.args.get('offset', 10))
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid page or limit'
        }), 400

    posts_query = Post.query.order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=offset, error_out=False)

    return jsonify({
        'status': 'success',
        'data': {
            'page': page,
            'total_post': posts.total,
            'posts': [
                {
                    'id': post.id,
                    'user_id': post.user_id,
                    'content': post.content,
                    'created_at': post.created_at.isoformat()
                } for post in posts.items
            ]
        }
    }), 200


def get_post_detail_controller(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({
            'status': 'error',
            'message': 'post does not exist.'
        }), 404

    return jsonify({
        'status': 'success',
        'data': {
            'post': {
                'id': post.id,
                'user_id': post.user_id,
                'created_at': post.created_at.isoformat(),
                'content': post.content
            }
        }
    }), 200


def update_post_controller(post_id):
    data = request.json
    content = data.get('content')
    user_id = int(get_jwt_identity())
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({
            'status': 'error',
            'message': 'post does not exist.'
        }), 404

    if post.user_id != user_id:
        return jsonify({
            'status': 'error',
            'message': 'Permission denied.'
        }), 403

    if not content or len(content.strip()) == 0:
        return jsonify({
            'status': 'error',
            'message': 'content is required'
        }), 400

    post.content = content
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'details': str(e)}
        ), 500

    return jsonify({
        'status': 'success',
        'message': 'update post successfully.'
    }), 200


def delete_post_controller(post_id):
    user_id = int(get_jwt_identity())
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({
            'status': 'error',
            'message': 'post does not exist.'
        }), 404

    if post.user_id != user_id:
        return jsonify({
            'status': 'error',
            'message': 'Permission denied.'
        }), 403

    db.session.delete(post)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'details': str(e)
        }), 500

    return jsonify({
        'status': 'success',
        'message': 'delete post successfully.'
    }), 200
