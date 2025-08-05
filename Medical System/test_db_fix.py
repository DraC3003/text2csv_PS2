from database_manager import DatabaseManager

db = DatabaseManager()
test_types = db.get_test_types()
print('Database Manager Results:')
for test_type in test_types:
    critical_low = test_type[7] if len(test_type) > 7 else "N/A"
    critical_high = test_type[8] if len(test_type) > 8 else "N/A"
    print(f'Test: {test_type[1]}, Length: {len(test_type)}, Critical: {critical_low}-{critical_high}')
