# Test Type Management Guide

## How to Add New Test Types and Ranges

### Using the Test Types Tab

The medical test system now includes a dedicated **Test Types** tab for managing test types and their normal ranges. Here's how to use it:

### Adding a New Test Type

1. **Open the Test Types Tab**

   - Launch the medical test application
   - Click on the "Test Types" tab

2. **Fill in Test Information**

   - **Test Name\*** (Required): Enter the name of the test (e.g., "Total Protein", "Vitamin D", "Hemoglobin A1c")
   - **Normal Range**: Enter the minimum and maximum values for normal results
   - **Unit**: Select or enter the unit of measurement (mg/dL, g/dL, etc.)
   - **Description**: Add a brief description of what the test measures
   - **Critical Thresholds**: Optionally set values that indicate urgent medical attention

3. **Save the Test Type**
   - Click "Add Test Type" to save the new test type
   - The system will validate your input and confirm successful addition

### Example Test Types to Add

#### Blood Chemistry Tests

- **Total Protein**: 6.0-8.0 g/dL
- **Albumin**: 3.5-5.0 g/dL
- **Globulin**: 2.0-3.5 g/dL
- **Vitamin D**: 30-100 ng/mL
- **Vitamin B12**: 200-900 pg/mL

#### Cardiac Markers

- **Troponin I**: 0.0-0.04 ng/mL
- **CK-MB**: 0-6.3 ng/mL
- **BNP**: 0-100 pg/mL

#### Hormones

- **TSH**: 0.4-4.0 mIU/L
- **Free T4**: 0.8-1.8 ng/dL
- **Testosterone**: Varies by age/gender
- **Cortisol**: 6-23 mcg/dL

#### Lipid Profile

- **Total Cholesterol**: <200 mg/dL
- **HDL Cholesterol**: >40 mg/dL (men), >50 mg/dL (women)
- **LDL Cholesterol**: <100 mg/dL
- **Triglycerides**: <150 mg/dL

### Managing Existing Test Types

#### Viewing Test Types

- The right panel shows all existing test types
- Use the search box to quickly find specific tests
- Click on any test to select and edit it

#### Editing Test Types

1. Select a test type from the list
2. Modify the information in the form
3. Click "Update Test Type" to save changes

#### Deleting Test Types

1. Select a test type from the list
2. Click "Delete Test Type"
3. Confirm the deletion (this will also remove all test results of this type)

### Setting Up Age/Gender-Specific Ranges

After creating a test type, you can set up custom ranges for different demographics:

1. Go to the **Custom Ranges** tab
2. Select your test type
3. Add specific ranges for:
   - Different age groups
   - Male vs. female patients
   - Special conditions

### Best Practices

#### Naming Conventions

- Use clear, standard medical terminology
- Include common abbreviations in parentheses when helpful
- Examples: "Hemoglobin A1c (HbA1c)", "Prostate Specific Antigen (PSA)"

#### Units

- Use standard medical units
- Be consistent across similar tests
- Common units: mg/dL, g/dL, mmHg, bpm, U/L, cells/μL, %, ng/mL

#### Normal Ranges

- Use established reference ranges from medical literature
- Consider your laboratory's specific ranges
- Leave ranges blank for qualitative tests (Positive/Negative)

#### Critical Values

- Set critical low/high values for tests that require immediate attention
- Examples:
  - Glucose: Critical low <50 mg/dL, Critical high >400 mg/dL
  - Potassium: Critical low <2.5 mEq/L, Critical high >6.0 mEq/L

### Programmatic Access

You can also add test types programmatically using the database manager:

```python
from database_manager import DatabaseManager

db = DatabaseManager()
success = db.add_test_type(
    test_name="Vitamin D",
    normal_min=30.0,
    normal_max=100.0,
    unit="ng/mL",
    description="25-hydroxyvitamin D level"
)
```

### Common Medical Tests Database

The system comes pre-configured with common tests, but you can add specialized tests for your practice:

#### Endocrinology

- Insulin levels
- DHEA-S
- Growth hormone
- Parathyroid hormone (PTH)

#### Immunology

- IgG, IgA, IgM levels
- Complement C3, C4
- Rheumatoid factor
- Anti-nuclear antibodies (ANA)

#### Oncology Markers

- AFP (Alpha-fetoprotein)
- CEA (Carcinoembryonic antigen)
- CA 19-9
- CA 125

#### Infectious Disease

- Hepatitis B surface antigen
- HIV antibodies
- C-reactive protein (CRP)
- Procalcitonin

### Troubleshooting

#### Common Issues

1. **Test name already exists**: Choose a more specific name or check if the test is already in the system
2. **Invalid range values**: Ensure minimum is less than maximum
3. **Missing units**: Add appropriate units for better reporting

#### Tips

- Use the search function to check if a test already exists
- Review the test list regularly to maintain consistency
- Back up your database before making bulk changes

### Integration with Other Features

After adding test types:

- They become available in the Test Results tab
- CSV import will recognize these tests by name
- Reports will use the defined normal ranges
- Custom ranges can be added for specific demographics

This test type management system provides the flexibility to adapt the medical test system to any healthcare practice's specific needs while maintaining data integrity and proper medical standards.
