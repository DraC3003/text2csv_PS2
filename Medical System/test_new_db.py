import sqlite3
from typing import List, Tuple, Optional

class TestDatabaseManager:
    def __init__(self):
        self.db_path = 'medical_test_data.db'
    
    def get_test_types(self) -> List[Tuple]:
        """Get all available test types"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT test_type_id, test_name, normal_min, normal_max, unit, description, category,
                       critical_low, critical_high, method 
                FROM test_types ORDER BY test_name
            ''')
            return cursor.fetchall()

# Test the new implementation
print("Testing new DatabaseManager implementation...")
db = TestDatabaseManager()
test_types = db.get_test_types()
print(f'Found {len(test_types)} test types')
for test_type in test_types:
    critical_low = test_type[7] if len(test_type) > 7 else "N/A"
    critical_high = test_type[8] if len(test_type) > 8 else "N/A"
    print(f'Test: {test_type[1]}, Length: {len(test_type)}, Critical: {critical_low}-{critical_high}')
