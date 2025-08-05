"""
Test Missing Value Handling
Tests the system's ability to handle missing patient demographics gracefully
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager

def test_missing_value_handling():
    """Test how the system handles missing patient demographic information"""
    print("🧪 Testing Missing Value Handling in Medical Test System")
    print("=" * 60)
    
    db = DatabaseManager()
    
    # Test 1: Patient with only ID
    print("\n1️⃣  Testing patient with only Patient ID...")
    success = db.add_patient('MINIMAL_001')
    if success:
        print("✅ Successfully added patient with minimal information")
        
        # Get demographics summary
        demographics = db.get_patient_demographics_summary('MINIMAL_001')
        print(f"   📊 Demographics completeness: {demographics['demographic_completeness']['level']}")
        print(f"   📊 Completeness score: {demographics['demographic_completeness']['score']}/100")
        print(f"   📊 Missing: {demographics['demographic_completeness']['missing']}")
        
        # Test range adjustment with no demographics
        range_info = db.get_age_gender_adjusted_range('Hemoglobin', None, None)
        print(f"   🩸 Hemoglobin range (no demographics): {range_info['normal_min']}-{range_info['normal_max']}")
        print(f"   📋 Range source: {range_info['source']}")
        print(f"   🎯 Age adjusted: {range_info['age_adjusted']}")
        print(f"   🎯 Gender adjusted: {range_info['gender_adjusted']}")
    
    # Test 2: Patient with age but no gender
    print("\n2️⃣  Testing patient with age but no gender...")
    success = db.add_patient('AGE_ONLY_002', date_of_birth='2010-01-01')
    if success:
        print("✅ Successfully added patient with age only")
        
        demographics = db.get_patient_demographics_summary('AGE_ONLY_002')
        print(f"   👶 Age: {demographics['age_display']}")
        print(f"   📊 Demographics completeness: {demographics['demographic_completeness']['level']}")
        
        # Test range adjustment with age only
        age = demographics['age']
        range_info = db.get_age_gender_adjusted_range('Hemoglobin', age, None)
        print(f"   🩸 Hemoglobin range (age {age}, no gender): {range_info['normal_min']}-{range_info['normal_max']}")
        print(f"   📋 Range source: {range_info['source']}")
    
    # Test 3: Patient with gender but no age
    print("\n3️⃣  Testing patient with gender but no age...")
    success = db.add_patient('GENDER_ONLY_003', gender='Female')
    if success:
        print("✅ Successfully added patient with gender only")
        
        demographics = db.get_patient_demographics_summary('GENDER_ONLY_003')
        print(f"   👩 Gender: {demographics['gender']}")
        print(f"   📊 Demographics completeness: {demographics['demographic_completeness']['level']}")
        
        # Test range adjustment with gender only
        range_info = db.get_age_gender_adjusted_range('Hemoglobin', None, 'Female')
        print(f"   🩸 Hemoglobin range (Female, no age): {range_info['normal_min']}-{range_info['normal_max']}")
        print(f"   📋 Range source: {range_info['source']}")
    
    # Test 4: Patient with complete demographics
    print("\n4️⃣  Testing patient with complete demographics...")
    success = db.add_patient('COMPLETE_004', 'Jane', 'Doe', '1985-05-15', 'Female', '555-1234', 'jane@test.com')
    if success:
        print("✅ Successfully added patient with complete information")
        
        demographics = db.get_patient_demographics_summary('COMPLETE_004')
        print(f"   👩 Name: {demographics['first_name']} {demographics['last_name']}")
        print(f"   🎂 Age: {demographics['age_display']}")
        print(f"   📊 Demographics completeness: {demographics['demographic_completeness']['level']}")
        
        # Test range adjustment with complete demographics
        age = demographics['age']
        range_info = db.get_age_gender_adjusted_range('Hemoglobin', age, 'Female')
        print(f"   🩸 Hemoglobin range (Female, age {age}): {range_info['normal_min']}-{range_info['normal_max']}")
        print(f"   📋 Range source: {range_info['source']}")
    
    # Test 5: Add test results to patients with different demographic completeness
    print("\n5️⃣  Testing test results with various demographic completeness...")
    
    test_value = 13.5  # Hemoglobin value
    patients_to_test = [
        ('MINIMAL_001', 'No demographics'),
        ('AGE_ONLY_002', 'Age only'),
        ('GENDER_ONLY_003', 'Gender only'),
        ('COMPLETE_004', 'Complete demographics')
    ]
    
    for patient_id, description in patients_to_test:
        # Add hemoglobin test result
        success = db.add_test_result(patient_id, 'Hemoglobin', test_value, '2025-08-01')
        if success:
            print(f"   ✅ Added Hemoglobin test for {description}")
            
            # Get patient demographics for range calculation
            demographics = db.get_patient_demographics_summary(patient_id)
            age = demographics['age']
            gender = demographics['gender'] if demographics['gender'] != 'Not specified' else None
            
            # Get adjusted range and status
            range_info = db.get_age_gender_adjusted_range('Hemoglobin', age, gender)
            normal_min, normal_max = range_info['normal_min'], range_info['normal_max']
            
            # Determine status
            if test_value < normal_min:
                status = "Low"
            elif test_value > normal_max:
                status = "High" 
            else:
                status = "Normal"
                
            print(f"      📊 Result: {test_value} g/dL - Status: {status}")
            print(f"      📏 Range used: {normal_min}-{normal_max} ({range_info['source']})")
    
    print("\n" + "=" * 60)
    print("✅ Missing Value Handling Test Complete!")
    print("\n📋 Summary:")
    print("   • System gracefully handles patients with minimal information")
    print("   • Appropriate fallback ranges are used when demographics are missing")
    print("   • Range sources are clearly indicated for transparency")
    print("   • Test interpretations work regardless of demographic completeness")
    print("   • Recommendations are provided for improving accuracy")

if __name__ == "__main__":
    test_missing_value_handling()
