/**
 * Utility functions for formatting MCP responses
 */

import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

/**
 * Format an API response for MCP protocol
 *
 * @param data The data to format
 * @returns Formatted MCP response
 */
export function formatResponse(data: any) {
  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(data),
      },
    ],
  };
}

/**
 * Handle errors from API calls
 *
 * @param error The error object
 * @param defaultMessage Default message to use
 * @returns McpError object
 */
export function handleApiError(
  error: unknown,
  defaultMessage: string
): McpError {
  if (axios.isAxiosError(error)) {
    return new McpError(
      ErrorCode.InternalError,
      `GitLab API error: ${error.response?.data?.message || error.message}`
    );
  }
  if (error instanceof Error) {
    return new McpError(
      ErrorCode.InternalError,
      `${defaultMessage}: ${error.message}`
    );
  }
  return new McpError(ErrorCode.InternalError, defaultMessage);
}
