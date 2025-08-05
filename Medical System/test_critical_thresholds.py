"""
Test script to verify critical thresholds are working correctly
"""

from database_manager import DatabaseManager
from report_generator import ReportGenerator

def test_critical_thresholds():
    """Test critical threshold functionality"""
    
    # Initialize components
    db_manager = DatabaseManager()
    report_generator = ReportGenerator(db_manager)
    
    print("Testing critical threshold functionality...")
    
    # Get test types
    test_types = db_manager.get_test_types()
    print(f"Found {len(test_types)} test types")
    
    if test_types:
        # Test the first test type
        test_type = test_types[0]
        test_name = test_type[1]
        print(f"\nTesting with: {test_name}")
        print(f"Test type structure: {test_type}")
        
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
                normal_min - 10,  # Should be critical low
                normal_min - 1,   # Should be low
                (normal_min + normal_max) / 2,  # Should be normal
                normal_max + 1,   # Should be high  
                normal_max + 10   # Should be critical high
            ]
            
            for test_value in test_values:
                status = report_generator.determine_test_status(
                    test_value, normal_min, normal_max, test_name, 30, 'Male'
                )
                print(f"Value {test_value}: {status}")

if __name__ == "__main__":
    test_critical_thresholds()
