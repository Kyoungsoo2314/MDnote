@echo off
REM MDnote Build Script

echo ========================================
echo Building MDnote
echo ========================================
echo.

REM Install required libraries
echo Installing required libraries...
pip install -r requirements.txt

echo.
echo ========================================
echo Building executable with PyInstaller...
echo ========================================
echo.

REM Build executable with PyInstaller
python -m PyInstaller --onefile --windowed --icon=md_viewer.ico --name md_viewer md_viewer.py

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Executable location: dist\md_viewer.exe
echo.
echo Next steps:
echo 1. Test dist\md_viewer.exe file
echo 2. Run register_md_viewer.bat as administrator to associate .md files
echo.
pause
