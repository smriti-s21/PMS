from app import app, db
from models import User, PMSEntry
import sqlite3
import os

def migrate_database():
    # Ensure instance folder exists
    os.makedirs('instance', exist_ok=True)
    
    # Check if database exists
    db_path = os.path.join('instance', 'pms.db')
    if os.path.exists(db_path):
        print("Database exists, backing up...")
        # Backup the database
        backup_path = os.path.join('instance', 'pms_backup.db')
        if os.path.exists(backup_path):
            os.remove(backup_path)
        
        # Copy the database
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        
        # Add new columns to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(pms_entry)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add on_hold column if it doesn't exist
        if 'on_hold' not in columns:
            print("Adding on_hold column...")
            cursor.execute("ALTER TABLE pms_entry ADD COLUMN on_hold INTEGER DEFAULT 0")
        
        # Add rejected column if it doesn't exist
        if 'rejected' not in columns:
            print("Adding rejected column...")
            cursor.execute("ALTER TABLE pms_entry ADD COLUMN rejected INTEGER DEFAULT 0")
        
        conn.commit()
        conn.close()
        print("Database migration completed successfully!")
    else:
        print("Database doesn't exist, creating new database...")
        with app.app_context():
            db.create_all()
            # Create admin user if not exists
            if not User.query.filter_by(username='admin').first():
                admin = User(username='admin', role='admin', name='Administrator')
                admin.set_password('admin123')  # Default password, should be changed
                db.session.add(admin)
                db.session.commit()
            print("Database created successfully!")

if __name__ == "__main__":
    migrate_database()