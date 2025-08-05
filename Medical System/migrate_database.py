"""
Database Migration Script
Updates existing database to make first_name and last_name optional
Run this script to update your existing medical_test_data.db
"""

import sqlite3
import os
import shutil
from datetime import datetime

def migrate_database(db_path="medical_test_data.db"):
    """Migrate existing database to make first_name and last_name optional"""
    
    if not os.path.exists(db_path):
        print(f"Database {db_path} does not exist. No migration needed.")
        return
    
    # Create backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"Created backup: {backup_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if migration is needed
            cursor.execute("PRAGMA table_info(patients)")
            columns = cursor.fetchall()
            
            # Check if first_name or last_name have NOT NULL constraint
            needs_migration = False
            for col in columns:
                if col[1] in ['first_name', 'last_name'] and col[3] == 1:  # NOT NULL = 1
                    needs_migration = True
                    break
            
            if not needs_migration:
                print("Database is already up to date. No migration needed.")
                return
            
            print("Starting migration...")
            
            # Create new table with updated schema
            cursor.execute('''
                CREATE TABLE patients_new (
                    patient_id TEXT PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    date_of_birth DATE,
                    gender TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Copy data from old table to new table
            cursor.execute('''
                INSERT INTO patients_new 
                SELECT * FROM patients
            ''')
            
            # Drop old table
            cursor.execute('DROP TABLE patients')
            
            # Rename new table
            cursor.execute('ALTER TABLE patients_new RENAME TO patients')
            
            conn.commit()
            print("Migration completed successfully!")
            print("First Name and Last Name are now optional fields.")
            
    except Exception as e:
        print(f"Migration failed: {e}")
        print(f"Restoring from backup: {backup_path}")
        shutil.copy2(backup_path, db_path)
        raise

if __name__ == "__main__":
    migrate_database()
