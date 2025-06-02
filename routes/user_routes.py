from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_jwt_identity, jwt_required

from models import db
from models.user import User

user_bp = Blueprint('user', __name__, url_prefix='/api/v1/user')


@user_bp.route('/me', methods=['GET', 'PUT'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found!'}), 404

    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email
        })

    elif request.method == 'PUT':
        data = request.json
        new_username = data.get('username')
        new_email = data.get('email')

        if new_username and User.query.filter(User.username == new_username, User.id != user_id).first():
            return jsonify({'error': 'Username has been used'}), 400
        if new_email and User.query.filter(User.email == new_email, User.id != user_id).first():
            return jsonify({'error': 'Email has been used'}), 400

        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email

        db.session.commit()

        return jsonify({
            'msg': 'Update Successfully'
        })

    return jsonify({'error': 'Method not allowed'}), 405


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'User not found!'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username
    })
