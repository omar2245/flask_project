import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, create_refresh_token, \
    set_refresh_cookies, unset_jwt_cookies
from sqlalchemy import or_

from models import db, Users

load_dotenv()  # load .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# connect SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Omar1231@localhost/flask'
db.init_app(app)
bcrypt = Bcrypt(app)


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if Users.query.filter((Users.username == username) | (Users.email == email)).first():
        return jsonify({'error': 'username or email are already exists'}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = Users(username=username, email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    user = Users.query.filter(or_(Users.username == username, Users.email == username)).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({'error': 'The username or password is invalid'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    resp = jsonify({'access_token': access_token})
    set_refresh_cookies(resp, refresh_token)
    return resp, 200


@app.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id = get_jwt_identity()
    user = Users.query.get(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email
    })


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({'access_token': new_access_token}), 200


@app.route('/logout', methods=['POST'])
def logout():
    resp = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(resp)
    return resp, 200


if __name__ == "__main__":
    app.run(debug=True)
