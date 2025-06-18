/**
 * Resource handlers for GitLab MCP Server
 */

import { AxiosInstance } from "axios";
import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { handleApiError } from "./response-formatter.js";

/**
 * Handle the listing of resources
 * 
 * @param axiosInstance The axios instance for API calls
 * @returns Response with available resources
 */
export async function handleListResources(axiosInstance: AxiosInstance) {
  return {
    resources: [
      {
        uri: 'gitlab://projects',
        name: 'GitLab Projects',
        description: 'List of GitLab projects accessible to the authenticated user'
      }
    ]
  };
}

/**
 * Handle reading of resources
 * 
 * @param uri Resource URI to read
 * @param axiosInstance The axios instance for API calls
 * @returns Resource contents
 */
export async function handleReadResource(uri: string, axiosInstance: AxiosInstance) {
  try {
    // Handle different resource types
    if (uri === 'gitlab://projects') {
      const response = await axiosInstance.get('/projects', {
        params: { membership: true, per_page: 20 }
      });
      
      return {
        contents: [{
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(response.data, null, 2)
        }]
      };
    }
    
    // Handle project-specific resources
    const projectMatch = uri.match(/^gitlab:\/\/projects\/(\d+)$/);
    if (projectMatch) {
      const projectId = projectMatch[1];
      const response = await axiosInstance.get(`/projects/${projectId}`);
      
      return {
        contents: [{
          uri,
          mimeType: 'application/json',
          text: JSON.stringify(response.data, null, 2)
        }]
      };
    }
    
    throw new McpError(ErrorCode.InvalidRequest, `Resource not found: ${uri}`);
  } catch (error) {
    throw handleApiError(error, `Failed to read resource: ${uri}`);
  }
} 