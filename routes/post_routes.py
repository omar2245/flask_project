from pathlib import Path

from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.post_controller import (
    create_post_controller,
    get_all_posts_controller,
    get_post_detail_controller,
    update_post_controller,
    delete_post_controller,
    get_post_comment_controller,
    like_post_controller,
    unlike_post_controller,
    get_post_likes_list_controller
)

post_bp = Blueprint('post', __name__, url_prefix='/api/v1/posts')
SWAGGER_DIR = Path(__file__).resolve().parents[1] / 'docs' / 'swagger' / 'posts'


def swagger_file(filename):
    return str(SWAGGER_DIR / filename)


@post_bp.route('', methods=['POST'])
@swag_from(swagger_file('create_post.yml'))
@jwt_required()
def create_post():
    return create_post_controller()


@post_bp.route('', methods=['GET'])
@swag_from(swagger_file('get_posts.yml'))
def get_all_post():
    return get_all_posts_controller()


@post_bp.route('/<int:post_id>', methods=['GET'])
@swag_from(swagger_file('get_post_detail.yml'))
def get_post_detail(post_id):
    return get_post_detail_controller(post_id)


@post_bp.route('/<int:post_id>', methods=['PUT'])
@swag_from(swagger_file('update_post.yml'))
@jwt_required()
def update_post(post_id):
    return update_post_controller(post_id)


@post_bp.route('/<int:post_id>', methods=['DELETE'])
@swag_from(swagger_file('delete_post.yml'))
@jwt_required()
def delete_post(post_id):
    return delete_post_controller(post_id)


@post_bp.route('/<int:post_id>/comments', methods=['GET'])
@swag_from(swagger_file('get_post_comments.yml'))
def get_post_comment(post_id):
    return get_post_comment_controller(post_id)


@post_bp.route('/<int:post_id>/like', methods=['POST'])
@swag_from(swagger_file('like_post.yml'))
@jwt_required()
def like_post(post_id):
    return like_post_controller(post_id)


@post_bp.route('/<int:post_id>/unlike', methods=['DELETE'])
@swag_from(swagger_file('unlike_post.yml'))
@jwt_required()
def unlike_post(post_id):
    return unlike_post_controller(post_id)


@post_bp.route('/<int:post_id>/like', methods=['GET'])
@swag_from(swagger_file('get_post_likes.yml'))
@jwt_required()
def get_post_likes(post_id):
    return get_post_likes_list_controller(post_id)
