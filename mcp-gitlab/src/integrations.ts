/**
 * GitLab Integrations Manager
 * 
 * This module provides functions for managing GitLab project integrations/webhooks
 * through the GitLab API.
 */

import axios, { AxiosInstance } from "axios";

/**
 * Class to manage GitLab project integrations and webhooks
 */
export class IntegrationsManager {
  private axiosInstance: AxiosInstance;

  constructor(axiosInstance: AxiosInstance) {
    this.axiosInstance = axiosInstance;
  }

  /**
   * List all active integrations for a project
   * 
   * @param projectId ID or URL-encoded path of the project
   * @returns List of project integrations
   */
  async listIntegrations(projectId: string | number) {
    try {
      const response = await this.axiosInstance.get(`/projects/${encodeURIComponent(String(projectId))}/integrations`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to list integrations');
    }
  }

  /**
   * Get details of a specific integration
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param integrationSlug Slug of the integration (e.g., 'slack', 'jira', 'gitlab-slack-application')
   * @returns Integration details
   */
  async getIntegration(projectId: string | number, integrationSlug: string) {
    try {
      const response = await this.axiosInstance.get(`/projects/${encodeURIComponent(String(projectId))}/integrations/${integrationSlug}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get integration: ${integrationSlug}`);
    }
  }

  /**
   * Update GitLab Slack integration
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param options Integration settings to update
   * @returns Updated integration settings
   */
  async updateSlackIntegration(projectId: string | number, options: any) {
    try {
      const response = await this.axiosInstance.put(
        `/projects/${encodeURIComponent(String(projectId))}/integrations/gitlab-slack-application`,
        options
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to update Slack integration');
    }
  }

  /**
   * Disable GitLab Slack integration
   * 
   * @param projectId ID or URL-encoded path of the project
   * @returns Response data
   */
  async disableSlackIntegration(projectId: string | number) {
    try {
      const response = await this.axiosInstance.delete(
        `/projects/${encodeURIComponent(String(projectId))}/integrations/gitlab-slack-application`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to disable Slack integration');
    }
  }

  /**
   * List project webhooks
   * 
   * @param projectId ID or URL-encoded path of the project
   * @returns List of project webhooks
   */
  async listWebhooks(projectId: string | number) {
    try {
      const response = await this.axiosInstance.get(`/projects/${encodeURIComponent(String(projectId))}/hooks`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to list webhooks');
    }
  }

  /**
   * Get details of a specific webhook
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param webhookId ID of the webhook
   * @returns Webhook details
   */
  async getWebhook(projectId: string | number, webhookId: number) {
    try {
      const response = await this.axiosInstance.get(
        `/projects/${encodeURIComponent(String(projectId))}/hooks/${webhookId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get webhook: ${webhookId}`);
    }
  }

  /**
   * Add a webhook to a project
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param options Webhook options
   * @returns Created webhook details
   */
  async addWebhook(projectId: string | number, options: {
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
  }) {
    try {
      const response = await this.axiosInstance.post(
        `/projects/${encodeURIComponent(String(projectId))}/hooks`,
        options
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to add webhook');
    }
  }

  /**
   * Update a project webhook
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param webhookId ID of the webhook
   * @param options Webhook options to update
   * @returns Updated webhook details
   */
  async updateWebhook(projectId: string | number, webhookId: number, options: {
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
  }) {
    try {
      const response = await this.axiosInstance.put(
        `/projects/${encodeURIComponent(String(projectId))}/hooks/${webhookId}`,
        options
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to update webhook: ${webhookId}`);
    }
  }

  /**
   * Delete a project webhook
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param webhookId ID of the webhook
   * @returns Response data
   */
  async deleteWebhook(projectId: string | number, webhookId: number) {
    try {
      const response = await this.axiosInstance.delete(
        `/projects/${encodeURIComponent(String(projectId))}/hooks/${webhookId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to delete webhook: ${webhookId}`);
    }
  }

  /**
   * Test a project webhook
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param webhookId ID of the webhook
   * @param triggerType Type of trigger to test
   * @returns Response data
   */
  async testWebhook(projectId: string | number, webhookId: number, triggerType: string) {
    try {
      const response = await this.axiosInstance.post(
        `/projects/${encodeURIComponent(String(projectId))}/hooks/${webhookId}/test/${triggerType}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to test webhook: ${webhookId}`);
    }
  }

  /**
   * Handle API errors
   * 
   * @param error Error object
   * @param defaultMessage Default error message
   * @returns Error object with appropriate message
   */
  private handleError(error: any, defaultMessage: string) {
    if (axios.isAxiosError(error)) {
      return new Error(`${defaultMessage}: ${error.response?.data?.message || error.message}`);
    }
    return new Error(`${defaultMessage}: ${error.message}`);
  }
}
