"""
Complete Fresh Start - Remove ALL data and restart application
"""

import os
import sys
import shutil
import glob

def complete_fresh_start():
    """Remove all data files and restart with completely clean state"""
    print("Final COMPLETE FRESH START")
    print("=" * 50)
    
    # 1. Delete database file
    db_file = "medical_test_data.db"
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Database deleted")
    
    # 2. Delete ALL CSV files
    csv_files = glob.glob("*.csv")
    for csv_file in csv_files:
        os.remove(csv_file)
        print(f"Removed {csv_file}")
    
    # 3. Delete sample data files
    sample_files = ["sample_data.csv", "sample_device_data.csv", "sample_test_data.csv"]
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print(f"Removed {sample_file}")
    
    # 4. Delete test files
    test_files = glob.glob("test_*.py")
    demo_files = glob.glob("*demo*.csv")
    for file in test_files + demo_files:
        if file != "test_gender_functionality.py":  # Keep the demo test
            try:
                os.remove(file)
                print(f" Removed {file}")
            except:
                pass
    
    # 5. Delete JSON config files
    json_files = glob.glob("*.json")
    for json_file in json_files:
        os.remove(json_file)
        print(f"Removed {json_file}")
    
    # 6. Delete PDF reports
    pdf_files = glob.glob("*.pdf")
    for pdf_file in pdf_files:
        if not pdf_file.endswith("CHOWDHURY.pdf"):  # Keep original reference
            os.remove(pdf_file)
            print(f" Removed {pdf_file}")
    
    # 7. Clear Python cache
    if os.path.exists('__pycache__'):
        shutil.rmtree('__pycache__')
        print(" Python cache cleared")
    
    # 8. Delete any backup files
    backup_files = glob.glob("*.bak") + glob.glob("*~") + glob.glob("*.tmp")
    for backup_file in backup_files:
        os.remove(backup_file)
        print(f" Removed {backup_file}")
    
    print("\n FRESH done")
    print("All data wiped starting")
    print("=" * 50)
    
    # Start the application
    import subprocess
    subprocess.run([sys.executable, "main.py"])

if __name__ == "__main__":
    complete_fresh_start()
