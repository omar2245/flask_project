from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.user_controller import get_user_controller, get_me_controller, update_me_controller, \
    follow_user_controller, unfollow_user_controller, get_following_user_controller, get_user_follower_controller, \
    get_user_posts_controller, get_follow_stats_controller, is_following_user_controller

user_bp = Blueprint('user', __name__, url_prefix='/api/v1/user')


@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    return get_me_controller()


@user_bp.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    return update_me_controller()


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return get_user_controller(user_id)


@user_bp.route('<int:user_id>/follow', methods=['POST'])
@jwt_required()
def follow_user(user_id):
    return follow_user_controller(user_id)


@user_bp.route('<int:user_id>/unfollow', methods=['DELETE'])
@jwt_required()
def unfollow_user(user_id):
    return unfollow_user_controller(user_id)


@user_bp.route('<int:user_id>/following', methods=['GET'])
def get_following_user(user_id):
    return get_following_user_controller(user_id)


@user_bp.route('<int:user_id>/follower', methods=['GET'])
def get_user_follower(user_id):
    return get_user_follower_controller(user_id)


@user_bp.route('/<int:user_id>/posts', methods=['GET'])
@jwt_required(optional=True)
def get_user_posts(user_id):
    return get_user_posts_controller(user_id)


@user_bp.route('/<int:user_id>/follows/stat', methods=['GET'])
def get_follow_stats(user_id):
    return get_follow_stats_controller(user_id)


@user_bp.route("/<int:target_user_id>/is_following", methods=["GET"])
@jwt_required()
def is_following_user(target_user_id):
    return is_following_user_controller(target_user_id)
