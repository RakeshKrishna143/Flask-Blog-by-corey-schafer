from flask import Flask
from config import Config
from flask_mongoengine import MongoEngine
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)

bcrypt = Bcrypt()
bcrypt.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #to which we need to redirect
login_manager.login_message_category = 'info' #bootstrp class

mail = Mail()
mail.init_app(app)

from application import routes

