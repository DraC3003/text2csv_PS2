"""
SD Card Auto Processor - Main Entry Point
Processes SD card text files and appends data to appropriate EIPL CSV files
"""

import os
import csv
import json
import logging
import psutil
from datetime import datetime
from processors.sd_reader import SDCardReader
from processors.test_identifier import TestIdentifier
from processors.csv_appender import CSVAppender

class SDCardAutoProcessor:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.base_path, 'config')
        self.logs_path = os.path.join(self.base_path, 'logs')
        
        # Setup logging
        self.setup_logging()
        
        # Load configurations
        self.test_mappings = self.load_config('test_mappings.json')
        self.default_values = self.load_config('default_values.json')
        
        # Initialize processors
        self.sd_reader = SDCardReader()
        self.test_identifier = TestIdentifier(self.test_mappings)
        self.csv_appender = CSVAppender(self.test_mappings, self.default_values)
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.join(self.logs_path, f'processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self, filename):
        """Load configuration from JSON file"""
        config_file = os.path.join(self.config_path, filename)
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config {filename}: {e}")
            return {}
    
    def find_sd_card_files(self, sd_card_path=None):
        """Find text files on SD card or specified path using proper removable drive detection"""
        if not sd_card_path:
            # Use psutil to detect removable drives (same as original text2csv.py)
            removable_drives = []
            for partition in psutil.disk_partitions():
                if 'removable' in partition.opts:
                    removable_drives.append(partition.mountpoint)
            
            if not removable_drives:
                self.logger.warning("No removable drives (SD cards/USB) detected")
                return []
            
            # Use first removable drive found
            sd_card_path = removable_drives[0]
            self.logger.info(f"Using removable drive: {sd_card_path}")
            
            if len(removable_drives) > 1:
                self.logger.info(f"Multiple removable drives found: {removable_drives}")
        
        if not sd_card_path or not os.path.exists(sd_card_path):
            self.logger.error(f"SD card path not found: {sd_card_path}")
            return []
            
        # Look for text files (skip system directories)
        text_files = []
        excluded_dirs = {'System Volume Information', '$RECYCLE.BIN', 'RECYCLER'}
        
        for root, dirs, files in os.walk(sd_card_path):
            # Skip system directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if file.lower().endswith(('.txt', '.csv', '.dat')):
                    text_files.append(os.path.join(root, file))
                    
        self.logger.info(f"Found {len(text_files)} text files on removable drive {sd_card_path}")
        return text_files
    
    def process_sd_card(self, sd_card_path=None):
        """Main processing function"""
        self.logger.info("Starting SD card processing...")
        
        # Find SD card files
        text_files = self.find_sd_card_files(sd_card_path)
        if not text_files:
            self.logger.warning("No text files found on SD card")
            return
            
        total_records = 0
        processed_records = 0
        
        for file_path in text_files:
            self.logger.info(f"Processing file: {file_path}")
            
            # Read records from file
            records = self.sd_reader.read_file(file_path)
            total_records += len(records)
            
            for record in records:
                try:
                    # Identify test type
                    test_type = self.test_identifier.identify_test(record)
                    if not test_type:
                        self.logger.warning(f"Could not identify test type for record: {record}")
                        continue
                    
                    # Append to appropriate CSV
                    success = self.csv_appender.append_record(test_type, record)
                    if success:
                        processed_records += 1
                        self.logger.info(f"Successfully processed {test_type} record for patient: {record[0] if record else 'Unknown'}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing record {record}: {e}")
                    continue
        
        self.logger.info(f"Processing complete: {processed_records}/{total_records} records processed successfully")
        
        # Log summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_records': total_records,
            'processed_records': processed_records,
            'success_rate': f"{(processed_records/total_records*100):.1f}%" if total_records > 0 else "0%"
        }
        
        summary_file = os.path.join(self.logs_path, 'processing_summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

def main():
    """Main entry point"""
    processor = SDCardAutoProcessor()
    
    print("=== SD Card Auto Processor for Medical Data ===")
    print("This tool automatically processes medical test data from SD cards")
    print()
    
    # Check for removable drives first
    removable_drives = []
    for partition in psutil.disk_partitions():
        if 'removable' in partition.opts:
            removable_drives.append(partition.mountpoint)
    
    if removable_drives:
        print(f"Found removable drive(s): {removable_drives}")
        processor.process_sd_card()  # Auto-detect and process
    else:
        print("No removable drives (SD cards/USB) detected.")
        print()
        choice = input("Options:\n1. Wait and retry\n2. Specify custom path\n3. Exit\nChoose (1/2/3): ").strip()
        
        if choice == "1":
            print("Please insert SD card and try again...")
            input("Press Enter when ready...")
            processor.process_sd_card()
        elif choice == "2":
            custom_path = input("Enter path to text files: ").strip()
            if custom_path and os.path.exists(custom_path):
                processor.process_sd_card(custom_path)
            else:
                print("Invalid path. Exiting...")
        else:
            print("Exiting...")
            return
    
    print("\nProcessing complete! Check logs folder for details.")
    print("Next step: Run the appropriate analyzer batch file for each test type.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
