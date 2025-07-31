"""
CSV Appender - Appends processed records to appropriate EIPL CSV files
"""

import os
import csv
import logging
from datetime import datetime

class CSVAppender:
    def __init__(self, test_mappings, default_values):
        self.test_mappings = test_mappings
        self.default_values = default_values
        self.logger = logging.getLogger(__name__)
        
        # Base path for analyzer folders (parent of SD_Card_Auto_Processor)
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.analyzer_base_path = os.path.dirname(current_dir)  # Go up one more level to Analysis folder
        
        self.logger.info(f"Analyzer base path set to: {self.analyzer_base_path}")
        
    def append_record(self, test_type, sd_record):
        """
        Append record to appropriate EIPL CSV file
        """
        if test_type not in self.test_mappings:
            self.logger.error(f"Unknown test type: {test_type}")
            return False
            
        test_config = self.test_mappings[test_type]
        
        try:
            # Build target file path
            folder_name = test_config['folder_name']
            eipl_file = test_config['eipl_file']
            target_file = os.path.join(self.analyzer_base_path, folder_name, eipl_file)
            
            if not os.path.exists(target_file):
                self.logger.error(f"Target EIPL file not found: {target_file}")
                return False
            
            # Read existing CSV to get current row count for Sr. No.
            current_rows = self._count_csv_rows(target_file)
            next_sr_no = current_rows  # Header is row 1, so data starts from row 2
            
            # Map SD record to EIPL format
            eipl_record = self._map_record(test_type, sd_record, next_sr_no)
            
            # Validate required fields
            if not self._validate_required_fields(test_type, eipl_record):
                return False
            
            # Append to CSV
            with open(target_file, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(eipl_record)
            
            self.logger.info(f"Successfully appended record to {target_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error appending record for {test_type}: {e}")
            return False
    
    def _count_csv_rows(self, file_path):
        """Count existing rows in CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return sum(1 for line in file)
        except Exception:
            return 1  # Default to 1 if can't read
    
    def _map_record(self, test_type, sd_record, sr_no):
        """
        Map SD card record to EIPL CSV format
        SD format: [PatientID, TestName, Age, Gender, Reading, Optional Fields...]
        """
        test_config = self.test_mappings[test_type]
        columns = test_config['columns']
        sd_mapping = test_config.get('sd_card_mapping', {})
        
        # Initialize with defaults
        eipl_record = [''] * len(columns)
        
        # Set Sr. No.
        eipl_record[0] = str(sr_no)
        
        # Apply default values
        common_defaults = self.default_values.get('common_defaults', {})
        test_defaults = self.default_values.get('test_specific_defaults', {}).get(test_type, {})
        
        for i, column in enumerate(columns):
            # Apply common defaults
            if column in common_defaults:
                value = common_defaults[column]
                if value == "auto_timestamp":
                    value = datetime.now().strftime("%m/%d/%y %H:%M")
                eipl_record[i] = value
            
            # Apply test-specific defaults
            if column in test_defaults:
                eipl_record[i] = test_defaults[column]
        
        # Map from SD card record
        for column, sd_index in sd_mapping.items():
            if column in columns:
                column_index = columns.index(column)
                
                # Get value from SD record if available
                if sd_index < len(sd_record) and sd_record[sd_index].strip():
                    value = sd_record[sd_index].strip()
                    
                    # Special handling for age
                    if column == 'Age' and not self._is_valid_age(value):
                        value = common_defaults.get('Age', '30')
                    
                    eipl_record[column_index] = value
        
        # Generate missing IDs if needed
        self._generate_missing_ids(eipl_record, columns)
        
        return eipl_record
    
    def _is_valid_age(self, age_str):
        """Check if age is valid"""
        try:
            age = int(float(age_str))
            return 0 <= age <= 150
        except (ValueError, TypeError):
            return False
    
    def _generate_missing_ids(self, record, columns):
        """Generate missing Barcode ID and Patient ID_BIOCHEQ"""
        patient_id = record[columns.index('Patient ID')] if 'Patient ID' in columns else ''
        
        if 'Barcode ID' in columns:
            barcode_index = columns.index('Barcode ID')
            if not record[barcode_index]:
                # Generate barcode from timestamp and patient ID
                timestamp = datetime.now().strftime("%y%m%d%H%M")
                record[barcode_index] = f"{timestamp}{patient_id[-4:] if patient_id else '0000'}"
        
        if 'Patient ID_BIOCHEQ' in columns:
            biocheq_index = columns.index('Patient ID_BIOCHEQ')
            if not record[biocheq_index]:
                # Use last 7 digits of patient ID or generate random
                record[biocheq_index] = patient_id[-7:] if len(patient_id) >= 7 else '1234567'
    
    def _validate_required_fields(self, test_type, record):
        """Validate that required fields are not empty"""
        test_config = self.test_mappings[test_type]
        required_fields = test_config.get('required_fields', [])
        columns = test_config['columns']
        
        for field in required_fields:
            if field in columns:
                field_index = columns.index(field)
                if field_index < len(record) and not record[field_index].strip():
                    self.logger.error(f"Required field '{field}' is empty for {test_type}")
                    return False
        
        return True
