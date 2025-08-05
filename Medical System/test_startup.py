"""
Test script to debug application startup issues
"""

import sys
import traceback

try:
    print("1. Testing basic imports...")
    import tkinter as tk
    print("   ✅ tkinter imported successfully")
    
    import sqlite3
    print("   ✅ sqlite3 imported successfully")
    
    import pandas as pd
    print("   ✅ pandas imported successfully")
    
    print("\n2. Testing database components...")
    from database_manager import DatabaseManager
    db = DatabaseManager()
    print("   ✅ DatabaseManager initialized successfully")
    
    from data_processor import DataProcessor
    processor = DataProcessor(db)
    print("   ✅ DataProcessor initialized successfully")
    
    print("\n3. Testing UI components...")
    from ui_components import PatientForm, TestResultForm, DataImportFrame
    print("   ✅ UI components imported successfully")
    
    from flexible_import_ui import FlexibleDataImportFrame
    print("   ✅ FlexibleDataImportFrame imported successfully")
    
    from test_configuration_ui import TestConfigurationFrame
    print("   ✅ TestConfigurationFrame imported successfully")
    
    print("\n4. Testing basic tkinter window...")
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x200")
    
    # Create a simple label
    label = tk.Label(root, text="If you see this window, GUI is working!")
    label.pack(pady=50)
    
    # Create a close button
    def close_window():
        root.destroy()
        print("   ✅ GUI test window closed successfully")
    
    close_btn = tk.Button(root, text="Close", command=close_window)
    close_btn.pack()
    
    print("   ✅ Basic tkinter window created successfully")
    print("\n🎉 All components loaded successfully!")
    print("\nShowing test window for 3 seconds...")
    
    # Show window for 3 seconds then close
    root.after(3000, close_window)
    root.mainloop()
    
    print("\n✅ GUI test completed successfully!")
    print("✅ All startup components are working properly!")
    
except Exception as e:
    print(f"\n❌ Error during startup test: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
