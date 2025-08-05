"""
Fresh Start Script - Reset Medical Test System Database
This script will completely reset the database, removing all:
- Patients
- Test results
- Test types
- Custom ranges
- All data

Use this to start with a completely clean system.
"""

import sqlite3
import os
import shutil
import sys
from datetime import datetime

def backup_existing_database():
    """Create a backup of the existing database before clearing"""
    db_path = "medical_test_data.db"
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"medical_test_data_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    return None

def clear_all_data():
    """Clear all data from the database while keeping structure"""
    db_path = "medical_test_data.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("🗑️  Clearing all data...")
            
            # Clear data in correct order (respect foreign key constraints)
            cursor.execute('DELETE FROM test_results')
            print("   - Test results cleared")
            
            # Check if custom_ranges table exists before clearing
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='custom_ranges'")
            if cursor.fetchone():
                cursor.execute('DELETE FROM custom_ranges')
                print("   - Custom ranges cleared")
            
            cursor.execute('DELETE FROM patients')
            print("   - Patients cleared")
            
            cursor.execute('DELETE FROM test_types')
            print("   - Test types cleared (clean slate - no default tests)")
            
            # Reset auto-increment counters
            cursor.execute('DELETE FROM sqlite_sequence')
            print("   - Auto-increment counters reset")
            
            conn.commit()
            print("✅ All data cleared successfully!")
            
    except sqlite3.Error as e:
        print(f"❌ Error clearing data: {e}")
        return False
    
    return True

def recreate_fresh_database():
    """Delete and recreate the entire database"""
    db_path = "medical_test_data.db"
    
    try:
        # Remove existing database
        if os.path.exists(db_path):
            os.remove(db_path)
            print("🗑️  Old database deleted")
        
        # Create fresh database
        print("🆕 Creating fresh database...")
        from database_manager import DatabaseManager
        db = DatabaseManager()
        print("✅ Fresh database created with clean schema!")
        
        # Verify database was created properly
        if os.path.exists(db_path):
            print("✅ Database file verified to exist")
            
            # Test database connection
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                print(f"✅ Database has {len(tables)} tables: {[table[0] for table in tables]}")
        else:
            print("❌ Warning: Database file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error recreating database: {e}")
        return False
        
    return True

def main():
    """Main function to reset the system"""
    print("=" * 60)
    print("🏥 Medical Test System - Fresh Start")
    print("=" * 60)
    print()
    print("This will completely reset your medical test system:")
    print("❌ Remove ALL patients")
    print("❌ Remove ALL test results") 
    print("❌ Remove ALL test types")
    print("❌ Remove ALL custom ranges")
    print("✅ Create a backup first")
    print("✅ Start with completely clean database")
    print()
    
    # Confirm with user
    response = input("⚠️  Are you sure you want to proceed? (type 'YES' to confirm): ")
    
    if response.upper() != 'YES':
        print("❌ Operation cancelled.")
        return
    
    print("\n🚀 Starting fresh database reset...")
    print()
    
    # Step 1: Backup existing database
    backup_path = backup_existing_database()
    
    # Step 2: Choose reset method
    print("\nChoose reset method:")
    print("1. Clear all data but keep database structure")
    print("2. Delete and recreate entire database (recommended)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        # Clear data only
        success = clear_all_data()
    else:
        # Recreate entire database
        success = recreate_fresh_database()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 FRESH START COMPLETE!")
        print("=" * 60)
        print()
        print("✅ Database has been reset to fresh state")
        print("✅ All old data has been removed")
        if backup_path:
            print(f"✅ Backup saved as: {backup_path}")
        print()
        print("📋 Next Steps:")
        print("1. Run the application: python main.py")
        print("2. Use 'Test Types' tab to add your test types")
        print("3. Add patients in 'Patient Management' tab")
        print("4. Start entering test results")
        print()
        print("💡 Tip: Use quick_setup.bat to add sample data")
        
        # Ask if user wants to launch the application now
        print()
        launch_choice = input("🚀 Would you like to launch the application now? (y/n): ").strip().lower()
        if launch_choice in ['y', 'yes']:
            print("\n🎯 Launching Medical Test System...")
            try:
                import subprocess
                subprocess.run([sys.executable, "main.py"])
            except Exception as e:
                print(f"❌ Error launching application: {e}")
                print("💡 You can manually run: python main.py")
        
    else:
        print("\n❌ Fresh start failed. Check error messages above.")

if __name__ == "__main__":
    main()
