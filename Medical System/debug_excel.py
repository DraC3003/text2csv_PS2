#!/usr/bin/env python3
"""
Debug script to test Excel generation and see what's causing the unpacking error
"""

from database_manager import DatabaseManager
from report_generator import ReportGenerator
import traceback

def debug_excel_generation():
    """Debug the Excel generation issue"""
    try:
        # Initialize database
        db_manager = DatabaseManager()
        
        # Get all patients
        patients = db_manager.get_all_patients()
        print(f"Found {len(patients)} patients")
        
        if not patients:
            print("No patients found, creating sample data...")
            # Add a sample patient and test result
            db_manager.add_patient(
                patient_id="TEST001",
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-01",
                gender="Male"
            )
            
            # Add a test type if needed
            test_types = db_manager.get_test_types()
            if not test_types:
                print("No test types found, need to add some first")
                return
            
            # Add a test result
            db_manager.add_test_result(
                patient_id="TEST001",
                test_type_id=test_types[0][0],
                test_value=10.5,
                test_date="2024-01-01"
            )
            
            patients = db_manager.get_all_patients()
            print(f"After creating sample: {len(patients)} patients")
        
        # Test getting patient test results
        for patient in patients[:1]:  # Just test first patient
            patient_id = patient[0]
            print(f"\nTesting patient: {patient_id}")
            
            test_results = db_manager.get_patient_test_results(patient_id)
            print(f"Found {len(test_results)} test results")
            
            if test_results:
                for i, result in enumerate(test_results):
                    print(f"Result {i}: {len(result)} values")
                    print(f"Result {i}: {result}")
                    
                    # Try the unpacking that's failing
                    try:
                        result_id, _, test_name, test_value, normal_min, normal_max, unit, test_date, lab_tech, notes = result
                        print(f"Unpacking successful: {test_name} = {test_value}")
                    except ValueError as e:
                        print(f"Unpacking failed: {e}")
                        print(f"Result tuple length: {len(result)}")
                        print(f"Result content: {result}")
                        break
            
            break  # Just test first patient
        
        # Try Excel generation
        print("\n" + "="*50)
        print("Testing Excel generation...")
        report_gen = ReportGenerator(db_manager)
        
        success = report_gen.generate_all_patients_excel_report("test_report.xlsx")
        if success:
            print("Excel generation successful!")
        else:
            print("Excel generation failed!")
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_excel_generation()
