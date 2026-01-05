@echo off
REM ========================================
REM MDnote Internal Installer Script
REM Used by IExpress self-extracting archive
REM ========================================

echo.
echo ========================================
echo       MDnote v2.0 Installation
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Installing for all users...
    set "INSTALL_DIR=%ProgramFiles%\MDnote"
    set "SHORTCUT_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
    set "REG_ROOT=HKLM"
) else (
    echo [OK] Installing for current user...
    set "INSTALL_DIR=%LOCALAPPDATA%\Programs\MDnote"
    set "SHORTCUT_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
    set "REG_ROOT=HKCU"
)

set "EXE_PATH=%INSTALL_DIR%\md_viewer.exe"

REM Create installation directory
echo [1/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable (extracted by IExpress to temp folder)
echo [2/5] Installing MDnote...
copy /Y "%~dp0md_viewer.exe" "%INSTALL_DIR%\" >nul
if %errorLevel% neq 0 (
    echo     ERROR: Failed to copy executable
    pause
    exit /b 1
)
echo     Installed to: %INSTALL_DIR%

REM Register file association
echo [3/5] Registering .md file association...
reg add "%REG_ROOT%\Software\Classes\.md" /ve /d "MDnote.Document" /f >nul
reg add "%REG_ROOT%\Software\Classes\MDnote.Document" /ve /d "Markdown Document" /f >nul
reg add "%REG_ROOT%\Software\Classes\MDnote.Document\DefaultIcon" /ve /d "\"%EXE_PATH%\",0" /f >nul
reg add "%REG_ROOT%\Software\Classes\MDnote.Document\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul
echo     Registered .md files to open with MDnote

REM Create Start Menu shortcut
echo [4/5] Creating Start Menu shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_DIR%\MDnote.lnk'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.Description = 'MDnote - Markdown Viewer'; $Shortcut.Save()" >nul 2>&1
echo     Created: Start Menu\MDnote

REM Refresh icon cache
echo [5/5] Refreshing system...
ie4uinit.exe -show >nul 2>&1

echo.
echo ========================================
echo    Installation Completed!
echo ========================================
echo.
echo Installed to: %INSTALL_DIR%
echo.
echo You can now:
echo  - Double-click any .md file to open it
echo  - Find "MDnote" in Start Menu
echo.

REM Show README
if exist "%~dp0README.txt" (
    echo Opening README...
    timeout /t 2 /nobreak >nul
    notepad "%~dp0README.txt"
)

exit /b 0
