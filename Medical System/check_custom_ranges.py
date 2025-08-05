from database_manager import DatabaseManager

db = DatabaseManager()
custom_ranges = db.get_custom_test_ranges()
print(f'Found {len(custom_ranges)} custom ranges:')
for i, range_data in enumerate(custom_ranges):
    print(f'Range {i+1}: {range_data}')
    if len(range_data) >= 11:
        range_name = range_data[2]
        gender = range_data[5]
        critical_low = range_data[9]
        critical_high = range_data[10]
        print(f'  Name: {range_name}, Gender: {gender}, Critical: {critical_low}-{critical_high}')
