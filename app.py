import os
from datetime import timedelta

import cloudinary
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from controllers import bcrypt
from models import db
from routes.auth_routes import auth_bp
from routes.comment_routes import comment_bp
from routes.post_routes import post_bp
from routes.user_routes import user_bp

load_dotenv()  # load .env

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)  # 測試方便記得改回來
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
jwt = JWTManager(app)

# connect SQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI') or os.environ.get('DATABASE_URL')
db.init_app(app)
migrate = Migrate(app, db)
bcrypt.init_app(app)

# connect cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)
CORS(app, supports_credentials=True)


# 測試登入和Refresh token cookie用的
@app.route('/')
def test():
    return 'test'


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug)
