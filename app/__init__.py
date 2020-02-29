from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_moment import Moment

app = Flask(__name__)

environment = app.config["ENV"]
if environment == "production":
    app.config.from_object("config.ProductionConfig")
elif environment == "testing":
    app.config.from_object("config.TestingConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
moment = Moment(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@app.before_first_request
def create_tables():
    from app.models import User
    db.create_all()

from app import routes