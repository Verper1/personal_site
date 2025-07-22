from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask import Flask
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_BINDS'] = {
#     'comments': os.environ.get('DATABASE_URL'),
# }
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
csrf = CSRFProtect(app)
WTF_CSRF_ENABLED = True

migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

limiter = Limiter(
    key_func=get_remote_address, # ограничение на основе IP, можно сделать по пользователю
    app=app,
    default_limits=["100 per hour"]
)

with app.app_context():
    db.create_all()
