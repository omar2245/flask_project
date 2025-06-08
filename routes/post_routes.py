from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.post_controller import create_post_controller, get_all_posts_controller, get_post_detail_controller, \
    update_post_controller, delete_post_controller, get_post_comment_controller, like_post_controller, \
    unlike_post_controller, get_post_likes_list_controller

post_bp = Blueprint('post', __name__, url_prefix='/api/v1/posts')


@post_bp.route('', methods=['POST'])
def create_post():
    return create_post_controller()


@post_bp.route('', methods=['GET'])
def get_all_post():
    return get_all_posts_controller()


@post_bp.route('/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    return get_post_detail_controller(post_id)


@post_bp.route('/<int:post_id>', methods=['PUT'])
@jwt_required()
def update_post(post_id):
    return update_post_controller(post_id)


@post_bp.route('/<int:post_id>', methods=['DELETE'])
@jwt_required()
def delete_post(post_id):
    return delete_post_controller(post_id)


# get post's comments
@post_bp.route('/<int:post_id>/comments', methods=['GET'])
def get_post_comment(post_id):
    return get_post_comment_controller(post_id)


@post_bp.route('/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    return like_post_controller(post_id)


@post_bp.route('/<int:post_id>/unlike', methods=['DELETE'])
@jwt_required()
def unlike_post(post_id):
    return unlike_post_controller(post_id)


@post_bp.route('/<int:post_id>/like', methods=['GET'])
@jwt_required()
def get_post_likes(post_id):
    return get_post_likes_list_controller(post_id)
