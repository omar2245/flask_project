from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.post_controller import create_post_controller, get_all_posts_controller, get_post_detail_controller, \
    update_post_controller, delete_post_controller

post_bp = Blueprint('post', __name__, url_prefix='/api/v1/posts')


@post_bp.route('', methods=['POST'])
@jwt_required()
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
