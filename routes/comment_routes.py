from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.comment_controller import create_comment_controller, update_comment_controller, \
    delete_comment_controller, like_comment_controller, unlike_comment_controller

comment_bp = Blueprint('comments', __name__, url_prefix='/api/v1/comments')


# 問這支API的 route 用這個還是POST /posts/<post_id>/comments
@comment_bp.route('', methods=['POST'])
@jwt_required()
def create_comment():
    return create_comment_controller()


@comment_bp.route('/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id):
    return update_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    return delete_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>/like', methods=['POST'])
@jwt_required()
def like_post(comment_id):
    return like_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>/unlike', methods=['DELETE'])
@jwt_required()
def unlike_post(comment_id):
    return unlike_comment_controller(comment_id)
