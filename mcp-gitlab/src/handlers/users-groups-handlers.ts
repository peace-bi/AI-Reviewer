/**
 * Users and Groups related tool handlers
 */

import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { ToolHandler } from "../utils/handler-types.js";
import { formatResponse } from "../utils/response-formatter.js";

/**
 * List users handler
 */
export const listUsers: ToolHandler = async (params, context) => {
  const { username, search, active, blocked, external } = params.arguments || {};
  
  const data = await context.usersGroupsManager.listUsers({
    username: username as string | undefined,
    search: search as string | undefined,
    active: active as boolean | undefined,
    blocked: blocked as boolean | undefined,
    external: external as boolean | undefined
  });
  return formatResponse(data);
};

/**
 * Get user handler
 */
export const getUser: ToolHandler = async (params, context) => {
  const { user_id } = params.arguments || {};
  if (!user_id) {
    throw new McpError(ErrorCode.InvalidParams, 'user_id is required');
  }
  
  const data = await context.usersGroupsManager.getUser(user_id as number);
  return formatResponse(data);
};

/**
 * List groups handler
 */
export const listGroups: ToolHandler = async (params, context) => {
  const { search, owned, min_access_level } = params.arguments || {};
  
  const data = await context.usersGroupsManager.listGroups({
    search: search as string | undefined,
    owned: owned as boolean | undefined,
    min_access_level: min_access_level as number | undefined
  });
  return formatResponse(data);
};

/**
 * Get group handler
 */
export const getGroup: ToolHandler = async (params, context) => {
  const { group_id } = params.arguments || {};
  if (!group_id) {
    throw new McpError(ErrorCode.InvalidParams, 'group_id is required');
  }
  
  const data = await context.usersGroupsManager.getGroup(group_id as string | number);
  return formatResponse(data);
};

/**
 * List group members handler
 */
export const listGroupMembers: ToolHandler = async (params, context) => {
  const { group_id } = params.arguments || {};
  if (!group_id) {
    throw new McpError(ErrorCode.InvalidParams, 'group_id is required');
  }
  
  const data = await context.usersGroupsManager.listGroupMembers(group_id as string | number);
  return formatResponse(data);
};

/**
 * Add group member handler
 */
export const addGroupMember: ToolHandler = async (params, context) => {
  const { group_id, user_id, access_level, expires_at } = params.arguments || {};
  if (!group_id || !user_id || !access_level) {
    throw new McpError(ErrorCode.InvalidParams, 'group_id, user_id, and access_level are required');
  }
  
  const data = await context.usersGroupsManager.addGroupMember(
    group_id as string | number,
    user_id as number,
    access_level as number,
    expires_at as string | undefined
  );
  return formatResponse(data);
};

/**
 * List project members handler
 */
export const listProjectMembers: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.usersGroupsManager.listProjectMembers(project_id as string | number);
  return formatResponse(data);
};

/**
 * Add project member handler
 */
export const addProjectMember: ToolHandler = async (params, context) => {
  const { project_id, user_id, access_level, expires_at } = params.arguments || {};
  if (!project_id || !user_id || !access_level) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id, user_id, and access_level are required');
  }
  
  const data = await context.usersGroupsManager.addProjectMember(
    project_id as string | number,
    user_id as number,
    access_level as number,
    expires_at as string | undefined
  );
  return formatResponse(data);
}; 