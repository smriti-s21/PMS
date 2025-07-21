# EpitomeTRC - Performance Management System

A web-based Performance Management System (PMS) for EpitomeTRC with admin and intern roles.

## Features

- **Admin Role**:
  - Manage users (edit, delete)
  - View reports from all interns
  - Filter reports by intern, section, and date range

- **Intern Role**:
  - Update daily PMS data for different sections
  - View personal history
  - Filter history by section and date range

- **Sections**:
  - TND
  - COLLEGE COLLAB
  - COMPANY COLLAB
  - SCHOOL COLLAB
  - RECRUITMENT

- **Metrics for Regular Sections**:
  - MTD (Month to Date) leads
  - Daily leads generated
  - Daily leads contacted
  - Daily prospects
  - Daily suspects
  - Support/help required

- **Metrics for Recruitment Section**:
  - MTD (Month to Date)
  - Applications Received
  - Interviewed Candidates
  - On Hold
  - Shortlisted
  - Rejected/Not Eligible
  - Support/help required

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install flask flask-sqlalchemy flask-login
   ```
3. Run the migration script to set up the database:
   ```
   python migrate_db.py
   ```
4. Run the application:
   ```
   python app.py
   ```
5. Access the application at `http://127.0.0.1:5000`

## Default Admin Credentials

- Username: admin
- Password: admin123

**Important**: Change the default admin password after first login for security.

## Technologies Used

- Flask (Python web framework)
- SQLite (Database)
- SQLAlchemy (ORM)
- HTML, CSS, JavaScript
- Bootstrap 5 (Frontend framework)

## Color Theme

- Orange
- Black
- White