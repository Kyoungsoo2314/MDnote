@echo off
REM Markdown Viewer File Association Script (User Level)
REM No administrator privileges required

echo ========================================
echo Markdown Viewer File Association Setup
echo (Current User Only)
echo ========================================
echo.

REM Get current directory path
set "CURRENT_DIR=%~dp0"
set "EXE_PATH=%CURRENT_DIR%dist\md_viewer.exe"

echo Executable path: %EXE_PATH%
echo.

REM Check if executable exists
if not exist "%EXE_PATH%" (
    echo ERROR: md_viewer.exe not found!
    echo Please run build.bat first to create the executable.
    echo.
    pause
    exit /b 1
)

REM Associate .md file extension (User level - no admin required)
echo Associating .md files with Markdown Viewer...
reg add "HKEY_CURRENT_USER\Software\Classes\.md" /ve /d "MarkdownFile" /f
reg add "HKEY_CURRENT_USER\Software\Classes\MarkdownFile" /ve /d "Markdown Document" /f
reg add "HKEY_CURRENT_USER\Software\Classes\MarkdownFile\DefaultIcon" /ve /d "%EXE_PATH%,0" /f
reg add "HKEY_CURRENT_USER\Software\Classes\MarkdownFile\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Now you can double-click .md files to open with Markdown Viewer.
echo (This setting applies only to your user account)
echo.
pause
