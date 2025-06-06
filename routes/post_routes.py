from flask import Blueprint, jsonify, request

from controllers.post_controller import create_post, get_post

post_bp = Blueprint('post', __name__, url_prefix='/api/v1/posts')


@post_bp.route('', methods=['GET', 'POST'])
def post():
    if request.method == 'GET':
        return get_post();
    elif request.method == 'POST':
        return create_post()

    return jsonify({'error': 'Method not allowed'}), 405
