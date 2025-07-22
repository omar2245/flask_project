import cloudinary.uploader
from PIL import Image
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from sqlalchemy import func

from models import Post, db, Comment, PostLikes, CommentLikes, User
from models.post import PostImage

excerpt_length = 100


def create_post_controller():
    user_id = get_jwt_identity()
    content = request.form.get('content')

    if not content or len(content.strip()) == 0:
        return jsonify({
            'status': 'error',
            'message': 'content is empty'
        }), 400

    # 檢查圖片大小和格式
    image_files = request.files.getlist('images')
    if image_files:
        # 限制最多 2 張
        if len(image_files) > 2:
            return jsonify({
                'status': 'error',
                'message': '最多只能上傳 2 張圖片'
            }), 400

        # 驗證每一張圖片格式是不是圖片
        for idx, image_file in enumerate(image_files):
            if not is_image(image_file):
                return jsonify({
                    'status': 'error',
                    'message': f'第 {idx + 1} 張檔案不是有效圖片格式'
                }), 400
    # 處理圖片
    try:
        new_post = Post(user_id=user_id, content=content)
        db.session.add(new_post)
        db.session.flush()

        image_urls = []  # 儲存上傳完成的image url
        # 上傳圖片
        for idx, image_file in enumerate(image_files):
            if image_file and image_file.filename != '':
                result = cloudinary.uploader.upload(
                    image_file,
                    folder="posts",
                    public_id=f"post_{new_post.id}_{idx}",
                    transformation=[{"width": 500, "height": 500, "crop": "limit"}],
                )
                image_urls.append(result['secure_url'])

        for url in image_urls:
            post_image = PostImage(post_id=new_post.id, image_url=url)
            db.session.add(post_image)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Failed to create post or upload images',
            'details': str(e)
        }), 500

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

    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)

    # 超過頁數處理
    if page > posts.pages:
        return jsonify({
            'status': 'error',
            'message': f'Page {page} exceeds total pages {posts.pages}.'
        }), 400

    # 取得目前分頁中的所有貼文 ID，後續用來批量查詢讚和留言數、是否按讚
    post_ids = [post.id for post in posts.items]

    # 若有登入，查詢使用者對這批貼文中哪些有按讚
    liked_post_ids = set()
    if user_id:
        user_liked_posts = PostLikes.query.filter(
            PostLikes.user_id == user_id,
            PostLikes.post_id.in_(post_ids)
        ).all()
        liked_post_ids = set(pl.post_id for pl in user_liked_posts)

    # 批量查詢每篇貼文的按讚數，回傳成 dict {post_id: likes_count}
    # 量大需要用其他方法
    likes_counts = dict(
        # SELECT post_id, count(user_id) FROM post_likes
        db.session.query(PostLikes.post_id, func.count(PostLikes.user_id))
        .filter(PostLikes.post_id.in_(post_ids))  # WHERE post_id in (1, 2, 3,...)
        .group_by(PostLikes.post_id)  # GROUP BY post_id
        .all()
    )  # 把tuple轉dict方便下面跑迴圈對應post_id使用

    comments_counts = dict(
        db.session.query(Comment.post_id, func.count(Comment.id))
        .filter(Comment.post_id.in_(post_ids))
        .group_by(Comment.post_id)
        .all()
    )

    result_posts = []
    for post in posts.items:
        content_excerpt = post.content_excerpt
        if len(content_excerpt) == post.excerpt_length:
            content_excerpt += "..."

        result_posts.append({
            'id': post.id,
            'user_id': post.user_id,
            'content': content_excerpt,
            'created_at': post.created_at.isoformat(),
            'username': post.user.username,
            'avatar': post.user.avatar,
            'images': [img.image_url for img in post.images],
            'likes': likes_counts.get(post.id, 0),
            'is_liked': post.id in liked_post_ids,
            'comment_count': comments_counts.get(post.id, 0),
        })

    return jsonify({
        'status': 'success',
        'data': {
            'page': page,
            'per_page': limit,
            'total_post': posts.total,
            'posts': result_posts
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
                'username': post.user.username,
                'avatar': post.user.avatar,
                'likes': len(post.likes),
                'images': [img.image_url for img in post.images],
                'is_liked': (PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()) is not None,
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

    # 查詢被按讚過的comment
    like_comment_ids = set()
    if user_id:
        comment_ids = [comment.id for comment in comments]

        user_liked_comments = CommentLikes.query.filter(
            CommentLikes.user_id == user_id,
            CommentLikes.comment_id.in_(comment_ids)
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
                    'username': comment.user.username,
                    'avatar': comment.user.avatar,
                    'is_liked': comment.id in like_comment_ids,
                    'created_at': comment.created_at.isoformat()
                } for comment in comments.items
            ]
        }
    })


def like_post_controller(post_id):
    user_id = int(get_jwt_identity())
    post = db.session.get(Post, post_id)
    already_liked = PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()

    if not post:
        return jsonify({'status': 'error', 'message': 'post does not exist.'}), 404

    if already_liked:
        return jsonify({'status': 'error', 'message': 'Already liked'}), 400

    like = PostLikes(user_id=user_id, post_id=post_id)
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
    like = PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()

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

    like_query = PostLikes.query.filter_by(post_id=post_id).join(User)
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
                'full_name': like.user.full_name,
                'avatar': like.user.avatar
            } for like in like_lists
        ]
    }), 200


def is_image(file_storage):
    try:
        image = Image.open(file_storage.stream)
        image.verify()  # 驗證圖片有效性
        file_storage.stream.seek(0)  # 驗證後回復指標
        return True
    except (TypeError, OSError):
        return False
