# Medical Test Data Management System

A comprehensive system for managing patient test results with data import, database storage, and reporting capabilities.

## Features

- **Patient Management**: Add, update, and manage patient information including age and gender
- **Flexible Data Entry**: All fields except Patient ID are optional, allowing quick patient registration
- **Missing Value Handling**: Graceful handling of missing age/gender information with appropriate fallbacks
- **Test Result Entry**: Manual entry and editing of test results
- **CSV Data Import**: Import test data from SD cards or other sources in CSV format
- **Duplicate Detection**: Intelligent duplicate prevention during data import
- **Database Storage**: Local SQLite database for all data storage
- **Smart Range Adjustments**: Automatic normal range adjustments based on available patient demographics
- **Excel Reports**: Generate color-coded Excel reports with medical thresholds and range sources
- **Patient Summaries**: Create printable patient reports combining all test results
- **Intelligent Validation**: Automatic validation with clear indication of range adjustment level

## Installation

1. **Install Python** (3.8 or higher required)

2. **Install required packages**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Starting the Application

Run `python main.py` to start the Medical Test Data Management System.

### Patient Management

1. Go to the "Patient Management" tab
2. Fill in patient information (Only Patient ID is required)
   - **Patient ID**: Required - unique identifier for the patient
   - **First Name & Last Name**: Optional - can be added later
   - **Date of Birth**: Optional but recommended - enables age-specific medical ranges
   - **Gender**: Optional but recommended - enables gender-specific medical ranges
   - **Contact Info**: Optional - phone, email, address for record keeping
3. Click "Add Patient" to save
4. Use the search function to find existing patients
5. Select a patient from the list to edit or delete

**Note**: While only Patient ID is required, providing date of birth and gender significantly improves the accuracy of medical test interpretations by enabling age and gender-specific normal ranges.

### Adding Test Results

1. Go to the "Test Results" tab
2. Select a patient from the dropdown
3. Choose a test type from the available options
4. Enter the test value and date
5. Optionally add lab technician name and notes
6. Click "Add Test Result"

### Importing CSV Data

1. Go to the "Data Import" tab
2. Click "Generate Template" to create a sample CSV file format
3. Prepare your CSV file with the required columns:
   - `patient_id` (required)
   - `first_name`, `last_name` (for new patients)
   - `test_name` (required)
   - `test_value` (required)
   - `test_date` (required, YYYY-MM-DD format)
   - `unit`, `lab_technician`, `notes` (optional)
4. Click "Browse" to select your CSV file
5. Click "Preview Data" to validate the file
6. Click "Import Data" to import into the database

### Generating Reports

1. Go to the "Reports" tab
2. Select a patient from the dropdown
3. Choose report type:
   - **Excel Report**: Comprehensive report with color-coded results
   - **Patient Summary**: Printable PDF summary

### Importing CSV Data with Flexible Format Support

1. Go to the "Flexible CSV Import" tab
2. **Step 1 - Select File**:
   - Click "Browse" to select CSV file from SD card or computer
   - Choose file encoding if needed (UTF-8 is default)
   - Click "Analyze File" for automatic column detection
3. **Step 2 - Verify Mappings**:
   - Review auto-detected column mappings
   - Use manual controls to correct mappings if needed
   - Ensure essential fields (Patient ID, Test Value) are mapped
4. **Step 3 - Preview Data**:
   - Review preview of how data will be imported
   - Check patient IDs, ages, genders, and test values
5. **Step 4 - Import**:
   - Click "Validate Data" to check for issues
   - Click "Import Data" to add to database

**Supported formats**: The system automatically handles various CSV formats from medical devices including:

- BIO-CHEQ devices with columns like "Patient ID_BIOCHEQ", "Parameters", "Date & Time"
- Generic lab equipment with standard column names
- Hospital information system exports
- Any CSV with patient demographics and test results

For detailed information about flexible import, see [FLEXIBLE_IMPORT_GUIDE.md](FLEXIBLE_IMPORT_GUIDE.md).

### Duplicate Detection

The system automatically prevents importing duplicate test records:

- **Automatic Detection**: Identifies records with identical patient ID, test type, value, and date
- **User Control**: Option to enable/disable duplicate checking in both import interfaces
- **Smart Reporting**: Clear feedback about duplicates found and skipped during import
- **Time Tolerance**: Configurable time window to catch near-duplicate entries

