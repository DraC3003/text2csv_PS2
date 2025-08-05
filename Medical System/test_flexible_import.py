#!/usr/bin/env python3
"""
Test script for the flexible CSV import system
"""

import sys
import os
from flexible_data_processor import FlexibleDataProcessor
from database_manager import DatabaseManager

def test_flexible_import():
    """Test the flexible CSV import functionality"""
    print("Testing Flexible CSV Import System")
    print("=" * 50)
    
    try:
        # Initialize components
        db_manager = DatabaseManager()
        processor = FlexibleDataProcessor(db_manager)
        
        # Test file path
        test_file = "sample_device_data.csv"
        
        if not os.path.exists(test_file):
            print(f"✗ Test file not found: {test_file}")
            return
        
        print(f"📄 Testing with file: {test_file}")
        
        # Step 1: Preview and analyze the file
        print("\n1. Analyzing CSV file...")
        success, message, preview_df, mapping = processor.preview_csv_with_mapping(test_file)
        
        if not success:
            print(f"✗ File analysis failed: {message}")
            return
        
        print(f"✓ File analysis successful: {message}")
        print(f"📊 Found {len(preview_df)} rows, {len(preview_df.columns)} columns")
        
        # Step 2: Show detected mappings
        print("\n2. Auto-detected column mappings:")
        if mapping:
            for field, column in mapping.items():
                print(f"   {field:15} → {column}")
        else:
            print("   No automatic mappings detected")
        
        # Step 3: Show original columns
        print(f"\n3. Original CSV columns:")
        for i, col in enumerate(preview_df.columns):
            print(f"   {i+1:2}. {col}")
        
        # Step 4: Show preview data
        print("\n4. Data preview (first 3 rows):")
        print(preview_df.head(3).to_string(index=False))
        
        # Step 5: Test data cleaning
        print("\n5. Testing data cleaning...")
        cleaned_df = processor.clean_and_convert_data(preview_df, mapping)
        print(f"✓ Data cleaned: {len(cleaned_df)} rows, {len(cleaned_df.columns)} columns")
        
        if not cleaned_df.empty:
            print("   Cleaned columns:", list(cleaned_df.columns))
            print("\n   Sample cleaned data:")
            print(cleaned_df.head(2).to_string(index=False))
        
        # Step 6: Test validation
        print("\n6. Testing data validation...")
        is_valid, errors, final_df = processor.validate_processed_data(cleaned_df)
        
        if is_valid:
            print(f"✓ Data validation passed: {len(final_df)} valid rows")
        else:
            print("⚠️ Data validation issues found:")
            for error in errors:
                print(f"   • {error}")
        
        if errors:
            print("   Validation warnings:")
            for error in errors:
                print(f"   • {error}")
        
        # Step 7: Test import (dry run)
        print("\n7. Testing import process...")
        success, import_message, imported_count = processor.import_flexible_csv(
            test_file, mapping
        )
        
        if success:
            print(f"✓ Import test successful: {imported_count} rows imported")
            print(f"   Message: {import_message}")
        else:
            print(f"✗ Import test failed: {import_message}")
        
        print("\n" + "=" * 50)
        print("✅ Flexible CSV Import System Test Complete!")
        print("\nTo use in the application:")
        print("1. Run 'python main.py'")
        print("2. Go to 'Flexible CSV Import' tab")
        print("3. Select your CSV file")
        print("4. Verify column mappings")
        print("5. Import data")
        
    except Exception as e:
        print(f"✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_flexible_import()
