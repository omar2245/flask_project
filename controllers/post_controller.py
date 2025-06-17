from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from models import Post, db, Comment, PostLike, CommentLike, User


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
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'status': 'success',
        'msg': 'create post successfully.'
    }), 201


def get_all_posts_controller():
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()

    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid page or limit'
        }), 400

    posts_query = Post.query.order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=limit, error_out=False)

    # 超過頁數處理
    if page > posts.pages:
        return jsonify({
            'status': 'error',
            'message': f'Page {page} exceeds total pages {posts.pages}.'
        }), 400

    # 批量查按過讚的post
    liked_post_ids = set()
    if user_id:
        post_ids = [post.id for post in posts]  # 目前貼文所有的post id

        # 把pagination後user按讚過的貼文過濾出來
        # content在SQL語法就切substring
        user_liked_posts = PostLike.query.filter(
            PostLike.user_id == user_id,
            PostLike.post_id.in_(post_ids)
        ).all()
        liked_post_ids = set(post.post_id for post in user_liked_posts)

    return jsonify({
        'status': 'success',
        'data': {
            'page': page,
            'per_page': limit,
            'total_post': posts.total,
            'posts': [
                {
                    'id': post.id,
                    'user_id': post.user_id,
                    'content': post.content,  # 不用全部吐回去, 在SQL語法就切 substring
                    'created_at': post.created_at.isoformat(),
                    'likes': len(post.likes),
                    'is_liked': post.id in liked_post_ids,
                    'comment_count': Comment.query.filter_by(post_id=post.id).count()
                } for post in posts.items
            ]
        }
    }), 200


def get_post_detail_controller(post_id):
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()
    post = db.session.get(Post, post_id)

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
                'content': post.content,
                'likes': len(post.likes),
                'is_liked': (PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()) is not None,
                'comment_count': Comment.query.filter_by(post_id=post.id).count()
            }
        }
    }), 200


def update_post_controller(post_id):
    data = request.json
    content = data.get('content')
    user_id = int(get_jwt_identity())
    post = db.session.get(Post, post_id)

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
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({
        'status': 'success',
        'message': 'update post successfully.'
    }), 200


def delete_post_controller(post_id):
    user_id = int(get_jwt_identity())
    post = db.session.get(Post, post_id)

    if not post:
        return jsonify({'status': 'error', 'message': 'post does not exist.'}), 404

    if post.user_id != user_id:
        return jsonify({'status': 'error', 'message': 'Permission denied.'}), 403

    db.session.delete(post)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'delete post successfully.'}), 200


def get_post_comment_controller(post_id):
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()

    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid post id or page or limit'}), 400

    if not post_id:
        return jsonify({'status': 'error', 'message': 'Post id is required'}), 400

    if not db.session.get(Post, post_id):
        return jsonify({'status': 'error', 'message': 'Post does not exist'}), 400

    comments_query = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.desc())
    comments = comments_query.paginate(page=page, per_page=limit, error_out=False)

    if page > comments.pages:
        return jsonify({
            'status': 'error',
            'message': f'Page {page} exceeds total pages {comments.pages}.'
        }), 400

    # 查詢被按讚過的comment
    like_comment_ids = set()
    if user_id:
        comment_ids = [comment.id for comment in comments]

        user_liked_comments = CommentLike.query.filter(
            CommentLike.user_id == user_id,
            CommentLike.comment_id.in_(comment_ids)
        ).all()
        like_comment_ids = set(comment.comment_id for comment in user_liked_comments)

    print(like_comment_ids)
    return jsonify({
        'status': 'success',
        'data': {
            'page': page,
            'per_page': limit,
            'total': comments.total,
            'comments': [
                {
                    'id': comment.id,
                    'user_id': comment.user_id,
                    'content': comment.content,
                    'likes': len(comment.likes),
                    'is_liked': comment.id in like_comment_ids,
                    'created_at': comment.created_at.isoformat()
                } for comment in comments.items
            ]
        }
    })


def like_post_controller(post_id):
    user_id = int(get_jwt_identity())
    post = db.session.get(Post, post_id)
    already_liked = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()

    if not post:
        return jsonify({'status': 'error', 'message': 'post does not exist.'}), 404

    if already_liked:
        return jsonify({'status': 'error', 'message': 'Already liked'}), 400

    like = PostLike(user_id=user_id, post_id=post_id)
    db.session.add(like)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Like post successfully.'}), 200


def unlike_post_controller(post_id):
    user_id = int(get_jwt_identity())
    post = db.session.get(Post, post_id)
    like = PostLike.query.filter_by(user_id=user_id, post_id=post_id).first()

    if not post:
        return jsonify({'status': 'error', 'message': 'post does not exist.'}), 404

    if not like:
        return jsonify({'status': 'error', 'message': 'You have not liked this yet'}), 400

    db.session.delete(like)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error', 'details': str(e)}), 500

    return jsonify({'status': 'success', 'message': 'Unlike post successfully.'}), 200


def get_post_likes_list_controller(post_id):
    post = db.session.get(Post, post_id)
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Invalid post id or page or limit'}), 400

    if not post:
        return jsonify({'status': 'error', 'message': 'Post does not exist'}), 404

    like_query = PostLike.query.filter_by(post_id=post_id).join(User)
    like_lists = like_query.paginate(page=page, per_page=limit, error_out=False)
    
    if page > like_lists.pages:
        return jsonify({
            'status': 'error',
            'message': f'Page {page} exceeds total pages {like_lists.pages}.'
        }), 400

    return jsonify({
        'status': 'success',
        'page': page,
        'per_page': limit,
        'total': like_lists.total,
        'data': [
            {
                'user_id': like.user.id,
                'username': like.user.username,
                'full_name': like.user.full_name
            } for like in like_lists
        ]
    }), 200
