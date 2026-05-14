from pathlib import Path

from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.comment_controller import (
    create_comment_controller,
    update_comment_controller,
    delete_comment_controller,
    like_comment_controller,
    unlike_comment_controller,
    get_comment_like_list_controller
)

comment_bp = Blueprint('comments', __name__, url_prefix='/api/v1/comments')
SWAGGER_DIR = Path(__file__).resolve().parents[1] / 'docs' / 'swagger' / 'comments'


def swagger_file(filename):
    return str(SWAGGER_DIR / filename)


@comment_bp.route('', methods=['POST'])
@swag_from(swagger_file('create_comment.yml'))
@jwt_required()
def create_comment():
    return create_comment_controller()


@comment_bp.route('/<int:comment_id>', methods=['PUT'])
@swag_from(swagger_file('update_comment.yml'))
@jwt_required()
def update_comment(comment_id):
    return update_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>', methods=['DELETE'])
@swag_from(swagger_file('delete_comment.yml'))
@jwt_required()
def delete_comment(comment_id):
    return delete_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>/like', methods=['POST'])
@swag_from(swagger_file('like_comment.yml'))
@jwt_required()
def like_post(comment_id):
    return like_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>/unlike', methods=['DELETE'])
@swag_from(swagger_file('unlike_comment.yml'))
@jwt_required()
def unlike_post(comment_id):
    return unlike_comment_controller(comment_id)


@comment_bp.route('/<int:comment_id>/like', methods=['GET'])
@swag_from(swagger_file('get_comment_likes.yml'))
@jwt_required()
def get_comment_like_list(comment_id):
    return get_comment_like_list_controller(comment_id)
