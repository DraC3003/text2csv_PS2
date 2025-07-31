"""
SD Card Reader - Handles reading text files from SD card
Supports flexible format: PatientID, TestName, Age, Gender, Reading, [Optional Fields...]
"""

import csv
import logging

class SDCardReader:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def read_file(self, file_path):
        """
        Read records from SD card text file
        Expected format: PatientID, TestName, Age, Gender, Reading, [Optional Fields...]
        """
        records = []
        
        try:
            # Try reading as CSV first
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                delimiter = ','
                if '\t' in sample:
                    delimiter = '\t'
                elif ';' in sample:
                    delimiter = ';'
                
                reader = csv.reader(file, delimiter=delimiter)
                
                for line_num, row in enumerate(reader, 1):
                    # Skip empty lines
                    if not row or all(field.strip() == '' for field in row):
                        continue
                    
                    # Clean up fields (remove extra whitespace)
                    cleaned_row = [field.strip() for field in row]
                    
                    # Validate minimum required fields
                    if len(cleaned_row) < 5:
                        self.logger.warning(f"Line {line_num}: Insufficient fields (need at least 5): {cleaned_row}")
                        continue
                    
                    # Validate basic format
                    if not self._validate_record(cleaned_row, line_num):
                        continue
                        
                    records.append(cleaned_row)
                    
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            
        self.logger.info(f"Read {len(records)} valid records from {file_path}")
        return records
    
    def _validate_record(self, record, line_num):
        """Validate basic record format"""
        try:
            # Check Patient ID (should not be empty)
            if not record[0]:
                self.logger.warning(f"Line {line_num}: Empty Patient ID")
                return False
            
            # Check Test Name (should not be empty)
            if not record[1]:
                self.logger.warning(f"Line {line_num}: Empty Test Name")
                return False
            
            # Check Age (should be numeric or empty)
            if record[2] and not self._is_valid_age(record[2]):
                self.logger.warning(f"Line {line_num}: Invalid age format: {record[2]}")
                # Don't reject, just warn - we'll use default
            
            # Check Reading (should be numeric)
            if record[4] and not self._is_numeric(record[4]):
                self.logger.warning(f"Line {line_num}: Invalid reading format: {record[4]}")
                return False
                
            return True
            
        except IndexError:
            self.logger.warning(f"Line {line_num}: Missing required fields")
            return False
    
    def _is_valid_age(self, age_str):
        """Check if age is valid"""
        try:
            age = int(float(age_str))
            return 0 <= age <= 150
        except (ValueError, TypeError):
            return False
    
    def _is_numeric(self, value_str):
        """Check if value is numeric"""
        try:
            float(value_str)
            return True
        except (ValueError, TypeError):
            return False
