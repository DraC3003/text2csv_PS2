#!/usr/bin/env python3
"""
Test script for duplicate detection functionality
"""

import os
import sys
import tempfile
import pandas as pd
from database_manager import DatabaseManager
from flexible_data_processor import FlexibleDataProcessor

def create_test_csv_with_duplicates():
    """Create a test CSV file with duplicate records"""
    test_data = {
        'patient_id': ['P001', 'P001', 'P001', 'P002', 'P002'],
        'first_name': ['John', 'John', 'John', 'Jane', 'Jane'],
        'last_name': ['Doe', 'Doe', 'Doe', 'Smith', 'Smith'],
        'age': [45, 45, 45, 30, 30],
        'gender': ['Male', 'Male', 'Male', 'Female', 'Female'],
        'test_name': ['Blood Glucose', 'Blood Glucose', 'Cholesterol', 'Blood Glucose', 'Blood Glucose'],
        'test_value': [95.5, 95.5, 180.0, 88.2, 88.2],  # First and second P001 records are identical
        'test_date': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-16', '2024-01-16'],  # Last P002 records are identical
        'unit': ['mg/dL', 'mg/dL', 'mg/dL', 'mg/dL', 'mg/dL']
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name

def test_duplicate_detection():
    """Test the duplicate detection functionality"""
    print("Testing Duplicate Detection System")
    print("=" * 50)
    
    # Use a temporary database for testing
    test_db_path = tempfile.mktemp(suffix='.db')
    
    try:
        # Initialize components
        db_manager = DatabaseManager(test_db_path)
        processor = FlexibleDataProcessor(db_manager)
        
        # Create test CSV with duplicates
        test_file = create_test_csv_with_duplicates()
        print(f"📄 Created test file: {test_file}")
        
        # Test 1: Import with duplicate checking enabled
        print("\n1. Testing import WITH duplicate checking...")
        success, message, imported_count = processor.import_flexible_csv(
            test_file, 
            {
                'patient_id': 'patient_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'age': 'age',
                'gender': 'gender',
                'test_name': 'test_name',
                'test_value': 'test_value',
                'test_date': 'test_date',
                'unit': 'unit'
            },
            check_duplicates=True
        )
        
        print(f"Success: {success}")
        print(f"Message: {message}")
        print(f"Imported Count: {imported_count}")
        
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
        print(f"Expected: 3 test results (2 duplicates should be skipped)")
        
        # Test 2: Try to import the same data again (should skip all as duplicates)
        print("\n2. Testing re-import of same data...")
        success2, message2, imported_count2 = processor.import_flexible_csv(
            test_file, 
            {
                'patient_id': 'patient_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'age': 'age',
                'gender': 'gender',
                'test_name': 'test_name',
                'test_value': 'test_value',
                'test_date': 'test_date',
                'unit': 'unit'
            },
            check_duplicates=True
        )
        
        print(f"Success: {success2}")
        print(f"Message: {message2}")
        print(f"Imported Count: {imported_count2}")
        print(f"Expected: 0 new imports (all should be duplicates)")
        
        # Test 3: Import without duplicate checking
        print("\n3. Testing import WITHOUT duplicate checking...")
        success3, message3, imported_count3 = processor.import_flexible_csv(
            test_file, 
            {
                'patient_id': 'patient_id',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'age': 'age',
                'gender': 'gender',
                'test_name': 'test_name',
                'test_value': 'test_value',
                'test_date': 'test_date',
                'unit': 'unit'
            },
            check_duplicates=False
        )
        
        print(f"Success: {success3}")
        print(f"Message: {message3}")
        print(f"Imported Count: {imported_count3}")
        print(f"Expected: 5 new imports (all records should be added despite duplicates)")
        
        # Final check
        total_test_results_final = 0
        for patient in all_patients:
            patient_id = patient[0]
            results = db_manager.get_patient_test_results(patient_id)
            total_test_results_final += len(results)
        
        print(f"\nFinal total test results: {total_test_results_final}")
        print(f"Expected: 8 test results (3 + 0 + 5)")
        
        print("\n" + "=" * 50)
        print("✅ Duplicate Detection Test Complete!")
        
        # Show summary
        if total_test_results == 3 and imported_count2 == 0 and imported_count3 == 5:
            print("🎉 All tests PASSED! Duplicate detection is working correctly.")
        else:
            print("❌ Some tests FAILED. Please check the implementation.")
            
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
    test_duplicate_detection()
