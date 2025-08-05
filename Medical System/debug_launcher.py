"""
Medical Test System Launcher with Debug Information
This script helps diagnose startup issues and provides better error reporting.
"""

import sys
import os
import traceback
from datetime import datetime

def check_requirements():
    """Check if all required packages are available"""
    print("🔍 Checking system requirements...")
    
    required_modules = [
        ('tkinter', 'GUI framework'),
        ('sqlite3', 'Database support'),
        ('pandas', 'Data processing'),
        ('openpyxl', 'Excel file support'),
        ('matplotlib', 'Plotting and visualization')
    ]
    
    missing_modules = []
    
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"   ✅ {module_name} - {description}")
        except ImportError:
            print(f"   ❌ {module_name} - {description} (MISSING)")
            missing_modules.append(module_name)
    
    if missing_modules:
        print(f"\n❌ Missing required modules: {', '.join(missing_modules)}")
        print("💡 Install missing modules with: pip install -r requirements.txt")
        return False
    
    print("✅ All required modules are available!")
    return True

def check_database():
    """Check database status"""
    print("\n🗃️ Checking database status...")
    
    db_path = "medical_test_data.db"
    if os.path.exists(db_path):
        print(f"   ✅ Database file exists: {db_path}")
        
        try:
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [table[0] for table in cursor.fetchall()]
                print(f"   ✅ Database has {len(tables)} tables: {tables}")
                return True
        except Exception as e:
            print(f"   ❌ Database error: {e}")
            return False
    else:
        print(f"   ⚠️ Database file not found: {db_path}")
        print("   💡 Will be created automatically on first run")
        return True

def launch_application():
    """Launch the main application with error handling"""
    print("\n🚀 Launching Medical Test System...")
    
    try:
        # Import and start the application
        from main import MedicalTestSystem
        
        print("   ✅ Main application module imported successfully")
        
        app = MedicalTestSystem()
        print("   ✅ Application instance created successfully")
        
        print("   🎯 Starting GUI...")
        app.run()
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Check if all required files are present in the current directory")
        return False
        
    except Exception as e:
        print(f"   ❌ Application error: {e}")
        print("\n📋 Full error details:")
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🏥 Medical Test System - Debug Launcher")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📂 Working directory: {os.getcwd()}")
    print()
    
    # Step 1: Check requirements
    if not check_requirements():
        input("\nPress Enter to exit...")
        return
    
    # Step 2: Check database
    if not check_database():
        print("\n⚠️ Database issues detected. The application may still work.")
    
    # Step 3: Launch application
    print("\n" + "─" * 60)
    success = launch_application()
    
    if success:
        print("\n✅ Application closed normally")
    else:
        print("\n❌ Application failed to start or crashed")
        print("\n💡 Troubleshooting tips:")
        print("1. Run fresh_start.py to reset the database")
        print("2. Check if all files are present in the directory")
        print("3. Reinstall requirements: pip install -r requirements.txt")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
