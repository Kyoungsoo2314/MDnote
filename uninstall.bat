@echo off
REM ========================================
REM Markdown Viewer - Uninstaller
REM ========================================

echo.
echo ========================================
echo Markdown Viewer Uninstaller
echo ========================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Running with administrator privileges
    set "ADMIN=1"
) else (
    echo [INFO] Running without administrator privileges
    echo       Will uninstall user-only installation
    set "ADMIN=0"
)

echo.
choice /C YN /M "Do you want to uninstall Markdown Viewer"
if errorlevel 2 goto :cancel
if errorlevel 1 goto :uninstall

:uninstall
echo.
echo Uninstalling...
echo.

if "%ADMIN%"=="1" (
    REM System-wide uninstallation
    echo [1/4] Removing registry entries (system-wide)...
    reg delete "HKEY_LOCAL_MACHINE\Software\Classes\.md" /f >nul 2>&1
    reg delete "HKEY_LOCAL_MACHINE\Software\Classes\MarkdownViewer.Document" /f >nul 2>&1

    echo [2/4] Removing files...
    if exist "%ProgramFiles%\MarkdownViewer" (
        rmdir /S /Q "%ProgramFiles%\MarkdownViewer" >nul 2>&1
        echo     Removed: %ProgramFiles%\MarkdownViewer
    )

    echo [3/4] Removing Start Menu shortcut...
    if exist "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Markdown Viewer.lnk" (
        del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Markdown Viewer.lnk" >nul 2>&1
    )
)

REM User-level uninstallation (always run)
echo [1/4] Removing registry entries (user)...
reg delete "HKEY_CURRENT_USER\Software\Classes\.md" /f >nul 2>&1
reg delete "HKEY_CURRENT_USER\Software\Classes\MarkdownViewer.Document" /f >nul 2>&1

echo [2/4] Removing files...
if exist "%LOCALAPPDATA%\Programs\MarkdownViewer" (
    rmdir /S /Q "%LOCALAPPDATA%\Programs\MarkdownViewer" >nul 2>&1
    echo     Removed: %LOCALAPPDATA%\Programs\MarkdownViewer
)

echo [3/4] Removing Start Menu shortcut...
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Markdown Viewer.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Markdown Viewer.lnk" >nul 2>&1
)

REM Remove user settings (optional)
echo.
choice /C YN /M "Do you want to remove user settings and recent files"
if errorlevel 1 (
    echo [4/4] Removing user settings...
    if exist "%APPDATA%\md_viewer" (
        rmdir /S /Q "%APPDATA%\md_viewer" >nul 2>&1
        echo     Removed: %APPDATA%\md_viewer
    )
) else (
    echo [4/4] Keeping user settings...
)

REM Refresh system
echo.
echo Refreshing system...
ie4uinit.exe -show >nul 2>&1

echo.
echo ========================================
echo Uninstallation Complete!
echo ========================================
echo.
goto :end

:cancel
echo.
echo Uninstallation cancelled.
echo.

:end
pause
