#!/usr/bin/env python3
"""
Test script for duplicate detection in regular data processor
"""

import os
import sys
import tempfile
import pandas as pd
from database_manager import DatabaseManager
from data_processor import DataProcessor

def create_test_csv_for_regular_import():
    """Create a test CSV file for regular import with duplicates"""
    test_data = {
        'patient_id': ['P100', 'P100', 'P101'],
        'first_name': ['Alice', 'Alice', 'Bob'],
        'last_name': ['Johnson', 'Johnson', 'Wilson'],
        'date_of_birth': ['1985-03-20', '1985-03-20', '1992-07-15'],
        'gender': ['Female', 'Female', 'Male'],
        'test_name': ['Hemoglobin', 'Hemoglobin', 'Hemoglobin'],
        'test_value': [12.5, 12.5, 14.2],  # First two records are identical
        'test_date': ['2024-02-01', '2024-02-01', '2024-02-01'],
        'unit': ['g/dL', 'g/dL', 'g/dL']
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name

def test_regular_import_duplicates():
    """Test duplicate detection in regular data processor"""
    print("Testing Regular Import Duplicate Detection")
    print("=" * 50)
    
    # Use a temporary database for testing
    test_db_path = tempfile.mktemp(suffix='.db')
    
    try:
        # Initialize components
        db_manager = DatabaseManager(test_db_path)
        processor = DataProcessor(db_manager)
        
        # Create test CSV with duplicates
        test_file = create_test_csv_for_regular_import()
        print(f"📄 Created test file: {test_file}")
        
        # Test 1: Import with duplicate checking enabled
        print("\n1. Testing regular import WITH duplicate checking...")
        success, message, stats = processor.import_csv_data(
            test_file, 
            update_existing=False,
            check_duplicates=True
        )
        
        print(f"Success: {success}")
        print(f"Message: {message}")
        print(f"Stats: {stats}")
        
        # Check total records in database
        all_patients = db_manager.get_all_patients()
        print(f"Total patients in database: {len(all_patients)}")
        
        total_test_results = 0
        for patient in all_patients:
            patient_id = patient[0]
            results = db_manager.get_patient_test_results(patient_id)
            total_test_results += len(results)
            print(f"  Patient {patient_id}: {len(results)} test results")
        
        print(f"Total test results: {total_test_results}")
        print(f"Expected: 2 test results (1 duplicate should be skipped)")
        print(f"Duplicates skipped: {stats.get('duplicates_skipped', 0)}")
        
        # Test 2: Import without duplicate checking
        print("\n2. Testing regular import WITHOUT duplicate checking...")
        success2, message2, stats2 = processor.import_csv_data(
            test_file, 
            update_existing=False,
            check_duplicates=False
        )
        
        print(f"Success: {success2}")
        print(f"Message: {message2}")
        print(f"Stats: {stats2}")
        
        # Final check
        total_test_results_final = 0
        for patient in all_patients:
            patient_id = patient[0]
            results = db_manager.get_patient_test_results(patient_id)
            total_test_results_final += len(results)
        
        print(f"\nFinal total test results: {total_test_results_final}")
        print(f"Expected: 5 test results (2 + 3)")
        
        print("\n" + "=" * 50)
        print("✅ Regular Import Duplicate Detection Test Complete!")
        
        # Show summary
        if (stats.get('duplicates_skipped', 0) == 1 and 
            stats.get('test_results_added', 0) == 2 and
            stats2.get('test_results_added', 0) == 3):
            print("🎉 All tests PASSED! Regular import duplicate detection is working correctly.")
        else:
            print("❌ Some tests FAILED. Please check the implementation.")
            print(f"  Expected: 1 duplicate skipped, 2 results added first time, 3 results added second time")
            print(f"  Actual: {stats.get('duplicates_skipped', 0)} duplicates skipped, {stats.get('test_results_added', 0)} results added first time, {stats2.get('test_results_added', 0)} results added second time")
            
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up test files
        try:
            if 'test_file' in locals():
                os.unlink(test_file)
            if os.path.exists(test_db_path):
                os.unlink(test_db_path)
        except:
            pass

if __name__ == "__main__":
    test_regular_import_duplicates()
