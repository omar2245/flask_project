from flask import Blueprint
from flask_jwt_extended import jwt_required

from controllers.user_controller import get_user_controller, get_me_controller, update_me_controller

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
