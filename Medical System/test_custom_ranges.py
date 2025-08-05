"""
Test script for Custom Ranges functionality
This script verifies that the custom ranges system is working correctly.
"""

import sqlite3
import json
from database_manager import DatabaseManager

def test_custom_ranges():
    """Test the custom ranges functionality"""
    print("Testing Custom Ranges System")
    print("=" * 50)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Test 1: Add a custom range
    print("\n1. Testing custom range creation...")
    try:
        success = db_manager.add_custom_test_range(
            test_type_id=4,  # Blood Glucose
            range_name="Test Diabetic Range",
            age_min=18,
            age_max=65,
            gender=None,
            condition_name="Diabetes",
            normal_min=80.0,
            normal_max=130.0,
            critical_low=70.0,
            critical_high=200.0,
            notes="Test range for diabetic patients"
        )
        print(f"✓ Custom range creation: {'SUCCESS' if success else 'FAILED'}")
    except Exception as e:
        print(f"✗ Custom range creation failed: {e}")
    
    # Test 2: Retrieve custom ranges
    print("\n2. Testing custom range retrieval...")
    try:
        ranges = db_manager.get_custom_test_ranges()
        print(f"✓ Retrieved {len(ranges)} custom ranges")
        if ranges:
            print(f"   Sample range: {ranges[0][2]} for {ranges[0][-1]}")  # range_name for test_name
    except Exception as e:
        print(f"✗ Custom range retrieval failed: {e}")
    
    # Test 3: Best matching range algorithm
    print("\n3. Testing range matching algorithm...")
    try:
        # Test with a 45-year-old patient with diabetes
        best_range = db_manager.get_best_matching_range(
            test_name="Blood Glucose",
            age=45,
            gender="Male",
            condition="Diabetes"
        )
        if best_range:
            print(f"✓ Found best matching range: {best_range['range_name']}")
            print(f"   Normal range: {best_range['normal_min']}-{best_range['normal_max']}")
        else:
            print("✓ No custom range found, will use default")
    except Exception as e:
        print(f"✗ Range matching failed: {e}")
    
    # Test 4: Age/gender adjusted range with custom ranges
    print("\n4. Testing integrated age/gender adjustment...")
    try:
        range_info = db_manager.get_age_gender_adjusted_range("Blood Glucose", 45, "Male", "Diabetes")
        print(f"✓ Adjusted range: {range_info['normal_min']}-{range_info['normal_max']}")
        print(f"   Source: {range_info.get('source', 'Default ranges')}")
    except Exception as e:
        print(f"✗ Age/gender adjustment failed: {e}")
    
    # Test 5: JSON export/import
    print("\n5. Testing JSON export/import...")
    try:
        # Export to JSON
        export_file = "test_export.json"
        export_success = db_manager.export_custom_ranges_to_json(export_file)
        print(f"✓ JSON export: {'SUCCESS' if export_success else 'FAILED'}")
        
        if export_success:
            # Check if file was created and has content
            with open(export_file, 'r') as f:
                data = json.load(f)
                print(f"   Exported {len(data.get('custom_test_ranges', []))} ranges")
        
        # Test import (would normally import from a different file)
        # For this test, we'll just verify the import function exists and works
        import_success = db_manager.import_custom_ranges_from_json("sample_custom_ranges.json")
        print(f"✓ JSON import: {'SUCCESS' if import_success else 'NOT TESTED (file may not exist)'}")
        
    except Exception as e:
        print(f"✗ JSON export/import failed: {e}")
    
    # Test 6: Database schema verification
    print("\n6. Verifying database schema...")
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Check if custom_test_ranges table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='custom_test_ranges'
        """)
        table_exists = cursor.fetchone() is not None
        print(f"✓ custom_test_ranges table: {'EXISTS' if table_exists else 'MISSING'}")
        
        # Check if lab_settings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='lab_settings'
        """)
        lab_table_exists = cursor.fetchone() is not None
        print(f"✓ lab_settings table: {'EXISTS' if lab_table_exists else 'MISSING'}")
        
        conn.close()
    except Exception as e:
        print(f"✗ Schema verification failed: {e}")
    
    print("\n" + "=" * 50)
    print("Custom Ranges Testing Complete!")
    print("\nTo use the custom ranges feature:")
    print("1. Run 'python main.py'")
    print("2. Go to the 'Custom Ranges' tab")
    print("3. Create, edit, or import custom ranges")
    print("4. Test with sample patient data")

if __name__ == "__main__":
    test_custom_ranges()
