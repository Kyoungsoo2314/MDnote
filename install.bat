@echo off
REM ========================================
REM Markdown Viewer - One-Click Installer
REM ========================================
REM This script will:
REM 1. Copy the executable to Program Files
REM 2. Register .md file association
REM 3. Create Start Menu shortcut
REM ========================================

echo.
echo ========================================
echo Markdown Viewer Installer v2.0
echo ========================================
echo.
echo This installer will:
echo  - Install Markdown Viewer to your system
echo  - Associate .md files with this viewer
echo  - Create a Start Menu shortcut
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with administrator privileges
    echo.
    goto :install
) else (
    echo [WARNING] Not running as administrator
    echo.
    echo For system-wide installation, please run as administrator.
    echo.
    choice /C YN /M "Install for current user only (Y) or Cancel (N)"
    if errorlevel 2 goto :cancel
    if errorlevel 1 goto :install_user
)

:install
REM Administrator installation
echo.
echo ========================================
echo Installing for all users...
echo ========================================
echo.

REM Set installation directory
set "INSTALL_DIR=%ProgramFiles%\MarkdownViewer"
set "EXE_PATH=%INSTALL_DIR%\md_viewer.exe"

REM Create installation directory
echo [1/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo [2/5] Copying executable...
if exist "dist\md_viewer.exe" (
    copy /Y "dist\md_viewer.exe" "%INSTALL_DIR%\" >nul
    echo     Copied to: %INSTALL_DIR%
) else (
    echo     ERROR: dist\md_viewer.exe not found!
    echo     Please run build.bat first.
    pause
    exit /b 1
)

REM Register file association (HKEY_LOCAL_MACHINE)
echo [3/5] Registering .md file association...
reg add "HKEY_LOCAL_MACHINE\Software\Classes\.md" /ve /d "MarkdownViewer.Document" /f >nul
reg add "HKEY_LOCAL_MACHINE\Software\Classes\MarkdownViewer.Document" /ve /d "Markdown Document" /f >nul
reg add "HKEY_LOCAL_MACHINE\Software\Classes\MarkdownViewer.Document\DefaultIcon" /ve /d "\"%EXE_PATH%\",0" /f >nul
reg add "HKEY_LOCAL_MACHINE\Software\Classes\MarkdownViewer.Document\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul
echo     Registered .md file association

REM Create Start Menu shortcut
echo [4/5] Creating Start Menu shortcut...
set "SHORTCUT_DIR=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_DIR%\Markdown Viewer.lnk'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.Save()" >nul 2>&1
echo     Created shortcut in Start Menu

REM Refresh icon cache
echo [5/5] Refreshing system...
ie4uinit.exe -show >nul 2>&1

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installed to: %INSTALL_DIR%
echo.
echo You can now:
echo  1. Double-click any .md file to open it
echo  2. Find "Markdown Viewer" in Start Menu
echo.
goto :end

:install_user
REM User-only installation
echo.
echo ========================================
echo Installing for current user only...
echo ========================================
echo.

REM Set installation directory
set "INSTALL_DIR=%LOCALAPPDATA%\Programs\MarkdownViewer"
set "EXE_PATH=%INSTALL_DIR%\md_viewer.exe"

REM Create installation directory
echo [1/5] Creating installation directory...
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy executable
echo [2/5] Copying executable...
if exist "dist\md_viewer.exe" (
    copy /Y "dist\md_viewer.exe" "%INSTALL_DIR%\" >nul
    echo     Copied to: %INSTALL_DIR%
) else (
    echo     ERROR: dist\md_viewer.exe not found!
    echo     Please run build.bat first.
    pause
    exit /b 1
)

REM Register file association (HKEY_CURRENT_USER)
echo [3/5] Registering .md file association...
reg add "HKEY_CURRENT_USER\Software\Classes\.md" /ve /d "MarkdownViewer.Document" /f >nul
reg add "HKEY_CURRENT_USER\Software\Classes\MarkdownViewer.Document" /ve /d "Markdown Document" /f >nul
reg add "HKEY_CURRENT_USER\Software\Classes\MarkdownViewer.Document\DefaultIcon" /ve /d "\"%EXE_PATH%\",0" /f >nul
reg add "HKEY_CURRENT_USER\Software\Classes\MarkdownViewer.Document\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f >nul
echo     Registered .md file association

REM Create Start Menu shortcut
echo [4/5] Creating Start Menu shortcut...
set "SHORTCUT_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT_DIR%\Markdown Viewer.lnk'); $Shortcut.TargetPath = '%EXE_PATH%'; $Shortcut.Save()" >nul 2>&1
echo     Created shortcut in Start Menu

REM Refresh icon cache
echo [5/5] Refreshing system...
ie4uinit.exe -show >nul 2>&1

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installed to: %INSTALL_DIR%
echo.
echo You can now:
echo  1. Double-click any .md file to open it
echo  2. Find "Markdown Viewer" in Start Menu
echo.
goto :end

:cancel
echo.
echo Installation cancelled.
echo.
goto :end

:end
pause
