from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import Config

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
# check for change in column type when migrating by setting compare_type to True
migrate = Migrate(app, db, compare_type=True)
login = LoginManager(app)
# setup login manager to redirect anonymous users to login page
login.login_view = 'login'

from app import models, routes

# set up alembic to support dropping columns when migrating
# https://stackoverflow.com/questions/30394222/why-flask-migrate-cannot-upgrade-when-drop-column
with app.app_context():
    if db.engine.url.drivername == 'sqlite':
        migrate.init_app(app, db, render_as_batch=True)
    else:
        migrate.init_app(app, db)