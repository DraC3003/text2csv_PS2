import os
import csv
import time
import re
import psutil
import logging
from pathlib import Path

# === UPDATED FOR MEDICAL DATA PROCESSING SYSTEM INTEGRATION ===
# This script has been enhanced to:
# 1. Output CSV format compatible with master_medical_data.csv 
# 2. Support 5 lab test types: Hemoglobin, Calcium, Urea, Albumin, Glucose
# 3. Standardize test names and units for clinical analysis
# 4. Include Age and Gender columns (extracted from filenames when possible)
# 5. Convert units to standard clinical formats (g/dL for Hb/Albumin, mg/dL for Ca/Urea/Glucose)
# === END ENHANCEMENT DOCUMENTATION ===

# --- Industrial Deployment Enhancements ---
# 1. Setup robust logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# 2. Define a file to track processed files to prevent duplicates
PROCESSED_FILES_LOG = "processed_files.log"
# --- End Enhancements ---

class SDCardHandler:
    def __init__(self, output_csv_path="medical_data.csv"):
        self.output_csv_path = output_csv_path
        self.monitored_drives = set()
        self.processed_files = self._load_processed_files()

    def _load_processed_files(self):
        """Load the set of already processed file paths from a log file."""
        try:
            if os.path.exists(PROCESSED_FILES_LOG):
                with open(PROCESSED_FILES_LOG, 'r') as f:
                    return set(line.strip() for line in f)
        except Exception as e:
            logging.error(f"Could not load processed files log: {e}")
        return set()

    def _log_processed_file(self, file_path):
        """Add a file path to the processed log to prevent reprocessing."""
        self.processed_files.add(file_path)
        try:
            with open(PROCESSED_FILES_LOG, 'a') as f:
                f.write(f"{file_path}\n")
        except Exception as e:
            logging.error(f"Could not write to processed files log: {e}")
        
    def get_removable_drives(self):
        """Get list of removable drives (SD cards, USB drives)"""
        removable_drives = []
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts:
                removable_drives.append(partition.mountpoint)
        return removable_drives
    
    def parse_medical_data(self, file_path):
        """
        Parses medical data from a text file.
        The data is expected in a continuous stream format like:
        ID<ID_value>Test_name<Test_name_value>reading<reading_value>
        Example: '1836Hb689mg/dL78887Na145mmol/L'
        Supports: Hemoglobin (Hb/HB), Calcium (Ca), Urea (Ur), Albumin (Alb/ALB), Glucose
        """
        data_rows = []
        
        # Try to extract demographics from filename
        default_age, default_gender = self.extract_demographics_from_filename(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()

            # Enhanced regex to capture ID, test name, and reading with units
            # Pattern: ID, followed by digits, then Test_name, then letters, then reading, then the value with units.
            pattern = re.compile(r'(\d+)([a-zA-Z\s]+)(\d+\.?\d*\s*[a-zA-Z/]+)')
            matches = pattern.findall(content)

            for match in matches:
                test_name_raw = match[1].strip()
                reading_raw = match[2].strip()
                
                # Standardize test names to match clinical analysis system
                test_name_standardized = self.standardize_test_name(test_name_raw)
                
                # Skip if test type is not supported
                if test_name_standardized == "Unknown":
                    logging.warning(f"Skipping unknown test type: {test_name_raw}")
                    continue
                
                # Standardize reading format
                reading_standardized = self.standardize_reading(reading_raw, test_name_standardized)
                
                record = {
                    'ID': match[0].strip(),
                    'Test_name': test_name_standardized,
                    'reading': reading_standardized,
                    'Age': default_age,  # Use extracted or default age
                    'Gender': default_gender  # Use extracted or default gender
                }
                data_rows.append(record)

        except UnicodeDecodeError:
            logging.warning(f"Skipping file due to encoding error: {file_path}")
        except Exception as e:
            logging.error(f"Error parsing file {file_path}: {str(e)}")
            
        return data_rows
    
    def standardize_test_name(self, test_name_raw):
        """Standardize test names to match clinical analysis system"""
        test_name_lower = test_name_raw.lower().strip()
        
        # Map various test name formats to standard names
        if any(term in test_name_lower for term in ['hb', 'hemoglobin', 'haemoglobin']):
            return 'Hemoglobin'
        elif any(term in test_name_lower for term in ['ca', 'calcium']):
            return 'Calcium'
        elif any(term in test_name_lower for term in ['ur', 'urea', 'bun', 'blood urea']):
            return 'Urea'
        elif any(term in test_name_lower for term in ['alb', 'albumin']):
            return 'Albumin'
        elif any(term in test_name_lower for term in ['glucose', 'blood glucose', 'blood sugar', 'fasting glucose', 'random glucose']):
            return 'Glucose'
        else:
            return "Unknown"
    
    def standardize_reading(self, reading_raw, test_name):
        """Standardize reading format with proper units"""
        # Extract numeric value and unit
        numeric_match = re.search(r'(\d+\.?\d*)', reading_raw)
        unit_match = re.search(r'([a-zA-Z/]+)', reading_raw)
        
        if not numeric_match:
            return reading_raw  # Return as-is if no numeric value found
        
        value = float(numeric_match.group(1))
        unit = unit_match.group(1) if unit_match else ''
        
        # Standardize units based on test type and clinical ranges
        if test_name == 'Hemoglobin':
            # Convert to g/dL (standard for hemoglobin)
            if 'mg/dl' in reading_raw.lower():
                value = value / 1000  # mg/dL to g/dL
                unit = 'g/dL'
            elif 'mmol/l' in reading_raw.lower():
                value = value * 1.611  # mmol/L to g/dL
                unit = 'g/dL'
            elif not unit or unit.lower() in ['g/dl', 'gdl']:
                unit = 'g/dL'
            return f"{value:.2f} {unit}"
            
        elif test_name == 'Calcium':
            # Convert to mg/dL (standard for calcium)
            if 'mmol/l' in reading_raw.lower():
                value = value * 4.0  # mmol/L to mg/dL
                unit = 'mg/dL'
            elif not unit or unit.lower() in ['mg/dl', 'mgdl']:
                unit = 'mg/dL'
            return f"{value:.2f} {unit}"
            
        elif test_name == 'Urea':
            # Convert to mg/dL (standard for urea)
            if 'mmol/l' in reading_raw.lower():
                value = value * 2.8  # mmol/L to mg/dL
                unit = 'mg/dL'
            elif not unit or unit.lower() in ['mg/dl', 'mgdl']:
                unit = 'mg/dL'
            return f"{value:.2f} {unit}"
            
        elif test_name == 'Albumin':
            # Standard unit is g/dL
            if not unit or unit.lower() in ['g/dl', 'gdl']:
                unit = 'g/dL'
            return f"{value:.2f} {unit}"
            
        elif test_name == 'Glucose':
            # Convert to mg/dL (standard for glucose)
            if 'mmol/l' in reading_raw.lower():
                value = value * 18.0  # mmol/L to mg/dL
                unit = 'mg/dL'
            elif not unit or unit.lower() in ['mg/dl', 'mgdl']:
                unit = 'mg/dL'
            return f"{value:.2f} {unit}"
        
        # Default: return with original or standardized unit
        return f"{value:.2f} {unit}" if unit else f"{value:.2f}"
    
    def extract_demographics_from_filename(self, file_path):
        """
        Try to extract age and gender from filename patterns
        Common patterns: PatientName_Age_Gender.txt, Patient_25_M.txt, etc.
        """
        filename = os.path.basename(file_path).lower()
        age = 35  # Default
        gender = 'Male'  # Default
        
        # Try to extract age (look for numbers that could be age: 1-120)
        age_matches = re.findall(r'\b(\d{1,3})\b', filename)
        for match in age_matches:
            potential_age = int(match)
            if 1 <= potential_age <= 120:  # Reasonable age range
                age = potential_age
                break
        
        # Try to extract gender
        if any(term in filename for term in ['female', 'f', 'woman', 'girl']):
            gender = 'Female'
        elif any(term in filename for term in ['male', 'm', 'man', 'boy']):
            gender = 'Male'
        
        return age, gender
    
    def append_to_csv(self, data_rows):
        """Append data to CSV file, creating it if it doesn't exist"""
        if not data_rows:
            return
            
        # Updated fieldnames to match master_medical_data.csv format
        fieldnames = ['ID', 'Test_name', 'reading', 'Source_File', 'Timestamp', 'Age', 'Gender']
        
        # Check if file exists
        file_exists = os.path.exists(self.output_csv_path)
        
        try:
            with open(self.output_csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header if file is new
                if not file_exists:
                    writer.writeheader()
                    logging.info(f"Created new CSV file: {self.output_csv_path}")
                
                # Write data rows
                for row in data_rows:
                    # Add source file and timestamp to each row before writing
                    row['Source_File'] = os.path.basename(row.get('Source_File', 'N/A'))
                    row['Timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Ensure Age and Gender are present (they should be from parsing)
                    if 'Age' not in row or not row['Age']:
                        row['Age'] = 35  # Fallback default
                    if 'Gender' not in row or not row['Gender']:
                        row['Gender'] = 'Male'  # Fallback default
                    
                    writer.writerow(row)
                
                logging.info(f"Appended {len(data_rows)} rows to {self.output_csv_path}")
                
        except Exception as e:
            logging.error(f"Error writing to CSV: {str(e)}")
    
    def process_text_files_on_drive(self, drive_path):
        """Process all text files found on the specified drive, skipping duplicates."""
        logging.info(f"Scanning drive: {drive_path}")
        
        all_data = []
        text_files_found = 0
        excluded_dirs = {'System Volume Information', '$RECYCLE.BIN'}
        
        try:
            for root, dirs, files in os.walk(drive_path):
                # --- Enhancement: Skip excluded system directories ---
                dirs[:] = [d for d in dirs if d not in excluded_dirs]
                # --- End Enhancement ---
                
                for file in files:
                    if file.lower().endswith(('.txt', '.dat', '.log')):
                        file_path = os.path.join(root, file)

                        # --- Enhancement: Skip already processed files ---
                        if file_path in self.processed_files:
                            logging.info(f"Skipping already processed file: {file_path}")
                            continue
                        # --- End Enhancement ---

                        logging.info(f"Processing: {file_path}")
                        
                        # The parse function now returns a list of dicts
                        parsed_data = self.parse_medical_data(file_path)
                        
                        if parsed_data:
                            # Add source file information to each record
                            for record in parsed_data:
                                record['Source_File'] = file_path
                            all_data.extend(parsed_data)
                            text_files_found += 1
                            # Log file as processed only if data was successfully parsed
                            self._log_processed_file(file_path)
            
            if all_data:
                self.append_to_csv(all_data)
                logging.info(f"Successfully processed {text_files_found} new text files from {drive_path}")
            else:
                logging.info(f"No new data found to process on {drive_path}")
                
        except Exception as e:
            logging.error(f"Error processing drive {drive_path}: {str(e)}")
    
    def check_for_new_drives(self):
        """Check for newly inserted removable drives"""
        current_drives = set(self.get_removable_drives())
        new_drives = current_drives - self.monitored_drives
        
        for drive in new_drives:
            logging.info(f"New SD card/USB drive detected: {drive}")
            self.process_text_files_on_drive(drive)
        
        # Update monitored drives
        self.monitored_drives = current_drives
        
        # Remove drives that are no longer connected
        disconnected_drives = self.monitored_drives - current_drives
        if disconnected_drives:
            for drive in disconnected_drives:
                logging.info(f"Drive disconnected: {drive}")
    
    def start_monitoring(self):
        """Start monitoring for SD card insertion"""
        logging.info("Starting SD card monitoring...")
        logging.info("Insert your SD card to automatically process text files...")
        logging.info("Press Ctrl+C to stop monitoring")
        
        # Initial scan
        self.monitored_drives = set(self.get_removable_drives())
        
        try:
            while True:
                self.check_for_new_drives()
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            logging.info("\nMonitoring stopped by user")
        except Exception as e:
            logging.error(f"Critical error in monitoring loop: {str(e)}")

def main():
    """Main function to run the SD card monitor"""
    logging.info("=== Automatic SD Card Text-to-CSV Converter (Industrial Version) ===")
    
    # Ask user for output CSV file name
    output_file = input("Enter the path to your master CSV file (default: medical_data.csv): ").strip()
    if not output_file:
        output_file = "medical_data.csv"
    
    # Create handler
    handler = SDCardHandler(output_file)
    
    # Option to process existing drives
    existing_drives = handler.get_removable_drives()
    if existing_drives:
        logging.info(f"Found existing removable drives: {existing_drives}")
        process_existing = input("Process existing drives now? (y/n): ").lower().strip()
        
        if process_existing == 'y':
            for drive in existing_drives:
                handler.process_text_files_on_drive(drive)
    
    # Start monitoring
    handler.start_monitoring()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"A fatal error occurred: {str(e)}")
        input("Press Enter to exit...")
