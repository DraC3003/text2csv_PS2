# Custom Test Ranges Feature

## Overview

The Custom Test Ranges feature allows healthcare professionals to define and manage custom normal value ranges for medical tests. This is essential for different patient populations, specific conditions, or varying laboratory standards.

## Features

### 1. Custom Range Management

- **Create Custom Ranges**: Define test-specific ranges with demographic and condition filters
- **Edit Existing Ranges**: Modify ranges as medical standards evolve
- **Delete Ranges**: Remove outdated or incorrect ranges
- **List All Ranges**: View all custom ranges in an organized table

### 2. Demographic Filtering

- **Age-Based Ranges**: Set minimum and maximum age limits
- **Gender-Specific Ranges**: Define ranges for Male, Female, or Other
- **Condition-Specific Ranges**: Create ranges for specific medical conditions (e.g., diabetes, CKD)

### 3. Range Types

- **Normal Range**: Define the healthy/normal value range (min-max)
- **Critical Thresholds**: Set critical low and high values for alerts
- **Notes**: Add clinical notes or explanations for the custom range

### 4. Import/Export Functionality

- **JSON Export**: Export all custom ranges to a JSON file for backup or sharing
- **JSON Import**: Import custom ranges from a JSON file
- **Data Portability**: Share range configurations between different installations

## Using the Custom Ranges Interface

### Creating a New Range

1. Navigate to the "Custom Ranges" tab
2. Click "New Range" to clear the form
3. Fill in the required fields:
   - **Test Type**: Select from existing test types
   - **Range Name**: Give a descriptive name (e.g., "Pediatric Range", "Diabetic Monitoring")
   - **Age Range**: Optional - specify minimum and/or maximum age
   - **Gender**: Optional - select specific gender
   - **Condition**: Optional - specify medical condition
   - **Normal Range**: Set the normal minimum and maximum values
   - **Critical Thresholds**: Set critical low and high values
   - **Notes**: Add any relevant clinical notes
4. Click "Save Range"

### Editing an Existing Range

1. Select a range from the list on the left
2. The form will populate with the range data
3. Modify the fields as needed
4. Click "Save Range" to update

### Deleting a Range

1. Select a range from the list
2. Click "Delete"
3. Confirm the deletion

### Import/Export Operations

- **Export**: Click "Export to JSON" and choose a file location
- **Import**: Click "Import from JSON" and select a JSON file containing custom ranges

## JSON File Format

Custom ranges can be imported/exported using JSON files with the following structure:

```json
{
  "custom_test_ranges": [
    {
      "test_name": "Glucose",
      "range_name": "Diabetic Monitoring",
      "age_min": 18,
      "age_max": 80,
      "gender": null,
      "condition_name": "Diabetes",
      "normal_min": 80.0,
      "normal_max": 130.0,
      "critical_low": 70.0,
      "critical_high": 200.0,
      "notes": "Tight glucose control for diabetic patients"
    }
  ]
}
```

### Field Descriptions

- **test_name**: Must match an existing test type in the system
- **range_name**: Descriptive name for the range
- **age_min/age_max**: Optional age limits (null for no limit)
- **gender**: "Male", "Female", "Other", or null
- **condition_name**: Medical condition name or null
- **normal_min/normal_max**: Normal value range
- **critical_low/critical_high**: Critical threshold values (null if not applicable)
- **notes**: Clinical notes or explanations

## How Custom Ranges Are Applied

### Range Selection Priority

When determining the appropriate range for a patient's test result, the system uses the following priority:

1. **Exact Match**: Custom ranges that exactly match the patient's demographics and conditions
2. **Best Partial Match**: Custom ranges that match some criteria (age, gender, or condition)
3. **Default Ranges**: Built-in age/gender-adjusted ranges if no custom ranges match

### Matching Algorithm

The system scores custom ranges based on how well they match the patient:

- **Age Match**: +10 points if patient age falls within the range
- **Gender Match**: +5 points if gender matches exactly
- **Condition Match**: +15 points if condition matches exactly
- **Specificity Bonus**: Additional points for more specific ranges

### Example Scenarios

#### Scenario 1: Diabetic Patient

- Patient: 45-year-old male with diabetes
- Available ranges:
  - "General Adult" (age 18-65, no condition): Score = 10
  - "Diabetic Monitoring" (age 18-80, condition: diabetes): Score = 25
- **Selected**: "Diabetic Monitoring" (higher score)

#### Scenario 2: Pediatric Patient

- Patient: 8-year-old female
- Available ranges:
  - "Adult Range" (age 18+): No match
  - "Pediatric Range" (age 2-12): Score = 15
- **Selected**: "Pediatric Range"

## Clinical Use Cases

### 1. Laboratory Standards

Different laboratories may have different reference ranges due to:

- Equipment variations
- Population demographics
- Testing methodologies

### 2. Special Populations

- **Pediatric patients**: Age-specific ranges for growing children
- **Elderly patients**: Adjusted ranges for age-related changes
- **Pregnant women**: Pregnancy-specific reference ranges

### 3. Disease-Specific Monitoring

- **Diabetes**: Tighter glucose control targets
- **Chronic Kidney Disease**: Modified creatinine ranges
- **Cardiac Risk**: Stricter cholesterol targets

### 4. Research Settings

- **Clinical trials**: Protocol-specific ranges
- **Research studies**: Population-specific baselines

## Best Practices

### 1. Range Naming

- Use descriptive names that indicate the purpose
- Include population or condition information
- Examples: "Pediatric_2-12y", "Diabetic_Tight_Control", "CKD_Stage_3"

### 2. Documentation

- Always include clinical notes explaining the rationale
- Reference medical guidelines or studies when applicable
- Include date of last review or update

### 3. Regular Review

- Periodically review and update ranges based on new medical evidence
- Remove outdated ranges that are no longer clinically relevant
- Keep backup exports before making major changes

### 4. Testing

- Test custom ranges with sample patient data
- Verify that ranges are being applied correctly
- Check critical alerts are functioning properly

## Database Schema

Custom ranges are stored in two main tables:

### custom_test_ranges

- **range_id**: Unique identifier
- **test_type_id**: Links to test_types table
- **range_name**: Descriptive name
- **age_min/age_max**: Age boundaries
- **gender**: Gender specification
- **condition_name**: Associated medical condition
- **normal_min/normal_max**: Normal value range
- **critical_low/critical_high**: Critical thresholds
- **is_active**: Enable/disable flag
- **created_date**: Creation timestamp
- **notes**: Clinical notes

### lab_settings

- **setting_name**: Configuration parameter name
- **setting_value**: Configuration value
- **description**: Setting description

## Troubleshooting

### Common Issues

1. **Range Not Applied**: Check that patient demographics match the custom range criteria
2. **Import Fails**: Verify JSON format and ensure all test names exist in the system
3. **Unexpected Results**: Review the range selection algorithm and scoring

### Validation Rules

- Age minimum must be less than age maximum
- Normal minimum must be less than normal maximum
- Test type must exist in the system
- Range name cannot be empty

## Security Considerations

- Custom ranges should only be modified by authorized healthcare professionals
- Keep audit trails of range changes for clinical safety
- Regular backups of custom range configurations are recommended
