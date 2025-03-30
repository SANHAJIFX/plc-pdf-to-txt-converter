@echo off
echo PLC Program PDF to TXT Converter
echo ============================
echo.

set /p clean_dir="Do you want to clean the output directory first? (Y/N): "
if /i "%clean_dir%"=="Y" (
    echo Cleaning output directory...
    if exist PlainTextFiles (
        del /Q PlainTextFiles\*.* 2>nul
        echo Output directory cleaned.
    ) else (
        echo Output directory does not exist. It will be created.
    )
)

echo.
echo Converting files...
echo This may take several minutes for large files.
echo Files larger than 2MB will be automatically split into multiple parts.
echo.

REM Run the conversion script
python convert_to_txt.py
if %errorlevel% neq 0 (
    echo.
    echo Conversion failed. Please check the error message above.
    pause
    exit /b 1
)

echo.
echo Conversion completed successfully!
echo.
echo All files have been converted to TXT format and are available in the PlainTextFiles directory.
echo No file exceeds 2MB in size.
echo.
echo Notes:
echo - Large files have been split into multiple parts with prefixes like "_part01", "_part02", etc.
echo - Each part file includes headers that indicate which part it is and how to navigate between parts.
echo.

pause