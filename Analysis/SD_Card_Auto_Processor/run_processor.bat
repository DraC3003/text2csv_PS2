@echo off
echo SD Card Auto Processor
echo =====================
echo.
echo This tool will:
echo 1. Detect SD card or prompt for path
echo 2. Read text files with medical data
echo 3. Identify test types (Cal, Glucose, Hb, Chloride)
echo 4. Append data to appropriate EIPL CSV files
echo.
pause
echo.
echo Starting processing...
python main.py
echo.
echo Processing complete! Check the logs folder for details.
pause
