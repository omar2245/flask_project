from flask import jsonify, Blueprint
from flask_jwt_extended import jwt_required

from controllers.user_controller import me_controller
from models import db
from models.user import User

user_bp = Blueprint('user', __name__, url_prefix='/api/v1/user')


@user_bp.route('/me', methods=['GET', 'PUT'])
@jwt_required()
def me():
    return me_controller()


@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found!'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username
    })
