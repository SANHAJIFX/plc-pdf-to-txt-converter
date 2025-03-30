@echo off
echo PLC Program PDF to Structured Text Converter
echo ==========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python 3.6 or later and try again.
    echo You can download Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Install required dependencies
echo Installing required dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies. Please check your internet connection and try again.
    pause
    exit /b 1
)

REM Run the conversion script
echo.
echo Running conversion script...
python pdf_to_structured_text.py
if %errorlevel% neq 0 (
    echo Conversion failed. Please check the error message above.
    pause
    exit /b 1
)

echo.
echo Conversion completed successfully! The converted files are in the ConvertedProgram directory.
echo.

pause