**Recommended**: Keep duplicate detection enabled (default) to maintain data integrity.

For detailed information about duplicate detection, see [DUPLICATE_DETECTION_GUIDE.md](DUPLICATE_DETECTION_GUIDE.md).

### Managing Custom Test Ranges

1. Go to the "Custom Ranges" tab
2. **Create New Range**:
   - Click "New Range" to clear the form
   - Select test type and enter range details
   - Specify age, gender, or condition filters as needed
   - Set normal and critical value ranges
   - Add clinical notes
   - Click "Save Range"
3. **Edit Existing Range**:
   - Select a range from the list
   - Modify the values in the form
   - Click "Save Range" to update
4. **Import/Export Ranges**:
   - Use "Export to JSON" to backup your custom ranges
   - Use "Import from JSON" to restore or share range configurations

For detailed information about custom ranges, see [CUSTOM_RANGES_GUIDE.md](CUSTOM_RANGES_GUIDE.md).

### Understanding Color Coding

The system uses color coding in Excel reports to indicate test result status:

- **Green**: Normal values within expected range
- **Light Red**: High values (above normal range)
- **Light Blue**: Low values (below normal range)
- **Red**: Critical high values (significantly above normal)
- **Blue**: Critical low values (significantly below normal)

Note: Color coding is based on age/gender-adjusted ranges and any applicable custom ranges.

## Handling Missing Patient Information

The system is designed to work gracefully even when patient demographic information is incomplete:

### Missing Age Information

- **When no date of birth is provided**: The system uses general adult normal ranges as a fallback
- **Impact**: Test results will still be interpreted, but may be less accurate for pediatric or elderly patients
- **Recommendation**: Add date of birth when possible for more accurate medical interpretations

### Missing Gender Information

- **When gender is not specified**: The system uses general ranges that apply to all genders
- **Impact**: Some tests (like Hemoglobin, HDL Cholesterol) have gender-specific ranges that won't be applied
- **Recommendation**: Specify gender when relevant for the test being performed

### Missing Name Information

- **When first/last name is not provided**: The system works normally using Patient ID
- **Impact**: Reports will show "Not provided" for missing names
- **Use case**: Useful for anonymous testing or when using coded patient identifiers

### Fallback Behavior

1. **Custom Ranges**: If custom ranges are configured, they take precedence regardless of missing demographics
2. **Age-Specific**: If age is available but gender is missing, age-adjusted ranges are used
3. **Gender-Specific**: If gender is available but age is missing, gender-adjusted ranges for adults are used
4. **Base Ranges**: If both age and gender are missing, standard adult ranges are used
5. **Clear Indicators**: Reports clearly indicate what level of demographic adjustment was applied

### Best Practices

- **Minimum viable**: Patient ID + test results = functional system
- **Recommended**: Patient ID + date of birth + gender + test results = optimal accuracy
- **Flexible workflow**: Add demographic information as it becomes available

## File Structure

```
medical_test_system/
├── main.py                 # Main application entry point
├── database_manager.py     # Database operations and management
├── data_processor.py       # CSV import and data processing
├── report_generator.py     # Excel and PDF report generation
├── ui_components.py        # User interface components
├── requirements.txt        # Python package dependencies
├── sample_data.csv        # Sample CSV data for testing
├── medical_test_data.db   # SQLite database (created automatically)
└── README.md              # This file
```

## Database Schema

### Patients Table

- `patient_id` (TEXT, PRIMARY KEY)
- `first_name` (TEXT, OPTIONAL)
- `last_name` (TEXT, OPTIONAL)
- `date_of_birth` (DATE)
- `gender` (TEXT)
- `phone` (TEXT)
- `email` (TEXT)
- `address` (TEXT)
- `created_date` (TIMESTAMP)

### Test Types Table

- `test_type_id` (INTEGER, PRIMARY KEY)
- `test_name` (TEXT, UNIQUE)
- `normal_min` (REAL)
- `normal_max` (REAL)
- `unit` (TEXT)
- `description` (TEXT)

### Test Results Table

- `result_id` (INTEGER, PRIMARY KEY)
- `patient_id` (TEXT, FOREIGN KEY)
- `test_type_id` (INTEGER, FOREIGN KEY)
- `test_value` (REAL)
- `test_date` (DATE)
- `lab_technician` (TEXT)
- `notes` (TEXT)
- `created_date` (TIMESTAMP)

