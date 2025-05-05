@echo off
echo ========================================================
echo AI Dev Toolkit - Project Generator
echo ========================================================
echo.
echo This script will:
echo   1. Generate a project structure from the project plan
echo   2. Create necessary project files
echo   3. Set up GitHub repository instructions
echo.
echo NOTE: Ensure Python 3.8+ is installed on your system
echo.
echo ========================================================

setlocal

set PROJECT_PLAN=..\docs\project-plan.md
set OUTPUT_DIR=..\ai-dev-toolkit

if not exist %PROJECT_PLAN% (
    echo ERROR: Project plan file not found: %PROJECT_PLAN%
    echo Please ensure the file exists in the current directory.
    goto :EOF
)

echo.
echo Generating project from plan: %PROJECT_PLAN%
echo Output directory: %OUTPUT_DIR%
echo.

python project-generator-script.py %PROJECT_PLAN% %OUTPUT_DIR%

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo ERROR: Project generation failed!
    echo Please check the error messages above.
    echo ========================================================
    goto :EOF
)

echo.
echo ========================================================
echo Project generation complete!
echo.
echo Your new project has been created at: %OUTPUT_DIR%
echo.
echo Next steps:
echo   1. Review the generated project structure
echo   2. Follow the GitHub setup instructions in GITHUB_SETUP.md
echo   3. Run the server with 'python src/server.py'
echo ========================================================
echo.
pause