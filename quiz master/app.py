from flask import Flask
from flask_login import LoginManager
from models.model import db, User
from werkzeug.security import generate_password_hash
from functools import wraps
import os

app = None
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates")
    app.secret_key = '23f3003203quizmaster'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    login_manager.init_app(app)
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()

def setup_database():
    if not os.path.exists("instance/quiz_master.db"): 
        db.create_all() 

        admin = User(id = 1, username= "quiz_master@gmail.com", password= generate_password_hash("admin1234@#"), full_name= "Quiz Master")
        db.session.add(admin)
        db.session.commit()

with app.app_context():
    setup_database()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from controllers.user_controller import *
from controllers.admin_controller import *
from controllers.login_signup import *
from controllers.error_handler import *


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
