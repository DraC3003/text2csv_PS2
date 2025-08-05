"""
Flexible Data Processor for Medical Test System
Handles CSV data import with intelligent column mapping for various medical device formats.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re
from typing import List, Dict, Tuple, Optional, Any
from database_manager import DatabaseManager

class FlexibleDataProcessor:
    def __init__(self, db_manager: DatabaseManager):
        """Initialize flexible data processor with database manager"""
        self.db_manager = db_manager
        
        # Define column mapping patterns for intelligent detection
        self.column_patterns = {
            'patient_id': [
                'patient_id', 'patientid', 'patient id', 'pid', 'id',
                'patient_id_biocheq', 'barcode_id', 'barcode id'
            ],
            'age': [
                'age', 'patient_age', 'age_years', 'years'
            ],
            'gender': [
                'gender', 'sex', 'patient_gender', 'male_female', 'm/f'
            ],
            'test_name': [
                'test_name', 'testname', 'test name', 'test_type', 'test type',
                'parameters', 'analyte', 'test', 'parameter'
            ],
            'test_value': [
                'test_value', 'testvalue', 'test value', 'value', 'result',
                'reading', 'measurement', 'concentration', 'level'
            ],
            'test_date': [
                'test_date', 'testdate', 'test date', 'date', 'date_time',
                'date & time', 'timestamp', 'collection_date'
            ],
            'first_name': [
                'first_name', 'firstname', 'first name', 'fname', 'given_name'
            ],
            'last_name': [
                'last_name', 'lastname', 'last name', 'lname', 'surname', 'family_name'
            ],
            'unit': [
                'unit', 'units', 'measurement_unit', 'test_unit'
            ],
            'lab_technician': [
                'lab_technician', 'technician', 'operator', 'tech', 'performed_by'
            ],
            'notes': [
                'notes', 'comments', 'remarks', 'observation'
            ]
        }
        
        # Useless columns to ignore
        self.ignore_patterns = [
            'sr.', 'sr no', 'serial', 'device_id', 'device id', 'bio-cheq',
            'biocheq', 'opd/ipd', 'opd', 'ipd', 'unused', 'empty', 'blank'
        ]
        
    def detect_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Intelligently detect column mappings from CSV headers
        Returns a dictionary mapping standard field names to actual column names
        """
        column_mapping = {}
        available_columns = [col.lower().strip() for col in df.columns]
        
        for standard_field, patterns in self.column_patterns.items():
            best_match = None
            best_score = 0
            
            for pattern in patterns:
                pattern_lower = pattern.lower()
                
                # Look for exact matches first
                for i, col in enumerate(available_columns):
                    if col == pattern_lower:
                        best_match = df.columns[i]
                        best_score = 100
                        break
                
                # If no exact match, look for partial matches
                if best_score < 100:
                    for i, col in enumerate(available_columns):
                        if pattern_lower in col or col in pattern_lower:
                            score = len(pattern_lower) / max(len(col), len(pattern_lower)) * 50
                            if score > best_score:
                                best_match = df.columns[i]
                                best_score = score
            
            if best_match and best_score > 30:  # Minimum confidence threshold
                column_mapping[standard_field] = best_match
                
        return column_mapping
    
    def preview_csv_with_mapping(self, file_path: str, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[pd.DataFrame], Optional[Dict[str, str]]]:
        """
        Preview CSV file with intelligent column mapping
        Returns: (success, message, dataframe, column_mapping)
        """
        try:
            # Try multiple encodings
            encodings_to_try = [encoding, 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            df = None
            
            for enc in encodings_to_try:
                try:
                    df = pd.read_csv(file_path, encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                return False, "Could not read CSV file with any encoding", None, None
            
            # Check if file is empty
            if df.empty:
                return False, "CSV file is empty", None, None
            
            # Remove completely empty columns
            df = df.dropna(axis=1, how='all')
            
            # Detect column mapping
            column_mapping = self.detect_column_mapping(df)
            
            # Create a preview with mapped columns - show all data for complete visibility
            preview_df = df.copy()  # Show all rows instead of limiting to 10
            
            # Check if we found essential columns
            essential_fields = ['patient_id', 'test_value']
            missing_essential = [field for field in essential_fields if field not in column_mapping]
            
            if missing_essential:
                message = f"Could not auto-detect columns: {', '.join(missing_essential)}. Please verify column mapping."
            else:
                message = f"Successfully detected {len(column_mapping)} column mappings."
            
            return True, message, preview_df, column_mapping
            
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}", None, None
    
    def clean_and_convert_data(self, df: pd.DataFrame, column_mapping: Dict[str, str]) -> pd.DataFrame:
        """
        Clean and convert data based on column mapping
        """
        cleaned_df = pd.DataFrame()
        
        # Map columns to standard names
        for standard_field, actual_column in column_mapping.items():
            if actual_column in df.columns:
                cleaned_df[standard_field] = df[actual_column]
        
        # Clean and convert data types
        if 'patient_id' in cleaned_df.columns:
            # Clean patient IDs - remove spaces, convert to string
            cleaned_df['patient_id'] = cleaned_df['patient_id'].astype(str).str.strip()
            cleaned_df['patient_id'] = cleaned_df['patient_id'].replace(['nan', 'NaN', ''], np.nan)
        
        if 'age' in cleaned_df.columns:
            # Convert age to numeric, handle various formats
            cleaned_df['age'] = pd.to_numeric(cleaned_df['age'], errors='coerce')
        
        if 'gender' in cleaned_df.columns:
            # Standardize gender values
            gender_mapping = {
                'm': 'Male', 'male': 'Male', 'man': 'Male', '1': 'Male',
                'f': 'Female', 'female': 'Female', 'woman': 'Female', '2': 'Female',
                'o': 'Other', 'other': 'Other', 'unknown': 'Other'
            }
            cleaned_df['gender'] = cleaned_df['gender'].astype(str).str.lower().str.strip()
            cleaned_df['gender'] = cleaned_df['gender'].map(gender_mapping).fillna('Other')
        
        if 'test_value' in cleaned_df.columns:
            # Convert test values to numeric
            cleaned_df['test_value'] = pd.to_numeric(cleaned_df['test_value'], errors='coerce')
        
        if 'test_date' in cleaned_df.columns:
            # Try to parse various date formats
            cleaned_df['test_date'] = self.parse_flexible_date(cleaned_df['test_date'])
        
        # Clean text fields
        text_fields = ['first_name', 'last_name', 'test_name', 'unit', 'lab_technician', 'notes']
        for field in text_fields:
            if field in cleaned_df.columns:
                cleaned_df[field] = cleaned_df[field].astype(str).str.strip()
                cleaned_df[field] = cleaned_df[field].replace(['nan', 'NaN', ''], np.nan)
        
        return cleaned_df
    
    def parse_flexible_date(self, date_series: pd.Series) -> pd.Series:
        """
        Parse dates from various formats commonly found in medical device outputs
        """
        parsed_dates = pd.Series(index=date_series.index, dtype='datetime64[ns]')
        
        # Common date formats from medical devices
        date_formats = [
            '%Y-%m-%d',           # 2024-01-15
            '%d/%m/%Y',           # 15/01/2024
            '%m/%d/%Y',           # 01/15/2024
            '%d-%m-%Y',           # 15-01-2024
            '%Y/%m/%d',           # 2024/01/15
            '%d.%m.%Y',           # 15.01.2024
            '%Y-%m-%d %H:%M:%S',  # 2024-01-15 14:30:00
            '%d/%m/%Y %H:%M',     # 15/01/2024 14:30
            '%Y-%m-%d %H:%M',     # 2024-01-15 14:30
            '%d-%b-%Y',           # 15-Jan-2024
            '%b %d, %Y',          # Jan 15, 2024
        ]
        
        for date_format in date_formats:
            mask = parsed_dates.isna()
            if not mask.any():
                break
                
            try:
                parsed_dates[mask] = pd.to_datetime(
                    date_series[mask], 
                    format=date_format, 
                    errors='ignore'
                )
            except:
                continue
        
        # If standard formats don't work, try pandas' flexible parser
        mask = parsed_dates.isna()
        if mask.any():
            try:
                parsed_dates[mask] = pd.to_datetime(date_series[mask], errors='ignore')
            except:
                pass
        
        # For any remaining unparsed dates, use today's date
        today = datetime.now().strftime('%Y-%m-%d')
        parsed_dates = parsed_dates.fillna(pd.to_datetime(today))
        
        return parsed_dates
    
    def validate_processed_data(self, df: pd.DataFrame) -> Tuple[bool, List[str], pd.DataFrame]:
        """
        Validate the processed data and return validation results
        Returns: (is_valid, error_messages, cleaned_dataframe)
        """
        errors = []
        cleaned_df = df.copy()
        
        # Check for essential fields
        if 'patient_id' not in cleaned_df.columns or cleaned_df['patient_id'].isna().all():
            errors.append("No valid patient IDs found")
        
        if 'test_value' not in cleaned_df.columns or cleaned_df['test_value'].isna().all():
            errors.append("No valid test values found")
        
        # Remove rows with missing essential data
        initial_rows = len(cleaned_df)
        cleaned_df = cleaned_df.dropna(subset=['patient_id'])
        
        if 'test_value' in cleaned_df.columns:
            cleaned_df = cleaned_df.dropna(subset=['test_value'])
        
        final_rows = len(cleaned_df)
        
        if final_rows == 0:
            errors.append("No valid data rows remain after cleaning")
        elif final_rows < initial_rows:
            errors.append(f"Removed {initial_rows - final_rows} rows with missing essential data")
        
        # Validate data ranges
        if 'age' in cleaned_df.columns:
            invalid_ages = cleaned_df[(cleaned_df['age'] < 0) | (cleaned_df['age'] > 150)]
            if not invalid_ages.empty:
                errors.append(f"Found {len(invalid_ages)} rows with invalid ages (outside 0-150 range)")
                cleaned_df = cleaned_df[(cleaned_df['age'].isna()) | ((cleaned_df['age'] >= 0) & (cleaned_df['age'] <= 150))]
        
        if 'test_value' in cleaned_df.columns:
            # Check for extremely large or negative values that might be errors
            suspicious_values = cleaned_df[(cleaned_df['test_value'] < 0) | (cleaned_df['test_value'] > 10000)]
            if not suspicious_values.empty:
                errors.append(f"Found {len(suspicious_values)} rows with suspicious test values (negative or > 10000)")
        
        is_valid = len(errors) == 0 or (len(cleaned_df) > 0 and not any("No valid" in error for error in errors))
        
        return is_valid, errors, cleaned_df
    
    def import_flexible_csv(self, file_path: str, column_mapping: Dict[str, str], 
                           encoding: str = 'utf-8', check_duplicates: bool = True) -> Tuple[bool, str, int]:
        """
        Import CSV data with flexible column mapping
        
        Args:
            file_path: Path to the CSV file
            column_mapping: Dictionary mapping standard fields to CSV columns
            encoding: File encoding (default: utf-8)
            check_duplicates: Whether to check for and skip duplicate records (default: True)
            
        Returns: (success, message, imported_rows)
        """
        try:
            # Read the full CSV file
            success, message, df, auto_mapping = self.preview_csv_with_mapping(file_path, encoding)
            
            if not success:
                return False, message, 0
            
            # Use provided mapping or auto-detected mapping
            final_mapping = column_mapping if column_mapping else auto_mapping
            
            # Clean and convert data
            cleaned_df = self.clean_and_convert_data(df, final_mapping)
            
            # Validate data
            is_valid, validation_errors, final_df = self.validate_processed_data(cleaned_df)
            
            if not is_valid and len(final_df) == 0:
                return False, f"Data validation failed: {'; '.join(validation_errors)}", 0
            
            # Import data into database
            imported_count = 0
            duplicate_count = 0
            errors = []
            
            for index, row in final_df.iterrows():
                try:
                    # Extract patient information
                    patient_id = row.get('patient_id')
                    first_name = row.get('first_name', 'Unknown')
                    last_name = row.get('last_name', 'Patient')
                    age = row.get('age')
                    gender = row.get('gender')
                    
                    # Calculate date of birth from age if available
                    date_of_birth = None
                    if pd.notna(age) and age > 0:
                        birth_year = datetime.now().year - int(age)
                        date_of_birth = f"{birth_year}-01-01"  # Approximate DOB
                    
                    # Add or update patient
                    self.db_manager.add_patient(
                        patient_id=patient_id,
                        first_name=first_name,
                        last_name=last_name,
                        date_of_birth=date_of_birth,
                        gender=gender,
                        phone='',
                        email='',
                        address=''
                    )
                    
                    # Add test result if we have test data
                    if pd.notna(row.get('test_value')):
                        test_name = row.get('test_name', 'Unknown Test')
                        test_value = float(row['test_value'])
                        test_date = row.get('test_date', datetime.now().strftime('%Y-%m-%d'))
                        unit = row.get('unit', '')
                        lab_technician = row.get('lab_technician', '')
                        notes = row.get('notes', '')
                        
                        # Convert datetime to string if needed
                        if isinstance(test_date, pd.Timestamp):
                            test_date = test_date.strftime('%Y-%m-%d')
                        
                        # Get or create test type
                        test_type = self.db_manager.get_test_type_by_name(test_name)
                        if test_type:
                            test_type_id = test_type[0]
                        else:
                            # Create new test type if it doesn't exist
                            success = self.db_manager.add_test_type(
                                test_name=test_name,
                                unit=unit,
                                normal_min=0,  # Default values, can be updated later
                                normal_max=100
                            )
                            if success:
                                test_type = self.db_manager.get_test_type_by_name(test_name)
                                test_type_id = test_type[0] if test_type else None
                            else:
                                test_type_id = None
                        
                        if test_type_id:
                            # Try to add test result (with duplicate checking based on user preference)
                            result_added = self.db_manager.add_test_result(
                                patient_id=patient_id,
                                test_type_id=test_type_id,
                                test_value=test_value,
                                test_date=test_date,
                                lab_technician=lab_technician,
                                notes=notes,
                                check_duplicates=check_duplicates
                            )
                            
                            if not result_added and check_duplicates:
                                # Test result was not added due to duplicate
                                duplicate_count += 1
                                continue  # Skip incrementing imported_count for this row
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    continue
            
            # Prepare result message
            if imported_count > 0 or duplicate_count > 0:
                message_parts = [f"Successfully imported {imported_count} rows"]
                if duplicate_count > 0:
                    message_parts.append(f"Skipped {duplicate_count} duplicate records")
                if validation_errors:
                    message_parts.append(f"Warnings: {'; '.join(validation_errors)}")
                if errors:
                    message_parts.append(f"Errors in {len(errors)} rows")
                
                return True, ". ".join(message_parts), imported_count
            else:
                error_message = "No data imported."
                if duplicate_count > 0:
                    error_message += f" Found {duplicate_count} duplicate records."
                if errors:
                    error_message += f" Errors: {'; '.join(errors)}"
                return False, error_message, 0
                
        except Exception as e:
            return False, f"Import failed: {str(e)}", 0
    
    def generate_mapping_template(self, detected_columns: List[str]) -> str:
        """
        Generate a CSV template showing how columns would be mapped
        """
        template_data = []
        
        # Create a sample row showing the mapping
        template_data.append(["Standard Field", "Detected Column", "Sample Value"])
        
        sample_values = {
            'patient_id': 'P001',
            'age': '45',
            'gender': 'Male',
            'test_name': 'Blood Glucose',
            'test_value': '95.5',
            'test_date': '2024-01-15',
            'first_name': 'John',
            'last_name': 'Doe',
            'unit': 'mg/dL',
            'lab_technician': 'Tech1',
            'notes': 'Fasting'
        }
        
        # Add mappings for each detected field
        for field, column in detected_columns.items():
            sample_value = sample_values.get(field, 'N/A')
            template_data.append([field, column, sample_value])
        
        # Convert to CSV format
        template_text = "\n".join([",".join(row) for row in template_data])
        
        return template_text
