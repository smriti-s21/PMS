from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, date
import uuid
from models import db, User, PMSEntry
from app import app

# Constants
SECTIONS = ['TND', 'COLLEGE COLLAB', 'COMPANY COLLAB', 'SCHOOL COLLAB', 'RECRUITMENT']

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'admin':
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')
    
    return render_template('admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def intern_login():
    if current_user.is_authenticated and current_user.role == 'intern':
        return redirect(url_for('intern_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.role == 'intern':
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('intern_dashboard'))
        else:
            flash('Invalid credentials', 'danger')
    
    return render_template('intern_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin_login'))
    
    # Get all interns
    interns = User.query.filter_by(role='intern').all()
    
    # Get today's entries
    today = date.today()
    today_entries = PMSEntry.query.filter(PMSEntry.date == today).all()
    
    # Debug info
    print(f"Found {len(today_entries)} entries for today")
    for entry in today_entries:
        print(f"Entry: {entry.user.name}, {entry.section}, {entry.mtd_leads}")
    
    return render_template('admin_dashboard.html', interns=interns, entries=today_entries)

@app.route('/admin/users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/admin/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        name = request.form.get('name')
        email = request.form.get('email')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('add_user'))
        
        user = User(username=username, role=role, name=name, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('User added successfully', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('add_user.html')

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username')
        user.role = request.form.get('role')
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    
    if user.username == 'admin':
        flash('Cannot delete admin user', 'danger')
        return redirect(url_for('manage_users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully', 'success')
    return redirect(url_for('manage_users'))

@app.route('/admin/reports')
@login_required
def admin_reports():
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('index'))
    
    # Get filter parameters
    user_id = request.args.get('user_id', type=int)
    section = request.args.get('section')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query
    query = PMSEntry.query
    
    # Apply filters
    if user_id:
        query = query.filter_by(user_id=user_id)
    if section:
        query = query.filter_by(section=section)
    if start_date:
        query = query.filter(PMSEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(PMSEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Get entries
    entries = query.order_by(PMSEntry.date.desc()).all()
    
    # Get all interns for filter dropdown
    interns = User.query.filter_by(role='intern').all()
    
    return render_template('admin_reports.html', entries=entries, interns=interns, sections=SECTIONS)

@app.route('/intern/dashboard')
@login_required
def intern_dashboard():
    if current_user.role != 'intern':
        flash('Access denied. Intern privileges required.', 'danger')
        return redirect(url_for('intern_login'))
    
    # Get today's entries for the current user
    today = date.today()
    today_entries = PMSEntry.query.filter_by(user_id=current_user.id, date=today).all()
    
    # Create a dictionary to store entries by section
    entries_by_section = {section: None for section in SECTIONS}
    
    # Fill in existing entries
    for entry in today_entries:
        entries_by_section[entry.section] = entry
    
    return render_template('intern_dashboard.html', entries_by_section=entries_by_section, sections=SECTIONS)

@app.route('/intern/update_pms', methods=['POST'])
@login_required
def update_pms():
    if current_user.role != 'intern':
        flash('Access denied. Intern privileges required.', 'danger')
        return redirect(url_for('intern_login'))
    
    section = request.form.get('section')
    
    if section not in SECTIONS:
        flash('Invalid section', 'danger')
        return redirect(url_for('intern_dashboard'))
    
    today = date.today()
    
    # Check if entry already exists for today and this section
    entry = PMSEntry.query.filter_by(
        user_id=current_user.id,
        date=today,
        section=section
    ).first()
    
    # If entry doesn't exist, create a new one
    if not entry:
        entry = PMSEntry(
            user_id=current_user.id,
            date=today,
            section=section
        )
        db.session.add(entry)
    
    # Update entry fields
    entry.mtd_leads = request.form.get('mtd_leads', type=int) or 0
    entry.daily_leads_generated = request.form.get('daily_leads_generated', type=int) or 0
    entry.daily_leads_contacted = request.form.get('daily_leads_contacted', type=int) or 0
    entry.daily_prospects = request.form.get('daily_prospects', type=int) or 0
    entry.daily_suspects = request.form.get('daily_suspects', type=int) or 0
    
    # Update recruitment specific fields if section is RECRUITMENT
    if section == 'RECRUITMENT':
        entry.applications_received = request.form.get('applications_received', type=int) or 0
        entry.interviewed = request.form.get('interviewed', type=int) or 0
        entry.on_hold = request.form.get('on_hold', type=int) or 0
        entry.shortlisted = request.form.get('shortlisted', type=int) or 0
        entry.rejected = request.form.get('rejected', type=int) or 0
    
    entry.support_required = request.form.get('support_required', '')
    
    db.session.commit()
    
    flash(f'{section} data updated successfully', 'success')
    return redirect(url_for('intern_dashboard'))

@app.route('/intern/history')
@login_required
def intern_history():
    if current_user.role != 'intern':
        flash('Access denied. Intern privileges required.', 'danger')
        return redirect(url_for('intern_login'))
    
    # Get filter parameters
    section = request.args.get('section')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Base query for current user's entries
    query = PMSEntry.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if section:
        query = query.filter_by(section=section)
    if start_date:
        query = query.filter(PMSEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(PMSEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Get entries
    entries = query.order_by(PMSEntry.date.desc()).all()
    
    return render_template('intern_history.html', entries=entries, sections=SECTIONS)