import os
import sys
from flask import Flask
from models import db, User, PMSEntry

# Create a minimal Flask app
app = Flask(__name__)

# Configure database
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Handle Neon's SSL requirements
    if 'neon.tech' in DATABASE_URL:
        # Don't add sslmode=require if it's already in the URL
        if '?sslmode=require' not in DATABASE_URL:
            app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
        else:
            app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

# Create tables and admin user
with app.app_context():
    print("Creating database tables...")
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        print("Creating admin user...")
        admin = User(username='admin', role='admin', name='Administrator')
        admin.set_password('admin123')  # Default password, should be changed
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully")
    else:
        print("Admin user already exists")
    
    print("Database initialization complete")