/**
 * Repository-related tool handlers
 */

import { McpError, ErrorCode } from "@modelcontextprotocol/sdk/types.js";
import { ToolHandler } from "../utils/handler-types.js";
import { formatResponse } from "../utils/response-formatter.js";
import { Request, Response } from "express";
import axios from "axios";

/**
 * List projects handler
 */
export const listProjects: ToolHandler = async (params, context) => {
  const { search, owned, membership, per_page } = params.arguments || {};
  const response = await context.axiosInstance.get("/projects", {
    params: {
      search,
      owned: owned === true ? true : undefined,
      membership: membership === true ? true : undefined,
      per_page: per_page || 20,
    },
  });

  return formatResponse(response.data);
};

/**
 * Get project details handler
 */
export const getProject: ToolHandler = async (params, context) => {
  const { project_id } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, "project_id is required");
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(String(project_id))}`
  );
  return formatResponse(response.data);
};

/**
 * List branches handler
 */
export const listBranches: ToolHandler = async (params, context) => {
  const { project_id, search } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, "project_id is required");
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(String(project_id))}/repository/branches`,
    { params: { search } }
  );
  return formatResponse(response.data);
};

/**
 * List merge requests handler
 */
export const listMergeRequests: ToolHandler = async (params, context) => {
  const { project_id, state, scope } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, "project_id is required");
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(String(project_id))}/merge_requests`,
    { params: { state, scope } }
  );
  return formatResponse(response.data);
};

/**
 * Get merge request details handler
 */
export const getMergeRequest: ToolHandler = async (params, context) => {
  const { project_id, merge_request_iid } = params.arguments || {};
  if (!project_id || !merge_request_iid) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id and merge_request_iid are required"
    );
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/merge_requests/${merge_request_iid}`
  );
  return formatResponse(response.data);
};

/**
 * Get merge request changes handler
 */
export const getMergeRequestChanges: ToolHandler = async (params, context) => {
  const { project_id, merge_request_iid } = params.arguments || {};
  if (!project_id || !merge_request_iid) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id and merge_request_iid are required"
    );
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/merge_requests/${merge_request_iid}/changes`
  );
  return formatResponse(response.data);
};

/**
 * Create merge request note handler
 */
export const createMergeRequestNote: ToolHandler = async (params, context) => {
  const { project_id, merge_request_iid, body } = params.arguments || {};
  if (!project_id || !merge_request_iid || !body) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id, merge_request_iid, and body are required"
    );
  }

  const response = await context.axiosInstance.post(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/merge_requests/${merge_request_iid}/notes`,
    { body }
  );
  return formatResponse(response.data);
};

/**
 * List issues handler
 */
export const listIssues: ToolHandler = async (params, context) => {
  const { project_id, state, labels } = params.arguments || {};
  if (!project_id) {
    throw new McpError(ErrorCode.InvalidParams, "project_id is required");
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(String(project_id))}/issues`,
    { params: { state, labels } }
  );
  return formatResponse(response.data);
};

/**
 * Get repository file handler
 */
export const getRepositoryFile: ToolHandler = async (params, context) => {
  const { project_id, file_path, ref } = params.arguments || {};
  if (!project_id || !file_path) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id and file_path are required"
    );
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/repository/files/${encodeURIComponent(String(file_path))}`,
    { params: { ref: ref || "main" } }
  );
  return formatResponse(response.data);
};

/**
 * Compare branches handler
 */
export const compareBranches: ToolHandler = async (params, context) => {
  const { project_id, from, to } = params.arguments || {};
  if (!project_id || !from || !to) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id, from, and to are required"
    );
  }

  const response = await context.axiosInstance.get(
    `/projects/${encodeURIComponent(String(project_id))}/repository/compare`,
    { params: { from, to } }
  );
  return formatResponse(response.data);
};

/**
 * Update merge request title and description handler
 */
export const updateMergeRequest: ToolHandler = async (params, context) => {
  const { project_id, merge_request_iid, title, description } =
    params.arguments || {};
  if (!project_id || !merge_request_iid) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id and merge_request_iid are required"
    );
  }

  if (!title && !description) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "At least one of title or description is required"
    );
  }

  const response = await context.axiosInstance.put(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/merge_requests/${merge_request_iid}`,
    { title, description }
  );
  return formatResponse(response.data);
};

/**
 * Create merge request note handler with internal note option
 */
export const createMergeRequestNoteInternal: ToolHandler = async (
  params,
  context
) => {
  const { project_id, merge_request_iid, body, internal } =
    params.arguments || {};
  if (!project_id || !merge_request_iid || !body) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id, merge_request_iid, and body are required"
    );
  }

  const response = await context.axiosInstance.post(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/merge_requests/${merge_request_iid}/notes`,
    { body, internal: internal === true }
  );
  return formatResponse(response.data);
};

/**
 * Create merge request thread handler
 */
export const createMergeRequestThread: ToolHandler = async (
  params,
  context
) => {
  const {
    project_id,
    merge_request_iid,
    body,
    position_type = "text",
    base_sha,
    start_sha,
    head_sha,
    new_path,
    new_line,
    old_path,
    old_line,
    width,
    height,
    x,
    y,
    line_range,
  } = params.arguments || {};

  if (
    !project_id ||
    !merge_request_iid ||
    !body ||
    !base_sha ||
    !start_sha ||
    !head_sha
  ) {
    throw new McpError(
      ErrorCode.InvalidParams,
      "project_id, merge_request_iid, body, base_sha, start_sha, head_sha are required"
    );
  }

  // Build position object based on provided params
  const position: any = {
    position_type,
    base_sha,
    start_sha,
    head_sha,
  };

  if (new_path) position.new_path = new_path;
  if (new_line) position.new_line = new_line;
  if (old_path) position.old_path = old_path;
  if (old_line) position.old_line = old_line;
  if (line_range) position.line_range = line_range;

  if (position_type === "image") {
    if (width) position.width = width;
    if (height) position.height = height;
    if (x !== undefined) position.x = x;
    if (y !== undefined) position.y = y;
  }

  const response = await context.axiosInstance.post(
    `/projects/${encodeURIComponent(
      String(project_id)
    )}/merge_requests/${merge_request_iid}/discussions`,
    {
      body,
      position,
    }
  );

  return formatResponse(response.data);
};
