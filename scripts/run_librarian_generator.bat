@echo off
echo ========================================================
echo Running AI Librarian Generator
echo ========================================================
echo.
echo This script will:
echo   1. Clean existing librarian files
echo   2. Generate mini-librarians for all Python files
echo   3. Create script_index.json (limited to 500KB)
echo.
echo NOTE: This will overwrite any existing librarian files
echo.
echo ========================================================

cd /d %~dp0\..\.ai_reference

echo.
echo Executing librarian generator...
python generate_mini_librarians.py

echo.
echo ========================================================
echo AI Librarian generation complete!
echo.
echo After making significant code changes, run this script
echo again to keep the AI Librarian system up-to-date.
echo ========================================================
echo.
pause
