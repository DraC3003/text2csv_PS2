# SD Card Auto Processor

This tool automatically processes medical test data from SD cards and appends it to the appropriate EIPL CSV files in the analyzer folders.

## 🎯 Purpose

- **Input:** Text files from SD card with medical test data
- **Process:** Automatically identify test types and map data to correct format
- **Output:** Data appended to appropriate EIPL CSV files in analyzer folders

## 📁 Project Structure

```
SD_Card_Auto_Processor/
├── main.py                    # Main processor script
├── run_processor.bat         # Windows batch file to run the tool
├── requirements.txt          # Python dependencies (none needed!)
├── sample_sd_data.txt       # Sample input format
├── config/
│   ├── test_mappings.json   # Column mappings for each test
│   └── default_values.json  # Default values for missing data
├── processors/
│   ├── sd_reader.py         # Reads SD card text files
│   ├── test_identifier.py   # Identifies test types
│   └── csv_appender.py      # Appends to EIPL CSV files
└── logs/
    └── (processing logs will appear here)
```

## 📝 SD Card Data Format

**Required Format:** `PatientID, TestName, Age, Gender, Reading, [Optional Fields...]`

### Examples:

```
PMT24205895, Cal, 45, Female, 9.67, Yes, No, Fasting
PMT25001685, Glucose, 28, Male, 121
PMT24140363, Hb, 21, Female, 9.97
PMT25088925, Chloride, 27, Male, 91.5
```

### Supported Test Names:

- **Calcium:** Cal, Calcium
- **Glucose:** Glucose, Gluc
- **Hemoglobin:** Hb, Hemoglobin, Haemoglobin
- **Chloride:** Chloride, Cholride, Cl

## 🚀 How to Use

### Method 1: Double-click the batch file

1. Insert SD card into computer
2. Double-click `run_processor.bat`
3. The tool will auto-detect the SD card and process all text files

### Method 2: Run Python directly

```bash
cd SD_Card_Auto_Processor
python main.py
```

### Method 3: Specify custom path

Edit `main.py` and change:

```python
processor.process_sd_card("D:\\your_custom_path")
```

## 🔧 How It Works

1. **SD Card Detection:** Auto-detects drives D: through K: for SD cards
2. **File Reading:** Finds all .txt, .csv, .dat files on the card
3. **Test Identification:** Uses the second column (TestName) to identify test type
4. **Data Mapping:** Maps SD card fields to appropriate EIPL CSV columns
5. **Missing Data Handling:** Fills missing values with sensible defaults
6. **Validation:** Checks required fields before appending
7. **Logging:** Records all activities for troubleshooting

## 🎯 Target Files

Data gets appended to these files:

- **Calcium:** `analyser_Cal/EIPL_BIO-CHEQ_Aabir_1.xlsx - Cal.csv`
- **Glucose:** `analyser_Glucose/EIPL_BIO-CHEQ_Aabir_1.xlsx - Glucose.csv`
- **Hemoglobin:** `analyser_Hb/EIPL_BIO-CHEQ_Aabir_1.xlsx - Hb.csv`
- **Chloride:** `analyser_Chloride/EIPL_BIO-CHEQ_Aabir_1.xlsx - Chloride.csv`

## 📊 Default Values

When data is missing, these defaults are used:

- **Age:** 30 (instead of 0)
- **Gender:** "Not Specified"
- **Smoking Status:** "Unknown"
- **Alcohol Consumption:** "Unknown"
- **Date & Time:** Current timestamp

## 📋 After Processing

1. Check the `logs/` folder for processing details
2. Run the appropriate batch file in the analyzer folder:
   - `analyser_Cal/run_calcium_processor.bat`
   - `analyser_Glucose/run_glucose_processor.bat`
   - `analyser_Hb/run_hb_processor.bat`
   - `analyser_Chloride/run_chloride_processor.bat`

## 🔍 Adding New Tests

To add a new test type:

1. **Update `test_mappings.json`:**

```json
"NewTest": {
  "folder_name": "analyser_NewTest",
  "eipl_file": "EIPL_NewTest.csv",
  "columns": ["Sr. No.", "Patient ID", ...],
  "sd_card_mapping": {
    "Patient ID": 0,
    "Age": 2,
    "Gender": 3,
    "Reading": 4
  },
  "required_fields": ["Patient ID", "Reading"],
  "test_type_identifier": ["NewTest", "NT"]
}
```

2. **Update `default_values.json`** if needed
3. **No code changes required!**

## ⚠️ Important Notes

- **Backup your EIPL files** before first use
- The tool **appends** data - it doesn't overwrite existing records
- Check logs if processing fails
- Ensure SD card text files follow the expected format
- Run analyzer batch files manually after processing

## 🐛 Troubleshooting

- **No SD card detected:** Specify path manually in `main.py`
- **No records processed:** Check `sample_sd_data.txt` for format reference
- **Missing columns:** Update `test_mappings.json` configuration
- **Permission errors:** Run as Administrator if needed

## 📞 Support

Check the logs folder for detailed error messages and processing statistics.
