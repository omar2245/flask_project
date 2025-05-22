from functools import wraps

import jwt
from flask import request, jsonify, current_app


def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'Authorization header missing'}), 401

        bearer_token = auth_header.split()
        if bearer_token[0].lower() != 'bearer' or len(bearer_token) != 2:
            return jsonify({'error': 'Invalid Authorization header'}), 401
        token = bearer_token[1]

        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            request.id = payload['id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token expired'}), 401

        return f(*args, **kwargs)

    return decorated_function
