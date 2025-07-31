@echo off
title Glucose Processor

echo ===============================================
echo    GLUCOSE ANALYSIS PROCESSOR
echo ===============================================
echo.
echo This will process your EIPL CSV file and create
echo a protected Excel report with colored analysis.
echo.
echo APPEND MODE: If you have added new patients to 
echo your EIPL CSV, you can append them to the 
echo existing Excel file instead of overwriting it.
echo.
echo ===============================================

python glucose_medical_processor.py

echo.
echo Analysis complete! Check the generated Excel file.
echo.
pause
