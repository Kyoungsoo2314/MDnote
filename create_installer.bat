@echo off
REM ========================================
REM MDnote Installer Builder
REM Automatically creates single-file installer
REM ========================================

echo.
echo ========================================
echo  MDnote Installer Builder
echo ========================================
echo.

REM Check if dist/md_viewer.exe exists
if not exist "dist\md_viewer.exe" (
    echo [ERROR] dist\md_viewer.exe not found!
    echo.
    echo Please run build.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "install_internal.bat" (
    echo [ERROR] install_internal.bat not found!
    pause
    exit /b 1
)

if not exist "README.txt" (
    echo [ERROR] README.txt not found!
    pause
    exit /b 1
)

echo [1/2] Building installer with IExpress...
echo.

REM Run IExpress with .sed configuration
iexpress /N mdnote_installer.sed

if %errorLevel% neq 0 (
    echo.
    echo [ERROR] IExpress failed!
    echo Please check mdnote_installer.sed configuration.
    pause
    exit /b 1
)

echo.
echo [2/2] Verifying installer...
if exist "MDnote-Setup.exe" (
    echo.
    echo ========================================
    echo   Build Complete!
    echo ========================================
    echo.
    echo Created: MDnote-Setup.exe
    echo.
    for %%A in ("MDnote-Setup.exe") do echo Size: %%~zA bytes
    echo.
    echo This single file contains:
    echo  - MDnote executable
    echo  - Installation script
    echo  - README documentation
    echo.
    echo You can now distribute MDnote-Setup.exe!
    echo.
) else (
    echo.
    echo [ERROR] MDnote-Setup.exe was not created!
    pause
    exit /b 1
)

echo ========================================
echo Next steps:
echo ========================================
echo.
echo 1. Test the installer:
echo    MDnote-Setup.exe
echo.
echo 2. Copy to Git repository:
echo    copy MDnote-Setup.exe markdown-viewer-git\
echo.
echo 3. Upload to GitHub Releases
echo.

pause
