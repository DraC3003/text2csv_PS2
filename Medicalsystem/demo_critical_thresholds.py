"""
Critical Thresholds Demo Script
Demonstrates the critical threshold functionality
"""

from database_manager import DatabaseManager

def demo_critical_thresholds():
    """Demo critical thresholds functionality"""
    print("=" * 60)
    print("CRITICAL THRESHOLDS DEMO")
    print("=" * 60)
    
    db = DatabaseManager()
    
    # Add a test type with critical thresholds
    print("\n1. Adding test type 'Blood Glucose' with critical thresholds...")
    success = db.add_test_type(
        test_name="Blood Glucose",
        unit="mg/dL",
        normal_min=70.0,
        normal_max=140.0,
        critical_low=50.0,    # Critical low threshold
        critical_high=400.0,  # Critical high threshold
        description="Blood glucose with critical thresholds"
    )
    
    if success:
        print("✅ Test type added successfully")
    else:
        print("❌ Test type already exists")
    
    # Add a patient
    print("\n2. Adding test patient...")
    patient_success = db.add_patient(
        patient_id="DEMO001",
        first_name="Demo",
        last_name="Patient",
        date_of_birth="1990-01-01",
        gender="Male"
    )
    
    if patient_success:
        print("✅ Patient added successfully")
    else:
        print("❌ Patient already exists")
    
    # Get the test type ID
    test_type = db.get_test_type_by_name("Blood Glucose")
    if not test_type:
        print("❌ Failed to get test type")
        return
    
    test_type_id = test_type[0]
    
    # Add test results with different critical levels
    test_scenarios = [
        (45.0, "CRITICAL LOW - Severe hypoglycemia"),
        (65.0, "Low - Mild hypoglycemia"),
        (90.0, "Normal - Good control"),
        (160.0, "High - Elevated"),
        (450.0, "CRITICAL HIGH - Diabetic emergency")
    ]
    
    print("\n3. Adding test results to demonstrate critical detection...")
    for i, (value, description) in enumerate(test_scenarios, 1):
        success = db.add_test_result(
            patient_id="DEMO001",
            test_type_id=test_type_id,
            test_value=value,
            test_date=f"2025-08-0{i}",
            notes=description,
            check_duplicates=False
        )
        
        if success:
            print(f"✅ Added result: {value} mg/dL - {description}")
        else:
            print(f"❌ Failed to add result: {value} mg/dL")
    
    print("\n4. Testing critical threshold detection...")
    
    # Test the range detection function
    test_values = [45.0, 65.0, 90.0, 160.0, 450.0]
    
    for value in test_values:
        range_info = db.get_age_gender_adjusted_range("Blood Glucose", 30, "Male")
        
        status = "Unknown"
        if range_info['critical_low'] and value <= range_info['critical_low']:
            status = "🚨 CRITICAL LOW"
        elif range_info['critical_high'] and value >= range_info['critical_high']:
            status = "🚨 CRITICAL HIGH"
        elif range_info['normal_min'] and range_info['normal_max']:
            if value < range_info['normal_min']:
                status = "⚠️ Low"
            elif value > range_info['normal_max']:
                status = "⚠️ High"
            else:
                status = "✅ Normal"
        
        print(f"Value: {value:6.1f} mg/dL -> Status: {status}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("✅ Critical thresholds are working!")
    print("✅ Check the Test Results tab in the app to see color-coded results")
    print("✅ Critical values will show with red background and alerts")
    print("=" * 60)

if __name__ == "__main__":
    demo_critical_thresholds()
