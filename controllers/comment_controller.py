from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from models import Comment, Post, CommentLike, User
from models import db


def create_comment_controller():
    data = request.json
    post_id = int(data.get('post_id'))
    user_id = int(get_jwt_identity())
    content = data.get('content')

    if not db.session.get(Post, post_id):
        return jsonify({'status': 'error', 'message': 'post does not exist'}), 404

    if not content or len(content.strip()) == 0:
        return jsonify({'status': 'error', 'message': 'content is empty'}), 400

    new_comment = Comment(user_id=user_id, post_id=post_id, content=content)
    db.session.add(new_comment)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'status': 'success',
        'data': {
            'id': new_comment.id,
            'user_id': new_comment.user_id,
            'post_id': new_comment.post_id,
            'content': new_comment.content,
            'created_at': new_comment.created_at.isoformat()
        }}), 201


def update_comment_controller(comment_id):
    user_id = int(get_jwt_identity())
    comment = db.session.get(Comment, comment_id)
    data = request.json
    content = data.get('content')

    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment does not exist'}), 404

    if user_id != int(comment.user_id):
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    if not content or len(content.strip()) == 0:
        return jsonify({'status': 'error', 'message': 'Content is required'}), 400

    comment.content = content

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'status': 'success',
        'message': 'Update comment successfully',
        'data': {
            'id': comment.id,
            'user_id': comment.user_id,
            'post_id': comment.post_id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat()
        }
    }), 200


def delete_comment_controller(comment_id):
    user_id = int(get_jwt_identity())
    comment = db.session.get(Comment, comment_id)

    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment does not exist'}), 404

    if user_id != int(comment.user_id):
        return jsonify({'status': 'error', 'message': 'Permission denied'}), 403

    db.session.delete(comment)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Delete comment successfully.'}), 200


def like_comment_controller(comment_id):
    user_id = int(get_jwt_identity())
    comment = db.session.get(Comment, comment_id)
    is_liked = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()

    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment does not exist.'}), 404
    if is_liked:
        return jsonify({'status': 'error', 'message': 'Already liked'}), 400

    like = CommentLike(user_id=user_id, comment_id=comment_id)
    db.session.add(like)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Like comment successfully.'}), 200


def unlike_comment_controller(comment_id):
    user_id = int(get_jwt_identity())
    comment = db.session.get(Comment, comment_id)
    like = CommentLike.query.filter_by(user_id=user_id, comment_id=comment_id).first()

    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment does not exist.'}), 404

    if not like:
        return jsonify({'status': 'error', 'message': 'You have not liked this yet'}), 400

    db.session.delete(like)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Unlike comment successfully.'}), 200


def get_comment_like_list_controller(comment_id):
    comment = db.session.get(Comment, comment_id)
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid post id or page or limit'}), 400

    if not comment:
        return jsonify({'status': 'error', 'message': 'Comment does not exist.'}), 404

    like_query = CommentLike.query.filter_by(comment_id=comment_id).join(User)
    like_lists = like_query.paginate(page=page, per_page=limit, error_out=False)

    if page > like_lists.pages:
        return jsonify({
            'status': 'error',
            'message': f'Page {page} exceeds total pages {like_lists.pages}.'
        }), 400
    
    return jsonify({
        'status': 'success',
        'page': page,
        'total': like_lists.total,
        'data': [
            {
                'user_id': like.user.id,
                'username': like.user.username,
                'full_name': like.user.full_name
            } for like in like_lists
        ]
    })
