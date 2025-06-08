from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Initialize extensions without binding to an app
# They will be initialized with the app in run.py
db = SQLAlchemy()
login_manager = LoginManager()
