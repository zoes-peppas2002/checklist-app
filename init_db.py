import os
from flask import Flask
from werkzeug.security import generate_password_hash
from extensions import db, login_manager
from models_def import User

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mysecretkey')
    
    # Database configuration
    if 'RENDER' in os.environ:
        # Use the DATABASE_URL provided by Render
        database_url = os.environ.get('DATABASE_URL')
        if database_url and database_url.startswith('postgres://'):
            # Heroku-style URL needs to be updated for SQLAlchemy 1.4+
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Local development database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Zoupeppas2002!@localhost/checklist_app'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    return app

def init_db():
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                password=generate_password_hash('admin123'),  # Default password, change this!
                role='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'admin123'")
            print("IMPORTANT: Change this password immediately after first login!")
        else:
            print("Admin user already exists")
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
