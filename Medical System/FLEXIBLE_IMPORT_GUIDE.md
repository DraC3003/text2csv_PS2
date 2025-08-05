# Flexible CSV Import System

## Overview

The Flexible CSV Import System automatically handles various CSV formats from different medical devices, intelligently detecting and mapping columns to extract patient data, demographics, and test results.

## Key Features

### 🎯 **Intelligent Column Detection**

The system automatically detects and maps columns from various naming conventions:

#### Patient Information

- **Patient ID**: `patient_id`, `patientid`, `patient id`, `pid`, `id`, `patient_id_biocheq`, `barcode_id`, `barcode id`
- **Age**: `age`, `patient_age`, `age_years`, `years`
- **Gender**: `gender`, `sex`, `patient_gender`, `male_female`, `m/f`
- **Names**: `first_name`, `last_name`, `firstname`, `lastname`, etc.

#### Test Information

- **Test Name**: `test_name`, `testname`, `test name`, `test_type`, `test type`, `parameters`, `analyte`, `test`, `parameter`
- **Test Value**: `test_value`, `testvalue`, `test value`, `value`, `result`, `reading`, `measurement`, `concentration`, `level`
- **Test Date**: `test_date`, `testdate`, `test date`, `date`, `date_time`, `date & time`, `timestamp`, `collection_date`
- **Unit**: `unit`, `units`, `measurement_unit`, `test_unit`

#### Additional Fields

- **Lab Technician**: `lab_technician`, `technician`, `operator`, `tech`, `performed_by`
- **Notes**: `notes`, `comments`, `remarks`, `observation`

### 🔧 **Smart Data Processing**

#### Data Cleaning

- **Text Normalization**: Removes extra spaces, handles null values
- **Gender Standardization**: Converts `M/F`, `Male/Female`, `1/2` to standard format
- **Numeric Conversion**: Safely converts test values to numbers
- **Date Parsing**: Handles multiple date formats automatically

#### Date Format Support

- `2024-01-15` (ISO format)
- `15/01/2024` (DD/MM/YYYY)
- `01/15/2024` (MM/DD/YYYY)
- `15-01-2024` (DD-MM-YYYY)
- `2024/01/15` (YYYY/MM/DD)
- `15.01.2024` (DD.MM.YYYY)
- `2024-01-15 14:30:00` (with time)
- `15-Jan-2024` (with month names)
- `Jan 15, 2024` (US format)

### 📊 **Data Validation**

- **Essential Field Checking**: Ensures required data is present
- **Range Validation**: Checks for reasonable age (0-150) and test value ranges
- **Data Quality Reporting**: Provides detailed validation messages
- **Error Recovery**: Continues processing valid rows even if some rows have errors

## Using the Flexible Import System

### Step 1: Select CSV File

1. Click **"Browse"** to select your CSV file from SD card or computer
2. Choose appropriate **file encoding** if needed (usually UTF-8 works)
3. Click **"Analyze File"** to start automatic detection

### Step 2: Verify Column Mapping

1. Review **auto-detected mappings** in the table
2. **Manual adjustments**: If needed, use the dropdown menus to correct mappings
3. **Essential fields** are highlighted if missing
4. Click **"Update Mapping"** after manual changes

### Step 3: Preview Data

1. Review the **data preview** showing how your data will be imported
2. Check that **patient IDs**, **ages**, **genders**, and **test values** look correct
3. Verify **date formatting** appears properly

### Step 4: Import Data

1. Click **"Validate Data"** to check for issues before import
2. Review validation results and warnings
3. Click **"Import Data"** to add data to the database
4. Monitor progress bar during import

## Supported Device Formats

### Example 1: BIO-CHEQ Device Format

```csv
Sr. No.,Device ID,Patient ID,Barcode ID,Patient ID_BIOCHEQ,OPD/IPD,Age,Gender,Test type,Parameters,Test Value,Unit,Date & Time,BIO-CHEQ Notes
1,DEV001,P001,BC12345,BQ001,OPD,45,Male,Blood Test,Blood Glucose,105.5,mg/dL,2024-01-15 09:30:00,Normal reading
```

**Auto-detected mappings:**

- Patient ID → Barcode ID
- Age → Age
- Gender → Gender
- Test Name → Parameters
- Test Value → Test Value
- Test Date → Date & Time
- Unit → Unit

### Example 2: Generic Lab Device

```csv
Patient,Test,Result,Units,Date,Age,Sex,Notes
P001,Glucose,95.5,mg/dL,2024-01-15,45,M,Fasting
```

**Auto-detected mappings:**

- Patient ID → Patient
- Test Name → Test
- Test Value → Result
- Unit → Units
- Test Date → Date
- Age → Age
- Gender → Sex
- Notes → Notes

### Example 3: Hospital Information System Export

