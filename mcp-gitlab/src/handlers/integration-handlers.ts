/**
 * Integration-related tool handlers
 */

import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { ToolHandler } from "../utils/handler-types.js";
import { formatResponse } from "../utils/response-formatter.js";

/**
 * List integrations handler
 */
export const listIntegrations: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.integrationsManager.listIntegrations(project_id as string | number);
  return formatResponse(data);
};

/**
 * Get integration handler
 */
export const getIntegration: ToolHandler = async (params, context) => {
  const { project_id, integration_slug } = params.arguments || {};
  if (!project_id || !integration_slug) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and integration_slug are required');
  }
  
  const data = await context.integrationsManager.getIntegration(project_id as string | number, integration_slug as string);
  return formatResponse(data);
};

/**
 * Update Slack integration handler
 */
export const updateSlackIntegration: ToolHandler = async (params, context) => {
  const { project_id, webhook, username, channel, notify_only_broken_pipelines, notify_only_default_branch, ...options } = params.arguments || {};
  if (!project_id || !webhook) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and webhook are required');
  }
  
  const data = await context.integrationsManager.updateSlackIntegration(project_id as string | number, {
    webhook,
    username,
    channel,
    notify_only_broken_pipelines,
    notify_only_default_branch,
    ...options
  });
  return formatResponse(data);
};

/**
 * Disable Slack integration handler
 */
export const disableSlackIntegration: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.integrationsManager.disableSlackIntegration(project_id as string | number);
  return formatResponse(data);
};

/**
 * List webhooks handler
 */
export const listWebhooks: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  const data = await context.integrationsManager.listWebhooks(project_id as string | number);
  return formatResponse(data);
};

/**
 * Get webhook handler
 */
export const getWebhook: ToolHandler = async (params, context) => {
  const { project_id, webhook_id } = params.arguments || {};
  if (!project_id || !webhook_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and webhook_id are required');
  }
  
  const data = await context.integrationsManager.getWebhook(project_id as string | number, webhook_id as number);
  return formatResponse(data);
};

/**
 * Add webhook handler
 */
export const addWebhook: ToolHandler = async (params, context) => {
  const { project_id, ...options } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id is required');
  }
  
  if (!options.url) {
    throw new McpError(ErrorCode.InvalidParams, 'url is required for webhook');
  }
  
  const data = await context.integrationsManager.addWebhook(project_id as string | number, options as {
    url: string;
    name?: string;
    description?: string;
    token?: string;
    push_events?: boolean;
    push_events_branch_filter?: string;
    issues_events?: boolean;
    confidential_issues_events?: boolean;
    merge_requests_events?: boolean;
    tag_push_events?: boolean;
    note_events?: boolean;
    confidential_note_events?: boolean;
    job_events?: boolean;
    pipeline_events?: boolean;
    wiki_page_events?: boolean;
    deployment_events?: boolean;
    releases_events?: boolean;
    feature_flag_events?: boolean;
    enable_ssl_verification?: boolean;
    custom_webhook_template?: string;
    custom_headers?: Array<{key: string; value?: string}>;
  });
  return formatResponse(data);
};

/**
 * Update webhook handler
 */
export const updateWebhook: ToolHandler = async (params, context) => {
  const { project_id, webhook_id, ...options } = params.arguments || {};
  if (!project_id || !webhook_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and webhook_id are required');
  }
  
  if (!options.url) {
    throw new McpError(ErrorCode.InvalidParams, 'url is required for webhook');
  }
  
  const data = await context.integrationsManager.updateWebhook(project_id as string | number, webhook_id as number, options as {
    url: string;
    name?: string;
    description?: string;
    token?: string;
    push_events?: boolean;
    push_events_branch_filter?: string;
    issues_events?: boolean;
    confidential_issues_events?: boolean;
    merge_requests_events?: boolean;
    tag_push_events?: boolean;
    note_events?: boolean;
    confidential_note_events?: boolean;
    job_events?: boolean;
    pipeline_events?: boolean;
    wiki_page_events?: boolean;
    deployment_events?: boolean;
    releases_events?: boolean;
    feature_flag_events?: boolean;
    enable_ssl_verification?: boolean;
    custom_webhook_template?: string;
    custom_headers?: Array<{key: string; value?: string}>;
  });
  return formatResponse(data);
};

/**
 * Delete webhook handler
 */
export const deleteWebhook: ToolHandler = async (params, context) => {
  const { project_id, webhook_id } = params.arguments || {};
  if (!project_id || !webhook_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and webhook_id are required');
  }
  
  const data = await context.integrationsManager.deleteWebhook(project_id as string | number, webhook_id as number);
  return formatResponse(data);
};

/**
 * Test webhook handler
 */
export const testWebhook: ToolHandler = async (params, context) => {
  const { project_id, webhook_id, trigger_type } = params.arguments || {};
  if (!project_id || !webhook_id) {
    throw new McpError(ErrorCode.InvalidParams, 'project_id and webhook_id are required');
  }
  
  const data = await context.integrationsManager.testWebhook(
    project_id as string | number, 
    webhook_id as number, 
    (trigger_type as string) || 'push_events'
  );
  return formatResponse(data);
}; 