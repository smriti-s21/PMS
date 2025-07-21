from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
import os
import uuid
from datetime import datetime, date
from models import db, User, PMSEntry

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
def create_tables():
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    
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
from routes import *

# Create tables when app is initialized
with app.app_context():
    create_tables()

# For local development
if __name__ == '__main__':
    app.run(debug=True)