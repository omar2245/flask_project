import pytz

from datetime import datetime
from flask import Flask, request, render_template, flash, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy import or_

tz = pytz.timezone('Asia/Taipei')
app = Flask(__name__)
app.secret_key = 'flask_project_secret_key'

#connect SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Omar1231@localhost/flask'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255),  nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(tz))

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return "登入後的頁面！"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = Users(username=username, email=email, password_hash=hashed_pw)

        db.session.add(new_user)
        db.session.commit()
        flash('註冊成功!')
        return  redirect(url_for('login'))


    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Users.query.filter(or_( Users.username==username,Users.email==username)).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('登入成功!')
            return redirect(url_for('home'))
        else:
            flash('帳號或密碼錯誤')


    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)
