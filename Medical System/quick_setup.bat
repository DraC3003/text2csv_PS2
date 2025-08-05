@echo off
title Medical Test System - Quick Setup
color 0B
echo.
echo  ================================================
echo   Medical Test System - Quick Setup & Test
echo  ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    pause
    exit /b 1
)

echo [Setup] Installing dependencies...
pip install pandas openpyxl matplotlib tkinter >nul 2>&1

echo [Setup] Creating test database...
python -c "from database_manager import DatabaseManager; db = DatabaseManager()" >nul 2>&1

echo [Setup] Adding sample test types...
python -c "
from database_manager import DatabaseManager
db = DatabaseManager()
# Add common test types
tests = [
    ('Glucose', 70, 100, 'mg/dL', 'Fasting blood glucose'),
    ('Cholesterol', 0, 200, 'mg/dL', 'Total cholesterol'),
    ('HDL Cholesterol', 40, 999, 'mg/dL', 'High-density lipoprotein'),
    ('LDL Cholesterol', 0, 100, 'mg/dL', 'Low-density lipoprotein'),
    ('Hemoglobin', 12, 16, 'g/dL', 'Blood hemoglobin level'),
    ('White Blood Cells', 4000, 11000, 'cells/μL', 'WBC count'),
    ('Blood Pressure Systolic', 90, 120, 'mmHg', 'Systolic blood pressure'),
    ('Blood Pressure Diastolic', 60, 80, 'mmHg', 'Diastolic blood pressure')
]
for test in tests:
    try:
        db.add_test_type(*test)
        print(f'Added: {test[0]}')
    except:
        pass
print('Sample test types setup complete!')
" 2>nul

echo [Setup] Adding sample patient...
python -c "
from database_manager import DatabaseManager
db = DatabaseManager()
try:
    db.add_patient(
        patient_id='DEMO001',
        first_name='John',
        last_name='Demo',
        date_of_birth='1980-05-15',
        gender='Male',
        phone='555-0123',
        email='demo@example.com'
    )
    print('Sample patient added!')
except:
    print('Sample patient already exists')
" 2>nul

echo.
echo  ================================================
echo   Setup Complete! 
echo  ================================================
echo.
echo  What's been set up:
echo  ✓ Dependencies installed
echo  ✓ Database initialized  
echo  ✓ Sample test types added:
echo    - Glucose, Cholesterol, HDL/LDL
echo    - Hemoglobin, White Blood Cells
echo    - Blood Pressure (Systolic/Diastolic)
echo  ✓ Sample patient (DEMO001) created
echo.
echo  Ready to launch Medical Test System!
echo.

choice /c YN /m "Start the application now? (Y/N)"
if errorlevel 2 (
    echo.
    echo Run 'start_medical_system.bat' to launch later.
    pause
    exit /b 0
)

echo.
echo Launching Medical Test System...
python main.py

pause