## Age and Gender-Specific Normal Ranges

The system automatically adjusts normal ranges based on patient demographics:

### Age Groups:

- **Infant** (0-2 years): Special ranges for newborns and toddlers
- **Child** (3-12 years): Pediatric ranges
- **Teen** (13-17 years): Adolescent ranges
- **Adult** (18-64 years): Standard adult ranges
- **Elderly** (65+ years): Senior-specific ranges

### Gender-Specific Adjustments:

- **Hemoglobin**: Different ranges for males vs females
- **Creatinine**: Gender-specific kidney function ranges
- **HDL Cholesterol**: Higher normal minimums for females
- **Other tests**: Age-appropriate ranges regardless of gender

### Examples:

- **Hemoglobin**: Adult Male (13.8-17.2 g/dL) vs Adult Female (12.1-15.1 g/dL)
- **Heart Rate**: Child (70-120 bpm) vs Adult (60-100 bpm)
- **Blood Pressure**: Adjusted ranges for children, teens, adults, and elderly

## Pre-configured Test Types

The system comes with common medical test types and their base normal ranges:

- Hemoglobin (12.0-16.0 g/dL)
- White Blood Cell Count (4000-11000 cells/μL)
- Platelet Count (150000-450000 cells/μL)
- Blood Glucose (70-100 mg/dL)
- Cholesterol Total (0-200 mg/dL)
- HDL Cholesterol (40-100 mg/dL)
- LDL Cholesterol (0-100 mg/dL)
- Triglycerides (0-150 mg/dL)
- Creatinine (0.6-1.2 mg/dL)
- Blood Urea Nitrogen (7-20 mg/dL)
- ALT (7-40 U/L)
- AST (8-40 U/L)
- Blood Pressure Systolic (90-120 mmHg)
- Blood Pressure Diastolic (60-80 mmHg)
- Heart Rate (60-100 bpm)

_Note: These base ranges are automatically adjusted based on patient age and gender._

## CSV Import Format

Your CSV file should include these columns:

**Required columns:**

- `patient_id`: Unique identifier for each patient
- `test_name`: Name of the medical test
- `test_value`: Numeric test result value
- `test_date`: Date in YYYY-MM-DD format

**Optional columns:**

- `first_name`, `last_name`: Patient names (for new patients)
- `date_of_birth`: Patient DOB in YYYY-MM-DD format (for age-specific ranges)
- `gender`: Patient gender (Male/Female/Other for gender-specific ranges)
- `phone`, `email`, `address`: Contact information
- `unit`: Test value unit (e.g., mg/dL, g/dL)
- `lab_technician`: Name of lab technician
- `notes`: Additional notes about the test

## Troubleshooting

### Common Issues

1. **Import fails with "Missing required columns"**

   - Ensure your CSV has all required columns: patient_id, test_name, test_value, test_date

2. **"Non-numeric test values" error**

   - Check that all test_value entries are numbers (no text or special characters)

3. **"Invalid date format" error**

   - Ensure all dates are in YYYY-MM-DD format (e.g., 2025-01-15)

4. **Excel report generation fails**

   - Ensure openpyxl is installed: `pip install openpyxl`

5. **PDF report generation fails**
   - Ensure matplotlib is installed: `pip install matplotlib`

### Database Issues

- The SQLite database file (`medical_test_data.db`) is created automatically
- If you encounter database errors, you can delete this file to reset the database
- All data will be lost if you delete the database file

## Security and Privacy

- This system stores data locally in a SQLite database
- No data is transmitted over the internet
- Ensure proper access controls on the computer running this system
- Regular backups of the database file are recommended
- Follow your organization's data protection policies

## Extending the System

### Adding New Test Types

1. Use the database manager to add new test types programmatically
2. Or add them via the CSV import with new test names
3. The system will automatically create new test types during import

### Customizing Normal Ranges

1. Modify the `insert_default_test_types()` method in `database_manager.py`
2. Or update ranges directly in the database using SQL commands

### Adding New Report Formats

1. Extend the `ReportGenerator` class in `report_generator.py`
2. Add new methods for different report types
3. Update the UI to include new report options

## License

This is original code created specifically for medical test data management. No external libraries beyond the standard scientific Python stack are used. All code is custom-written and not based on existing licensed medical software.
