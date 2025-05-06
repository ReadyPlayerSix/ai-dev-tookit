#!/usr/bin/env node

/**
 * AI Dev Toolkit Dependency Checker
 * 
 * This script checks if the required dependencies (uv and Python) are installed
 * and guides the user on how to install them if they're missing.
 */

const { execSync } = require('child_process');
const os = require('os');

// Check if a command exists by running it
function commandExists(command) {
  try {
    execSync(`${command} --version`, { stdio: 'ignore' });
    return true;
  } catch (e) {
    return false;
  }
}

// Main check function
function checkDependencies() {
  const isWindows = os.platform() === 'win32';
  const uvCommand = isWindows ? 'uv.cmd' : 'uv';
  const pythonCommand = isWindows ? 'python' : 'python3';
  
  console.log('Checking for required dependencies...');
  
  // Check Python
  if (!commandExists(pythonCommand)) {
    console.error(`
⚠️ Python not found. The AI Dev Toolkit requires Python 3.8 or higher.
Please install Python from: https://www.python.org/downloads/
`);
  } else {
    try {
      const pythonVersion = execSync(`${pythonCommand} --version`).toString().trim();
      console.log(`✅ ${pythonVersion} found.`);
    } catch (e) {
      console.log('✅ Python found (unable to determine version).');
    }
  }
  
  // Check uv
  if (!commandExists(uvCommand)) {
    console.warn(`
⚠️ The 'uv' package manager is not installed. AI Dev Toolkit requires uv to run.
Installation instructions:
  • macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
  • Windows PowerShell: curl.exe -LsSf https://astral.sh/uv/install.ps1 | pwsh
  
For more information, visit: https://github.com/astral-sh/uv
`);
  } else {
    console.log('✅ uv package manager found.');
  }
  
  // Additional instructions
  console.log(`
AI Dev Toolkit NPM Wrapper
--------------------------
This package is a wrapper around the Python AI Dev Toolkit MCP server.
To use with Claude Desktop, add the following to your configuration:

{
  "mcpServers": {
    "ai-dev-toolkit": {
      "command": "npx",
      "args": ["-y", "@isekaizen/ai-dev-toolkit"]
    }
  }
}

For manual execution, run: npx @isekaizen/ai-dev-toolkit
`);
}

// Run the check
checkDependencies();
