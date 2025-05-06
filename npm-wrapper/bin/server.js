#!/usr/bin/env node

/**
 * AI Dev Toolkit MCP Server Launcher
 * 
 * This script launches the Python-based AI Dev Toolkit MCP server using uv.
 * It handles platform-specific paths and ensures proper environment setup.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');
const os = require('os');

// Find the toolkit directory relative to this script
const scriptDir = __dirname;
const packageDir = path.dirname(scriptDir);
const repoDir = path.dirname(packageDir);

// Determine platform-specific command
const isWindows = os.platform() === 'win32';
const uvCommand = isWindows ? 'uv.cmd' : 'uv';

// Function to find Python server script - looks in common locations
function findServerScript() {
  const possibleLocations = [
    // When installed via npm (relative to the wrapper)
    path.join(repoDir, 'src', 'server.py'),
    // When running from repo root
    path.join(packageDir, '..', 'src', 'server.py'),
    // When running in development mode
    path.join(process.cwd(), 'src', 'server.py')
  ];

  for (const location of possibleLocations) {
    if (fs.existsSync(location)) {
      return location;
    }
  }

  console.error('Error: Could not find server.py in any expected location');
  console.error('Looked in:');
  possibleLocations.forEach(loc => console.error(`- ${loc}`));
  process.exit(1);
}

// Get server script path
const serverScript = findServerScript();
console.log(`Found server script at: ${serverScript}`);
const serverDir = path.dirname(path.dirname(serverScript));

// Construct args for uv
const args = [
  'run',
  serverScript
];

// Pass any command line arguments to the Python script
// These will be treated as project directories
const projectDirs = process.argv.slice(2);

// If we have project directories, pass them to the server
if (projectDirs.length > 0) {
  console.log(`Project directories: ${projectDirs.join(', ')}`);
  projectDirs.forEach(dir => args.push(dir));
}

console.log(`Starting AI Dev Toolkit with uv...`);
console.log(`Command: ${uvCommand} ${args.join(' ')}`);

// Launch server with the proper environment
const server = spawn(uvCommand, args, {
  stdio: 'inherit',
  env: {
    ...process.env,
    PYTHONPATH: serverDir
  }
});

// Handle process events
server.on('error', (err) => {
  console.error(`Failed to start AI Dev Toolkit: ${err.message}`);
  if (err.code === 'ENOENT') {
    console.error(`
Error: Could not find the 'uv' command. Make sure you have the uv Python package manager installed.
Installation instructions:
  • macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
  • Windows: curl.exe -LsSf https://astral.sh/uv/install.ps1 | pwsh
  
For more details, visit: https://github.com/astral-sh/uv
`);
  }
  process.exit(1);
});

server.on('close', (code) => {
  if (code !== 0) {
    console.error(`AI Dev Toolkit exited with code ${code}`);
  }
  process.exit(code);
});

// Handle termination signals
process.on('SIGINT', () => {
  server.kill('SIGINT');
});

process.on('SIGTERM', () => {
  server.kill('SIGTERM');
});