```csv
ID,FirstName,LastName,DOB,Gender,TestName,Value,TestDate,Reference
12345,John,Doe,1979-01-01,Male,Hemoglobin,14.5,2024-01-15,Normal
```

**Auto-detected mappings:**

- Patient ID → ID
- First Name → FirstName
- Last Name → LastName
- Gender → Gender
- Test Name → TestName
- Test Value → Value
- Test Date → TestDate

## Advanced Features

### 🎯 **Column Confidence Scoring**

The system scores potential column matches:

- **Exact match**: 100 points (perfect match)
- **Partial match**: 30-99 points (substring match)
- **Minimum threshold**: 30 points (below this, mapping is ignored)

### 🔍 **Flexible Encoding Support**

Automatically tries multiple text encodings:

- UTF-8 (default)
- Latin-1
- CP1252 (Windows)
- ISO-8859-1

### 🧹 **Data Quality Features**

- **Duplicate detection**: Identifies potential duplicate entries
- **Suspicious value flagging**: Flags extremely high/low values
- **Missing data handling**: Provides options for incomplete records
- **Age calculation**: Can calculate age from date of birth if available

## Troubleshooting

### Common Issues

#### "Could not auto-detect columns"

- **Solution**: Use manual column mapping
- **Check**: Verify CSV file has headers in first row
- **Verify**: Ensure essential columns (Patient ID, Test Value) are present

#### "Non-numeric test values found"

- **Cause**: Test results contain text or special characters
- **Solution**: Clean data in CSV file or use data cleaning features
- **Alternative**: Map to notes field if not actual test values

#### "Invalid date format"

- **Cause**: Date format not recognized
- **Solution**: System will use current date as fallback
- **Manual fix**: Standardize dates in CSV before import

#### "No valid data rows remain"

- **Cause**: All rows failed validation
- **Check**: Verify patient IDs are not empty
- **Check**: Ensure test values are numeric
- **Review**: Column mappings for accuracy

### Best Practices

#### Preparing CSV Files

1. **Include headers**: First row should contain column names
2. **Remove empty columns**: Delete completely empty columns
3. **Standardize dates**: Use consistent date format if possible
4. **Clean patient IDs**: Remove extra spaces or special characters

#### Column Mapping Tips

1. **Start with essentials**: Map Patient ID and Test Value first
2. **Use preview**: Always review preview before import
3. **Check units**: Ensure units are correctly mapped
4. **Verify dates**: Confirm date format in preview

#### Data Quality Checks

1. **Run validation**: Always validate before final import
2. **Review warnings**: Address validation warnings when possible
3. **Sample testing**: Test with small sample first
4. **Backup data**: Keep original CSV files as backup

## Integration with Custom Ranges

The flexible import system works seamlessly with the **Custom Test Ranges** feature:

1. **Automatic range application**: Imported data automatically uses custom ranges if available
2. **Demographic matching**: Age/gender from CSV used for range selection
3. **Condition support**: Can import condition information for specialized ranges
4. **Range creation**: New test types are created with default ranges

## Performance Considerations

### Large File Handling

- **Memory efficient**: Processes data in chunks for large files
- **Progress tracking**: Shows import progress for large datasets
- **Error recovery**: Continues processing even if individual rows fail
- **Batch processing**: Optimized database operations for speed

### Validation Speed

- **Smart validation**: Only validates essential fields by default
- **Parallel processing**: Multiple validation checks run simultaneously
- **Early termination**: Stops validation if critical errors found
- **Incremental feedback**: Provides real-time validation status

## API Reference

### FlexibleDataProcessor Class

#### Key Methods

```python
# Analyze CSV file and detect column mappings
preview_csv_with_mapping(file_path, encoding='utf-8')

# Clean and convert data based on mappings
clean_and_convert_data(dataframe, column_mapping)

# Validate processed data
validate_processed_data(dataframe)

# Import data with flexible mappings
import_flexible_csv(file_path, column_mapping, encoding='utf-8')
```

#### Column Pattern Configuration

```python
# Customize column detection patterns
processor.column_patterns['custom_field'] = ['pattern1', 'pattern2']

# Add ignore patterns for irrelevant columns
processor.ignore_patterns.append('custom_ignore_pattern')
```

## Future Enhancements

### Planned Features

1. **Excel file support**: Direct import from .xlsx files
2. **Template creation**: Generate CSV templates for specific devices
3. **Mapping profiles**: Save and reuse column mappings
4. **Advanced validation**: Custom validation rules per test type
5. **Data transformation**: Built-in data conversion functions

### Integration Possibilities

1. **HL7 support**: Direct integration with HL7 messages
2. **API endpoints**: REST API for programmatic data import
3. **Real-time import**: Monitor folders for automatic import
4. **Cloud sync**: Synchronize with cloud-based lab systems

This flexible import system ensures your medical test management system can handle data from virtually any medical device or laboratory information system, making it truly adaptable to real-world clinical environments! 🏥✅
