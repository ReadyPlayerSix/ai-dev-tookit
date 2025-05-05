@echo off
echo ========================================================
echo AI Dev Toolkit - Claude Desktop Connection
echo ========================================================
echo.
echo This script will:
echo   1. Check if Claude Desktop is installed
echo   2. Create or update MCP server configuration
echo   3. Restart Claude Desktop (if running)
echo.
echo NOTE: This script works best with administrator privileges
echo.
echo ========================================================

setlocal EnableDelayedExpansion

REM Set path to Claude Desktop config
set "CLAUDE_CONFIG_DIR=%APPDATA%\Claude"
set "CLAUDE_CONFIG_FILE=%CLAUDE_CONFIG_DIR%\config.json"

REM Set MCP server details
set "SERVER_NAME=AI Dev Toolkit"
set "SERVER_URL=http://localhost:8000"
set "WORK_DIR=%CD%"

echo.
echo Checking if Claude Desktop is installed...

REM Check possible installation locations
set "CLAUDE_FOUND=false"
set "CLAUDE_PATH="

for %%P in (
    "%LOCALAPPDATA%\Programs\Claude\Claude.exe"
    "C:\Program Files\Claude\Claude.exe"
    "C:\Program Files (x86)\Claude\Claude.exe"
) do (
    if exist %%P (
        set "CLAUDE_FOUND=true"
        set "CLAUDE_PATH=%%P"
        echo Found Claude Desktop at: %%P
    )
)

if "%CLAUDE_FOUND%"=="false" (
    echo.
    echo Claude Desktop not found in common locations.
    echo Please install Claude Desktop from: https://claude.ai/download
    echo.
    echo After installation, you can connect manually:
    echo 1. Open Claude Desktop
    echo 2. Go to Settings ^> MCP Servers
    echo 3. Click "Add Server"
    echo 4. Enter name: %SERVER_NAME%
    echo 5. Enter URL: %SERVER_URL%
    echo 6. Click "Save" and grant permissions
    goto :EOF
)

echo.
echo Looking for Claude Desktop config...

if not exist "%CLAUDE_CONFIG_DIR%" (
    echo Creating Claude config directory...
    mkdir "%CLAUDE_CONFIG_DIR%"
)

set "CONFIG_UPDATED=false"

if not exist "%CLAUDE_CONFIG_FILE%" (
    echo Creating new Claude config file...
    echo {"mcpServers":[{"name":"%SERVER_NAME%","url":"%SERVER_URL%"}]} > "%CLAUDE_CONFIG_FILE%"
    set "CONFIG_UPDATED=true"
) else (
    echo Updating existing Claude config file...
    
    REM Create a temporary file with PowerShell to properly handle JSON
    powershell -Command "& {
        $config = Get-Content '%CLAUDE_CONFIG_FILE%' -Raw | ConvertFrom-Json
        
        if (-not $config.mcpServers) {
            $config | Add-Member -MemberType NoteProperty -Name 'mcpServers' -Value @()
        }
        
        $serverExists = $false
        foreach ($server in $config.mcpServers) {
            if ($server.name -eq '%SERVER_NAME%') {
                $server.url = '%SERVER_URL%'
                $serverExists = $true
                break
            }
        }
        
        if (-not $serverExists) {
            $config.mcpServers += @{name='%SERVER_NAME%'; url='%SERVER_URL%'}
        }
        
        $config | ConvertTo-Json -Depth 10 | Set-Content '%CLAUDE_CONFIG_FILE%'
    }"
    set "CONFIG_UPDATED=true"
)

if "%CONFIG_UPDATED%"=="true" (
    echo.
    echo Claude Desktop configuration updated successfully!
    
    REM Check if Claude is running and ask to restart
    tasklist /FI "IMAGENAME eq Claude.exe" 2>NUL | find /I /N "Claude.exe">NUL
    if "%ERRORLEVEL%"=="0" (
        echo.
        echo Claude Desktop is currently running.
        echo You need to restart Claude for changes to take effect.
        
        choice /C YN /M "Would you like to restart Claude Desktop now?"
        if "%ERRORLEVEL%"=="1" (
            echo.
            echo Restarting Claude Desktop...
            taskkill /F /IM Claude.exe
            timeout /t 2 >nul
            start "" "%CLAUDE_PATH%"
            echo Claude Desktop has been restarted.
        ) else (
            echo.
            echo Please restart Claude Desktop manually for changes to take effect.
        )
    ) else (
        echo.
        echo Claude Desktop is not currently running.
        
        choice /C YN /M "Would you like to start Claude Desktop now?"
        if "%ERRORLEVEL%"=="1" (
            echo.
            echo Starting Claude Desktop...
            start "" "%CLAUDE_PATH%"
        )
    )
) else (
    echo.
    echo Failed to update Claude Desktop configuration.
    echo.
    echo Please connect manually:
    echo 1. Open Claude Desktop
    echo 2. Go to Settings ^> MCP Servers
    echo 3. Click "Add Server"
    echo 4. Enter name: %SERVER_NAME%
    echo 5. Enter URL: %SERVER_URL%
    echo 6. Click "Save" and grant permissions
)

echo.
echo ========================================================
echo Next steps:
echo   1. Start the MCP server: python src/server.py
echo   2. In Claude Desktop, type "@AI Dev Toolkit" to use tools
echo ========================================================
echo.
pause
