import os
import csv
import time
import re
import psutil
import logging
from pathlib import Path

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
        """
        data_rows = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()

            # Regex to find all non-overlapping matches of the pattern
            # Pattern: ID, followed by digits, then Test_name, then letters, then reading, then the value.
            pattern = re.compile(r'(\d+)([a-zA-Z\s]+)(\d+\.?\d*\s*[a-zA-Z/]+)')
            matches = pattern.findall(content)

            for match in matches:
                record = {
                    'ID': match[0].strip(),
                    'Test_name': match[1].strip(),
                    'reading': match[2].strip()
                }
                data_rows.append(record)

        except UnicodeDecodeError:
            logging.warning(f"Skipping file due to encoding error: {file_path}")
        except Exception as e:
            logging.error(f"Error parsing file {file_path}: {str(e)}")
            
        return data_rows
    
    def extract_unit(self, value_string):
        """Extract unit from value string (e.g., 'mmol/L', 'mg/dL')"""
        unit_pattern = r'[a-zA-Z]+(?:/[a-zA-Z]+)*'
        match = re.search(unit_pattern, value_string)
        return match.group() if match else 'N/A'
    
    def append_to_csv(self, data_rows):
        """Append data to CSV file, creating it if it doesn't exist"""
        if not data_rows:
            return
            
        fieldnames = ['ID', 'Test_name', 'reading', 'Source_File', 'Timestamp']
        
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
