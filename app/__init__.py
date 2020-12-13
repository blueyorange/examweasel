from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

# app setup with extensions:
# flask_bootstrap
# flask-sqlalchemy
# flask-migrate
# flask-login
# flask-wtf

app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# setup login manager to redirect anonymous users to login page
login.login_view = 'login'

from app import models, routes
