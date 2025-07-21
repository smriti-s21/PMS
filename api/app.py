import os
import sys
from flask import Flask, jsonify, render_template, redirect, url_for, flash, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime, date

# Add parent directory to path so we can import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create Flask app
app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())

# Database configuration - use environment variable for PostgreSQL connection
# Format: postgresql://username:password@hostname/database
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    # Use PostgreSQL in production
    # Handle Neon's SSL requirements
    if 'neon.tech' in DATABASE_URL:
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL + '?sslmode=require'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    # Use SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../instance/pms.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import and initialize models
from models import db, User, PMSEntry
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables and admin user
def create_tables():
    with app.app_context():
        db.create_all()
        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', role='admin', name='Administrator')
            admin.set_password('admin123')  # Default password, should be changed
            db.session.add(admin)
            db.session.commit()

# Context processor to add current date to all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Import routes
try:
    from routes import *
except ImportError:
    # For Vercel deployment, define basic routes here
    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({"status": "ok", "message": "API is working"})

# Initialize database
create_tables()

# For local development
if __name__ == '__main__':
    app.run(debug=True)