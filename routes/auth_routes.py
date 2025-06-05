from flask import Blueprint

from controllers.auth_controller import (
    register_controller,
    login_controller,
    refresh_controller,
    logout_controller
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    return register_controller()


@auth_bp.route('/login', methods=['POST'])
def login():
    return login_controller()


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    return refresh_controller()


@auth_bp.route('/logout', methods=['POST'])
def logout():
    return logout_controller()
