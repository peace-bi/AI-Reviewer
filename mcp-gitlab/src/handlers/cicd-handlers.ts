/**
 * CI/CD-related tool handlers
 */

import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { ToolHandler } from "../utils/handler-types.js";
import { formatResponse } from "../utils/response-formatter.js";

/**
 * List trigger tokens handler
 */
export const listTriggerTokens: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.ciCdManager.listTriggerTokens(project_id as string | number);
  return formatResponse(data);
};

/**
 * Get trigger token handler
 */
export const getTriggerToken: ToolHandler = async (params, context) => {
  const { project_id, trigger_id } = params.arguments || {};
  if (!project_id || !trigger_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and trigger_id are required');
  }
  
  const data = await context.ciCdManager.getTriggerToken(project_id as string | number, trigger_id as number);
  return formatResponse(data);
};

/**
 * Create trigger token handler
 */
export const createTriggerToken: ToolHandler = async (params, context) => {
  const { project_id, description } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.ciCdManager.createTriggerToken(project_id as string | number, description as string);
  return formatResponse(data);
};

/**
 * Update trigger token handler
 */
export const updateTriggerToken: ToolHandler = async (params, context) => {
  const { project_id, trigger_id, description } = params.arguments || {};
  if (!project_id || !trigger_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and trigger_id are required');
  }
  
  const data = await context.ciCdManager.updateTriggerToken(project_id as string | number, trigger_id as number, description as string);
  return formatResponse(data);
};

/**
 * Delete trigger token handler
 */
export const deleteTriggerToken: ToolHandler = async (params, context) => {
  const { project_id, trigger_id } = params.arguments || {};
  if (!project_id || !trigger_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and trigger_id are required');
  }
  
  const data = await context.ciCdManager.deleteTriggerToken(project_id as string | number, trigger_id as number);
  return formatResponse(data);
};

/**
 * Trigger pipeline handler
 */
export const triggerPipeline: ToolHandler = async (params, context) => {
  const { project_id, ref, token, variables } = params.arguments || {};
  if (!project_id || !ref || !token) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id, ref, and token are required');
  }
  
  const data = await context.ciCdManager.triggerPipeline(
    project_id as string | number, 
    ref as string, 
    token as string, 
    variables as Record<string, string> | undefined
  );
  return formatResponse(data);
};

/**
 * List CI/CD variables handler
 */
export const listCiCdVariables: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.ciCdManager.listCiCdVariables(project_id as string | number);
  return formatResponse(data);
};

/**
 * Get CI/CD variable handler
 */
export const getCiCdVariable: ToolHandler = async (params, context) => {
  const { project_id, key } = params.arguments || {};
  if (!project_id || !key) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and key are required');
  }
  
  const data = await context.ciCdManager.getCiCdVariable(project_id as string | number, key as string);
  return formatResponse(data);
};

/**
 * Create CI/CD variable handler
 */
export const createCiCdVariable: ToolHandler = async (params, context) => {
  const { project_id, key, value, protected: isProtected, masked, variable_type, environment_scope } = params.arguments || {};
  if (!project_id || !key || !value) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id, key, and value are required');
  }
  
  const data = await context.ciCdManager.createCiCdVariable(project_id as string | number, {
    key: key as string,
    value: value as string,
    protected: isProtected as boolean | undefined,
    masked: masked as boolean | undefined,
    variable_type: variable_type as 'env_var' | 'file' | undefined,
    environment_scope: environment_scope as string | undefined
  });
  return formatResponse(data);
};

/**
 * Update CI/CD variable handler
 */
export const updateCiCdVariable: ToolHandler = async (params, context) => {
  const { project_id, key, value, protected: isProtected, masked, variable_type, environment_scope } = params.arguments || {};
  if (!project_id || !key) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and key are required');
  }
  
  const data = await context.ciCdManager.updateCiCdVariable(project_id as string | number, key as string, {
    value: value as string,
    protected: isProtected as boolean | undefined,
    masked: masked as boolean | undefined,
    variable_type: variable_type as 'env_var' | 'file' | undefined,
    environment_scope: environment_scope as string | undefined
  });
  return formatResponse(data);
};

/**
 * Delete CI/CD variable handler
 */
export const deleteCiCdVariable: ToolHandler = async (params, context) => {
  const { project_id, key } = params.arguments || {};
  if (!project_id || !key) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and key are required');
  }
  
  const data = await context.ciCdManager.deleteCiCdVariable(project_id as string | number, key as string);
  return formatResponse(data);
}; 