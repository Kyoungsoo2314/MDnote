@echo off
REM Markdown Viewer File Association Script
REM Must be run as Administrator

echo ========================================
echo Markdown Viewer File Association Setup
echo ========================================
echo.

REM Get current directory path
set "CURRENT_DIR=%~dp0"
set "EXE_PATH=%CURRENT_DIR%dist\md_viewer.exe"

echo Executable path: %EXE_PATH%
echo.

REM Associate .md file extension
echo Associating .md files with Markdown Viewer...
reg add "HKEY_CLASSES_ROOT\.md" /ve /d "MarkdownFile" /f
reg add "HKEY_CLASSES_ROOT\MarkdownFile" /ve /d "Markdown Document" /f
reg add "HKEY_CLASSES_ROOT\MarkdownFile\DefaultIcon" /ve /d "%EXE_PATH%,0" /f
reg add "HKEY_CLASSES_ROOT\MarkdownFile\shell\open\command" /ve /d "\"%EXE_PATH%\" \"%%1\"" /f

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Now you can double-click .md files to open with Markdown Viewer.
echo.
pause
