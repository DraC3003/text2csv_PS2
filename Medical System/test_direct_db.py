import sqlite3

print("Direct database test...")
conn = sqlite3.connect('medical_test_data.db')
cursor = conn.cursor()

print("Testing explicit column selection:")
cursor.execute('''
    SELECT test_type_id, test_name, normal_min, normal_max, unit, description, category,
           critical_low, critical_high, method 
    FROM test_types ORDER BY test_name
''')
results = cursor.fetchall()
print(f"Found {len(results)} results")
for result in results:
    print(f"Row: {result} (Length: {len(result)})")

conn.close()
