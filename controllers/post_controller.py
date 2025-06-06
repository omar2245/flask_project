from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import Post, db


def get_post():
    try:
        page = int(request.args.get('page', 1))
        offset = int(request.args.get('offset', 10))
    except ValueError:
        return jsonify({'error': 'Invalid page or limit'}), 400

    posts_query = Post.query.order_by(Post.created_at.desc())
    posts = posts_query.paginate(page=page, per_page=offset, error_out=False)

    return jsonify({
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
    }), 200


@jwt_required()
def create_post():
    user_id = get_jwt_identity()
    data = request.json
    content = data.get('content')

    if request.method == 'POST':
        if not content or len(content.strip()) == 0:
            return jsonify({'error': '請輸入文字內容'}), 400

        new_post = Post(user_id=user_id, content=content)
        db.session.add(new_post)
        db.session.commit()

        return jsonify({'msg': 'create post successfully.'}), 200

    if not content or len(content.strip()) == 0:
        return jsonify({'error': '請輸入文字內容'}), 400

    new_post = Post(user_id=user_id, content=content)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'msg': 'create post successfully.'}), 200
