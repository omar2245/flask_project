import os
import re
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
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
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

    # username 格式
    if len(username) < 3 or len(username) > 20:
        return jsonify({'error': 'Username must be 3-20 characters'}), 400
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        return jsonify({'error': 'Username can only contain letters, numbers and _'}), 400

    # email 格式
    if not re.match(r'^\S+@\S+\.\S+$', email):
        return jsonify({'error': 'Invalid email format'}), 400

    # 密碼格式
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400
    if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
        return jsonify({'error': 'Password must contain both letters and numbers'}), 400

    # 確認username 和 email是否重複
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


@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user_id)

    return jsonify({'access_token': new_access_token}), 200


@app.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    resp = jsonify({'msg': 'logout successfully'})
    unset_jwt_cookies(resp)
    return resp, 200


@app.route('/me', methods=['GET', 'PUT'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(Users, user_id)
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

        if new_username and Users.query.filter(Users.username == new_username, Users.id != user_id).first():
            return jsonify({'error': 'Username has been used'}), 400
        if new_email and Users.query.filter(Users.email == new_email, Users.id != user_id).first():
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


@app.route('/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    user = db.session.get(Users, user_id)
    if not user:
        return jsonify({'error': 'User not found!'}), 404

    return jsonify({
        'id': user.id,
        'username': user.username
    })


# 測試登入和Refresh token cookie用的
@app.route('/')
def test():
    return 'test'


if __name__ == "__main__":
    app.run(debug=True)
