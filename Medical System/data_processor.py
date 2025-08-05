"""
Data Processor for Medical Test System
Handles CSV data import and processing functionality.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import List, Dict, Tuple, Optional
from database_manager import DatabaseManager

class DataProcessor:
    def __init__(self, db_manager: DatabaseManager):
        """Initialize data processor with database manager"""
        self.db_manager = db_manager
        
    def validate_csv_format(self, file_path: str) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Validate CSV file format and return validation results
        Returns: (is_valid, message, dataframe)
        """
        try:
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Check if file is empty
            if df.empty:
                return False, "CSV file is empty", None
            
            # Required columns for medical test data
            required_columns = ['patient_id', 'test_name', 'test_value', 'test_date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}", None
            
            # Check for valid data types and formats
            validation_errors = []
            
            # Validate patient IDs (should not be empty)
            if df['patient_id'].isnull().any():
                validation_errors.append("Patient ID cannot be empty")
            
            # Validate test values (should be numeric)
            non_numeric_values = df[~pd.to_numeric(df['test_value'], errors='coerce').notnull()]
            if not non_numeric_values.empty:
                validation_errors.append(f"Non-numeric test values found in rows: {non_numeric_values.index.tolist()}")
            
            # Validate date format
            try:
                pd.to_datetime(df['test_date'], errors='raise')
            except:
                validation_errors.append("Invalid date format in test_date column. Use YYYY-MM-DD format")
            
            if validation_errors:
                return False, "; ".join(validation_errors), df
            
            return True, "CSV format is valid", df
            
        except FileNotFoundError:
            return False, "File not found", None
        except pd.errors.EmptyDataError:
            return False, "CSV file is empty or corrupted", None
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}", None
    
    def preview_csv_data(self, file_path: str, num_rows: int = None) -> Tuple[bool, str, Optional[pd.DataFrame]]:
        """
        Preview CSV data - shows all rows by default for complete visibility
        Returns: (success, message, preview_dataframe)
        """
        is_valid, message, df = self.validate_csv_format(file_path)
        
        if not is_valid:
            return False, message, None
        
        # Show all rows by default, or limited rows if specified
        if num_rows is None:
            preview_df = df  # Show entire dataset
            row_count_msg = f"all {len(df)} rows"
        else:
            preview_df = df.head(num_rows)
            row_count_msg = f"first {num_rows} rows"
        
        return True, f"Preview of {row_count_msg}", preview_df
    
    def clean_and_standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the imported data"""
        cleaned_df = df.copy()
        
        # Clean patient IDs (remove extra spaces, convert to uppercase)
        cleaned_df['patient_id'] = cleaned_df['patient_id'].astype(str).str.strip().str.upper()
        
        # Clean test names (standardize capitalization)
        cleaned_df['test_name'] = cleaned_df['test_name'].str.strip().str.title()
        
        # Convert test values to numeric
        cleaned_df['test_value'] = pd.to_numeric(cleaned_df['test_value'], errors='coerce')
        
        # Standardize date format
        cleaned_df['test_date'] = pd.to_datetime(cleaned_df['test_date']).dt.strftime('%Y-%m-%d')
        
        # Clean optional columns if they exist
        if 'lab_technician' in cleaned_df.columns:
            cleaned_df['lab_technician'] = cleaned_df['lab_technician'].astype(str).str.strip()
            cleaned_df['lab_technician'] = cleaned_df['lab_technician'].replace('nan', '')
        
        if 'notes' in cleaned_df.columns:
            cleaned_df['notes'] = cleaned_df['notes'].astype(str).str.strip()
            cleaned_df['notes'] = cleaned_df['notes'].replace('nan', '')
        
        # Remove rows with null test values (critical data)
        cleaned_df = cleaned_df.dropna(subset=['test_value'])
        
        return cleaned_df
    
    def extract_patient_info_from_csv(self, df: pd.DataFrame) -> List[Dict]:
        """Extract unique patient information from CSV data"""
        patient_columns = ['patient_id']
        optional_patient_columns = ['first_name', 'last_name', 'date_of_birth', 
                                   'gender', 'phone', 'email', 'address']
        
        # Get columns that exist in the dataframe
        available_columns = [col for col in patient_columns + optional_patient_columns 
                           if col in df.columns]
        
        # Get unique patients
        unique_patients = df[available_columns].drop_duplicates(subset=['patient_id'])
        
        patients_list = []
        for _, row in unique_patients.iterrows():
            patient_info = {'patient_id': row['patient_id']}
            
            for col in optional_patient_columns:
                if col in row and pd.notna(row[col]):
                    value = str(row[col]).strip()
                    # Special handling for date_of_birth
                    if col == 'date_of_birth':
                        try:
                            # Ensure proper date format
                            parsed_date = pd.to_datetime(value)
                            patient_info[col] = parsed_date.strftime('%Y-%m-%d')
                        except:
                            continue  # Skip invalid dates
                    else:
                        patient_info[col] = value
            
            patients_list.append(patient_info)
        
        return patients_list
    
    def import_csv_data(self, file_path: str, update_existing: bool = False, 
                       check_duplicates: bool = True) -> Tuple[bool, str, Dict]:
        """
        Import CSV data into the database
        
        Args:
            file_path: Path to the CSV file
            update_existing: Whether to update existing patient information
            check_duplicates: Whether to check for and skip duplicate test results
            
        Returns: (success, message, import_stats)
        """
        # Validate CSV format
        is_valid, validation_message, df = self.validate_csv_format(file_path)
        if not is_valid:
            return False, validation_message, {}
        
        # Clean and standardize data
        cleaned_df = self.clean_and_standardize_data(df)
        
        import_stats = {
            'total_rows': len(df),
            'processed_rows': len(cleaned_df),
            'patients_added': 0,
            'patients_updated': 0,
            'test_results_added': 0,
            'duplicates_skipped': 0,
            'test_types_added': 0,
            'errors': []
        }
        
        try:
            # Extract and process patient information
            patients_to_process = self.extract_patient_info_from_csv(cleaned_df)
            
            for patient_info in patients_to_process:
                patient_id = patient_info['patient_id']
                existing_patient = self.db_manager.get_patient(patient_id)
                
                if existing_patient is None:
                    # Add new patient
                    success = self.db_manager.add_patient(**patient_info)
                    if success:
                        import_stats['patients_added'] += 1
                    else:
                        import_stats['errors'].append(f"Failed to add patient {patient_id}")
                elif update_existing:
                    # Update existing patient with new information
                    update_data = {k: v for k, v in patient_info.items() if k != 'patient_id'}
                    if update_data:
                        success = self.db_manager.update_patient(patient_id, **update_data)
                        if success:
                            import_stats['patients_updated'] += 1
            
            # Process test results
            for _, row in cleaned_df.iterrows():
                # Get or create test type
                test_type = self.db_manager.get_test_type_by_name(row['test_name'])
                if test_type is None:
                    # Add new test type with default values
                    success = self.db_manager.add_test_type(
                        test_name=row['test_name'],
                        unit=row.get('unit', ''),
                        description=f"Imported test type: {row['test_name']}"
                    )
                    if success:
                        import_stats['test_types_added'] += 1
                        test_type = self.db_manager.get_test_type_by_name(row['test_name'])
                    else:
                        import_stats['errors'].append(f"Failed to create test type: {row['test_name']}")
                        continue
                
                # Add test result
                lab_technician = row.get('lab_technician', '')
                notes = row.get('notes', '')
                
                success = self.db_manager.add_test_result(
                    patient_id=row['patient_id'],
                    test_type_id=test_type[0],  # test_type_id is the first column
                    test_value=float(row['test_value']),
                    test_date=row['test_date'],
                    lab_technician=lab_technician if lab_technician != '' else None,
                    notes=notes if notes != '' else None,
                    check_duplicates=check_duplicates
                )
                
                if success:
                    import_stats['test_results_added'] += 1
                else:
                    # Could be either duplicate or error - check if it's a duplicate
                    is_duplicate = self.db_manager.check_duplicate_test_result(
                        patient_id=row['patient_id'],
                        test_type_id=test_type[0],
                        test_value=float(row['test_value']),
                        test_date=row['test_date']
                    )
                    if is_duplicate:
                        import_stats['duplicates_skipped'] += 1
                    else:
                        import_stats['errors'].append(f"Failed to add test result for patient {row['patient_id']}")
            
            # Generate success message
            success_message = f"""Import completed successfully!
            - Processed {import_stats['processed_rows']} out of {import_stats['total_rows']} rows
            - Added {import_stats['patients_added']} new patients
            - Updated {import_stats['patients_updated']} existing patients
            - Added {import_stats['test_results_added']} test results
            - Added {import_stats['test_types_added']} new test types"""
            
            if import_stats['duplicates_skipped'] > 0:
                success_message += f"\n- Skipped {import_stats['duplicates_skipped']} duplicate test results"
            
            if import_stats['errors']:
                success_message += f"\n- {len(import_stats['errors'])} errors occurred"
            
            return True, success_message, import_stats
            
        except Exception as e:
            return False, f"Import failed: {str(e)}", import_stats
    
    def generate_csv_template(self, file_path: str) -> bool:
        """Generate a CSV template file for data import"""
        try:
            template_data = {
                'patient_id': ['P001', 'P002', 'P001', 'P003'],
                'first_name': ['John', 'Jane', 'John', 'Mike'],
                'last_name': ['Doe', 'Smith', 'Doe', 'Brown'],
                'date_of_birth': ['1980-05-15', '1950-08-22', '1980-05-15', '1990-12-03'],
                'gender': ['Male', 'Female', 'Male', 'Male'],
                'test_name': ['Hemoglobin', 'Blood Glucose', 'Cholesterol Total', 'Creatinine'],
                'test_value': [14.5, 95, 180, 1.1],
                'test_date': ['2025-01-15', '2025-01-15', '2025-01-16', '2025-01-14'],
                'unit': ['g/dL', 'mg/dL', 'mg/dL', 'mg/dL'],
                'lab_technician': ['Dr. Johnson', 'Lab Tech A', 'Dr. Johnson', 'Dr. Smith'],
                'notes': ['Normal for adult male', 'Fasting', 'Slightly elevated', 'Normal kidney function']
            }
            
            template_df = pd.DataFrame(template_data)
            template_df.to_csv(file_path, index=False)
            return True
        except Exception:
            return False
    
    def validate_test_value_ranges(self, df: pd.DataFrame) -> List[Dict]:
        """Validate test values against normal ranges and return warnings"""
        warnings = []
        
        for _, row in df.iterrows():
            test_type = self.db_manager.get_test_type_by_name(row['test_name'])
            if test_type and test_type[2] is not None and test_type[3] is not None:
                normal_min = test_type[2]
                normal_max = test_type[3]
                test_value = float(row['test_value'])
                
                if test_value < normal_min or test_value > normal_max:
                    warnings.append({
                        'patient_id': row['patient_id'],
                        'test_name': row['test_name'],
                        'test_value': test_value,
                        'normal_range': f"{normal_min}-{normal_max}",
                        'status': 'HIGH' if test_value > normal_max else 'LOW'
                    })
        
        return warnings
    
    def get_import_summary(self, file_path: str) -> Dict:
        """Get a summary of what would be imported from a CSV file"""
        is_valid, message, df = self.validate_csv_format(file_path)
        
        if not is_valid:
            return {'valid': False, 'message': message}
        
        cleaned_df = self.clean_and_standardize_data(df)
        patients = self.extract_patient_info_from_csv(cleaned_df)
        warnings = self.validate_test_value_ranges(cleaned_df)
        
        # Count unique test types
        unique_tests = cleaned_df['test_name'].nunique()
        
        summary = {
            'valid': True,
            'message': 'CSV file is ready for import',
            'total_rows': len(df),
            'valid_rows': len(cleaned_df),
            'unique_patients': len(patients),
            'unique_test_types': unique_tests,
            'range_warnings': len(warnings),
            'warnings_detail': warnings[:10]  # Show first 10 warnings
        }
        
        return summary
