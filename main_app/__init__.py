# This is a blog app the allows users to register and post blogs
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
import os

app = Flask(__name__)
# Website secret key
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# Login manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# Mail server
app.config['MAIL_SERVER'] = os.environ.get('DB_MAILSERVER')
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('DB_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('DB_PASSWORD')
mail = Mail(app)

from main_app import routes
