/**
 * Common types and interfaces for GitLab tool handlers
 */

import { AxiosInstance } from "axios";
import { CallToolRequest } from "@modelcontextprotocol/sdk/types.js";
import { IntegrationsManager } from "../integrations.js";
import { CiCdManager } from "../ci-cd.js";
import { UsersGroupsManager } from "../users-groups.js";

/**
 * Context object passed to all tool handlers
 */
export interface HandlerContext {
  axiosInstance: AxiosInstance;
  integrationsManager: IntegrationsManager;
  ciCdManager: CiCdManager;
  usersGroupsManager: UsersGroupsManager;
}

/**
 * Function signature for tool handlers
 */
export type ToolHandler = (
  params: CallToolRequest['params'],
  context: HandlerContext
) => Promise<any>;

/**
 * Definition for tool registry
 */
export interface ToolRegistry {
  [toolName: string]: ToolHandler;
} 