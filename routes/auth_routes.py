from pathlib import Path

from flasgger import swag_from
from flask import Blueprint

from controllers.auth_controller import (
    register_controller,
    login_controller,
    refresh_controller,
    logout_controller
)

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
SWAGGER_DIR = Path(__file__).resolve().parents[1] / 'docs' / 'swagger' / 'auth'


def swagger_file(filename):
    return str(SWAGGER_DIR / filename)


@auth_bp.route('/register', methods=['POST'])
@swag_from(swagger_file('register.yml'))
def register():
    return register_controller()


@auth_bp.route('/login', methods=['POST'])
@swag_from(swagger_file('login.yml'))
def login():
    return login_controller()


@auth_bp.route('/refresh', methods=['POST'])
@swag_from(swagger_file('refresh.yml'))
def refresh():
    return refresh_controller()


@auth_bp.route('/logout', methods=['POST'])
@swag_from(swagger_file('logout.yml'))
def logout():
    return logout_controller()
