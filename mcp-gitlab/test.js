#!/usr/bin/env node

/**
 * Test script for the GitLab MCP server
 * 
 * This script tests the GitLab MCP server by listing projects.
 * It requires a GitLab API token to be set in the environment.
 * 
 * Usage:
 * GITLAB_API_TOKEN=your_token node test.js
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

// Get the directory of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Path to the built server
const serverPath = resolve(__dirname, 'build/index.js');

// Check if GitLab API token is provided
const GITLAB_API_TOKEN = process.env.GITLAB_API_TOKEN;
if (!GITLAB_API_TOKEN) {
  console.error('Error: GITLAB_API_TOKEN environment variable is required');
  console.error('Usage: GITLAB_API_TOKEN=your_token node test.js');
  process.exit(1);
}

// Start the server process
const serverProcess = spawn('node', [serverPath], {
  env: {
    ...process.env,
    GITLAB_API_TOKEN
  },
  stdio: ['pipe', 'pipe', 'inherit'] // Pipe stdin/stdout, inherit stderr
});

// Handle server process errors
serverProcess.on('error', (error) => {
  console.error('Failed to start server process:', error);
  process.exit(1);
});

// Prepare the list projects request
const listProjectsRequest = {
  jsonrpc: '2.0',
  id: 1,
  method: 'callTool',
  params: {
    name: 'gitlab_list_projects',
    arguments: {
      membership: true,
      per_page: 5
    }
  }
};

// Send the request to the server
serverProcess.stdin.write(JSON.stringify(listProjectsRequest) + '\n');

// Handle server response
let responseData = '';
serverProcess.stdout.on('data', (data) => {
  responseData += data.toString();
  
  try {
    // Try to parse the response as JSON
    const response = JSON.parse(responseData);
    
    // Check if the response is valid
    if (response.id === 1) {
      console.log('Test successful! Server responded with:');
      console.log(JSON.stringify(response.result, null, 2));
      
      // Terminate the server process
      serverProcess.kill();
      process.exit(0);
    }
  } catch (error) {
    // If the response is not complete JSON yet, continue collecting data
  }
});

// Set a timeout to prevent hanging
setTimeout(() => {
  console.error('Test timed out after 10 seconds');
  serverProcess.kill();
  process.exit(1);
}, 10000);