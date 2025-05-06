@echo off
REM AI Dev Toolkit GUI Launcher
REM This batch file launches the AI Dev Toolkit GUI

echo Starting AI Dev Toolkit Control Panel...

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Python executable - use the one in PATH or a specific version
python %SCRIPT_DIR%\launch_gui.py

REM If there was an error, pause to show messages
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to launch GUI. See error messages above.
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
