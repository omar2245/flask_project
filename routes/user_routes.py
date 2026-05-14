from pathlib import Path

from flasgger import swag_from
from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.user_controller import (
    get_user_controller,
    get_me_controller,
    update_me_controller,
    follow_user_controller,
    unfollow_user_controller,
    get_following_user_controller,
    get_user_follower_controller,
    get_user_posts_controller,
    get_follow_stats_controller,
    is_following_user_controller,
    upload_avatar_controller
)

user_bp = Blueprint('user', __name__, url_prefix='/api/v1/user')
SWAGGER_DIR = Path(__file__).resolve().parents[1] / 'docs' / 'swagger' / 'users'


def swagger_file(filename):
    return str(SWAGGER_DIR / filename)


@user_bp.route('/me', methods=['GET'])
@swag_from(swagger_file('get_me.yml'))
@jwt_required()
def get_me():
    return get_me_controller()


@user_bp.route('/me', methods=['PUT'])
@swag_from(swagger_file('update_me.yml'))
@jwt_required()
def update_me():
    return update_me_controller()


@user_bp.route('/me/upload_avatar', methods=['POST'])
@swag_from(swagger_file('upload_avatar.yml'))
@jwt_required()
def upload_avatar():
    return upload_avatar_controller()


@user_bp.route('/<int:user_id>', methods=['GET'])
@swag_from(swagger_file('get_user.yml'))
def get_user(user_id):
    return get_user_controller(user_id)


@user_bp.route('<int:user_id>/follow', methods=['POST'])
@swag_from(swagger_file('follow_user.yml'))
@jwt_required()
def follow_user(user_id):
    return follow_user_controller(user_id)


@user_bp.route('<int:user_id>/unfollow', methods=['DELETE'])
@swag_from(swagger_file('unfollow_user.yml'))
@jwt_required()
def unfollow_user(user_id):
    return unfollow_user_controller(user_id)


@user_bp.route('<int:user_id>/following', methods=['GET'])
@swag_from(swagger_file('get_following.yml'))
def get_following_user(user_id):
    return get_following_user_controller(user_id)


@user_bp.route('<int:user_id>/follower', methods=['GET'])
@swag_from(swagger_file('get_followers.yml'))
def get_user_follower(user_id):
    return get_user_follower_controller(user_id)


@user_bp.route('/<int:user_id>/posts', methods=['GET'])
@swag_from(swagger_file('get_user_posts.yml'))
@jwt_required(optional=True)
def get_user_posts(user_id):
    return get_user_posts_controller(user_id)


@user_bp.route('/<int:user_id>/follows/stat', methods=['GET'])
@swag_from(swagger_file('get_follow_stats.yml'))
def get_follow_stats(user_id):
    return get_follow_stats_controller(user_id)


@user_bp.route("/<int:target_user_id>/is_following", methods=["GET"])
@swag_from(swagger_file('is_following.yml'))
@jwt_required()
def is_following_user(target_user_id):
    return is_following_user_controller(target_user_id)
