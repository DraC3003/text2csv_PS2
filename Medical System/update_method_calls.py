#!/usr/bin/env python3
"""
Update script to fix method call signatures after changing get_age_gender_adjusted_range
"""

import re

def update_file(filename):
    """Update a file to use the new range_info dictionary format"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Pattern 1: Replace the method call
    pattern1 = r'adj_min, adj_max = self\.db_manager\.get_age_gender_adjusted_range\(([^)]+)\)'
    replacement1 = r'range_info = self.db_manager.get_age_gender_adjusted_range(\1)'
    content = re.sub(pattern1, replacement1, content)
    
    # Pattern 2: Replace the None check
    pattern2 = r'if adj_min is not None and adj_max is not None:'
    replacement2 = r'if range_info[\'normal_min\'] is not None and range_info[\'normal_max\'] is not None:'
    content = re.sub(pattern2, replacement2, content)
    
    # Pattern 3: Replace the assignment
    pattern3 = r'normal_min, normal_max = adj_min, adj_max'
    replacement3 = r'normal_min, normal_max = range_info[\'normal_min\'], range_info[\'normal_max\']'
    content = re.sub(pattern3, replacement3, content)
    
    with open(filename, 'w') as f:
        f.write(content)
    
    print(f'Updated {filename}')

if __name__ == "__main__":
    # Update the files that use the old method signature
    update_file('report_generator.py')
    update_file('ui_components.py')
