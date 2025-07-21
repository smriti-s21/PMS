from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'intern'
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    pms_entries = db.relationship('PMSEntry', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PMSEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    section = db.Column(db.String(50), nullable=False)  # TND, COLLEGE COLLAB, etc.
    
    # Metrics
    mtd_leads = db.Column(db.Integer, default=0)  # Month to date leads
    daily_leads_generated = db.Column(db.Integer, default=0)
    daily_leads_contacted = db.Column(db.Integer, default=0)
    daily_prospects = db.Column(db.Integer, default=0)
    daily_suspects = db.Column(db.Integer, default=0)
    
    # Recruitment specific fields
    applications_received = db.Column(db.Integer, default=0)
    interviewed = db.Column(db.Integer, default=0)
    on_hold = db.Column(db.Integer, default=0)
    shortlisted = db.Column(db.Integer, default=0)
    rejected = db.Column(db.Integer, default=0)
    
    support_required = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)