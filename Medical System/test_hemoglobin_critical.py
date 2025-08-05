"""
Test script to verify critical thresholds are working correctly with Hemoglobin
"""

from database_manager import DatabaseManager
from report_generator import ReportGenerator

def test_hemoglobin_critical_thresholds():
    """Test critical threshold functionality with Hemoglobin which has explicit critical values"""
    
    # Initialize components
    db_manager = DatabaseManager()
    report_generator = ReportGenerator(db_manager)
    
    print("Testing Hemoglobin critical threshold functionality...")
    
    test_name = "Hemoglobin"
    print(f"\nTesting with: {test_name}")
    
    # Test age/gender adjusted range
    range_info = db_manager.get_age_gender_adjusted_range(test_name, 30, 'Male')
    print(f"Range info: {range_info}")
    
    # Test status determination with different values
    if range_info['normal_min'] and range_info['normal_max']:
        normal_min = range_info['normal_min']
        normal_max = range_info['normal_max']
        critical_low = range_info.get('critical_low')
        critical_high = range_info.get('critical_high')
        
        print(f"Normal range: {normal_min} - {normal_max}")
        print(f"Critical thresholds: {critical_low} - {critical_high}")
        
        # Test different values
        test_values = [
            5.0,   # Should be critical low (below 10.0)
            9.0,   # Should be low (below 12.0 normal min)
            14.0,  # Should be normal (between 12.0-17.0)
            18.0,  # Should be high (above 17.0 normal max)
            25.0   # Should be critical high (above 20.0)
        ]
        
        for test_value in test_values:
            status = report_generator.determine_test_status(
                test_value, normal_min, normal_max, test_name, 30, 'Male'
            )
            print(f"Value {test_value}: {status}")

if __name__ == "__main__":
    test_hemoglobin_critical_thresholds()
