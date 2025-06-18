/**
 * GitLab Users and Groups Manager
 * 
 * This module provides functions for managing GitLab users, groups, and their memberships
 * through the GitLab API.
 */

import axios, { AxiosInstance } from "axios";

/**
 * Class to manage GitLab users and groups
 */
export class UsersGroupsManager {
  private axiosInstance: AxiosInstance;

  constructor(axiosInstance: AxiosInstance) {
    this.axiosInstance = axiosInstance;
  }

  /**
   * List users
   * 
   * @param options Query options
   * @returns List of users
   */
  async listUsers(options?: {
    username?: string;
    search?: string;
    active?: boolean;
    blocked?: boolean;
    external?: boolean;
    exclude_external?: boolean;
    exclude_internal?: boolean;
    order_by?: string;
    sort?: string;
    two_factor?: string;
    without_project_bots?: boolean;
    page?: number;
    per_page?: number;
  }) {
    try {
      const response = await this.axiosInstance.get('/users', { params: options });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to list users');
    }
  }

  /**
   * Get a specific user
   * 
   * @param userId ID of the user
   * @returns User details
   */
  async getUser(userId: number) {
    try {
      const response = await this.axiosInstance.get(`/users/${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get user: ${userId}`);
    }
  }

  /**
   * Create a new user
   * 
   * @param options User options
   * @returns Created user details
   */
  async createUser(options: {
    email: string;
    password?: string;
    reset_password?: boolean;
    force_random_password?: boolean;
    name: string;
    username: string;
    admin?: boolean;
    can_create_group?: boolean;
    skip_confirmation?: boolean;
    external?: boolean;
    private_profile?: boolean;
    projects_limit?: number;
    bio?: string;
    location?: string;
    public_email?: string;
    skype?: string;
    linkedin?: string;
    twitter?: string;
    discord?: string;
    website_url?: string;
    organization?: string;
    note?: string;
    pronouns?: string;
  }) {
    try {
      const response = await this.axiosInstance.post('/users', options);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to create user');
    }
  }

  /**
   * Update a user
   * 
   * @param userId ID of the user
   * @param options User options to update
   * @returns Updated user details
   */
  async updateUser(userId: number, options: {
    email?: string;
    password?: string;
    name?: string;
    username?: string;
    admin?: boolean;
    can_create_group?: boolean;
    skip_reconfirmation?: boolean;
    external?: boolean;
    private_profile?: boolean;
    projects_limit?: number;
    bio?: string;
    location?: string;
    public_email?: string;
    skype?: string;
    linkedin?: string;
    twitter?: string;
    discord?: string;
    website_url?: string;
    organization?: string;
    note?: string;
    pronouns?: string;
  }) {
    try {
      const response = await this.axiosInstance.put(`/users/${userId}`, options);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to update user: ${userId}`);
    }
  }

  /**
   * Delete a user
   * 
   * @param userId ID of the user
   * @param hardDelete If true, contributions will be deleted instead of moving to Ghost User
   * @returns Response data
   */
  async deleteUser(userId: number, hardDelete?: boolean) {
    try {
      const response = await this.axiosInstance.delete(`/users/${userId}`, {
        params: { hard_delete: hardDelete }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to delete user: ${userId}`);
    }
  }

  /**
   * Get a list of projects and groups that a user is a member of
   * 
   * @param userId ID of the user
   * @param type Filter memberships by type (Project or Namespace)
   * @returns List of user memberships
   */
  async getUserMemberships(userId: number, type?: 'Project' | 'Namespace') {
    try {
      const response = await this.axiosInstance.get(`/users/${userId}/memberships`, {
        params: { type }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get user memberships: ${userId}`);
    }
  }

  /**
   * List groups
   * 
   * @param options Query options
   * @returns List of groups
   */
  async listGroups(options?: {
    skip_groups?: number[];
    all_available?: boolean;
    search?: string;
    order_by?: string;
    sort?: string;
    statistics?: boolean;
    owned?: boolean;
    min_access_level?: number;
    top_level_only?: boolean;
    page?: number;
    per_page?: number;
  }) {
    try {
      const response = await this.axiosInstance.get('/groups', { params: options });
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to list groups');
    }
  }

  /**
   * Get a specific group
   * 
   * @param groupId ID or URL-encoded path of the group
   * @returns Group details
   */
  async getGroup(groupId: string | number) {
    try {
      const response = await this.axiosInstance.get(`/groups/${encodeURIComponent(String(groupId))}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get group: ${groupId}`);
    }
  }

  /**
   * Create a new group
   * 
   * @param options Group options
   * @returns Created group details
   */
  async createGroup(options: {
    name: string;
    path: string;
    description?: string;
    visibility?: string;
    parent_id?: number;
    lfs_enabled?: boolean;
    request_access_enabled?: boolean;
    project_creation_level?: string;
    auto_devops_enabled?: boolean;
    subgroup_creation_level?: string;
  }) {
    try {
      const response = await this.axiosInstance.post('/groups', options);
      return response.data;
    } catch (error) {
      throw this.handleError(error, 'Failed to create group');
    }
  }

  /**
   * Update a group
   * 
   * @param groupId ID or URL-encoded path of the group
   * @param options Group options to update
   * @returns Updated group details
   */
  async updateGroup(groupId: string | number, options: {
    name?: string;
    path?: string;
    description?: string;
    visibility?: string;
    lfs_enabled?: boolean;
    request_access_enabled?: boolean;
    project_creation_level?: string;
    auto_devops_enabled?: boolean;
    subgroup_creation_level?: string;
  }) {
    try {
      const response = await this.axiosInstance.put(`/groups/${encodeURIComponent(String(groupId))}`, options);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to update group: ${groupId}`);
    }
  }

  /**
   * Delete a group
   * 
   * @param groupId ID or URL-encoded path of the group
   * @returns Response data
   */
  async deleteGroup(groupId: string | number) {
    try {
      const response = await this.axiosInstance.delete(`/groups/${encodeURIComponent(String(groupId))}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to delete group: ${groupId}`);
    }
  }

  /**
   * List group members
   * 
   * @param groupId ID or URL-encoded path of the group
   * @returns List of group members
   */
  async listGroupMembers(groupId: string | number) {
    try {
      const response = await this.axiosInstance.get(`/groups/${encodeURIComponent(String(groupId))}/members`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to list group members: ${groupId}`);
    }
  }

  /**
   * Get a specific group member
   * 
   * @param groupId ID or URL-encoded path of the group
   * @param userId ID of the user
   * @returns Group member details
   */
  async getGroupMember(groupId: string | number, userId: number) {
    try {
      const response = await this.axiosInstance.get(
        `/groups/${encodeURIComponent(String(groupId))}/members/${userId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get group member: ${groupId}/${userId}`);
    }
  }

  /**
   * Add a member to a group
   * 
   * @param groupId ID or URL-encoded path of the group
   * @param userId ID of the user
   * @param accessLevel Access level for the user (10=Guest, 20=Reporter, 30=Developer, 40=Maintainer, 50=Owner)
   * @param expiresAt Expiration date for the membership
   * @returns Added group member details
   */
  async addGroupMember(groupId: string | number, userId: number, accessLevel: number, expiresAt?: string) {
    try {
      const response = await this.axiosInstance.post(
        `/groups/${encodeURIComponent(String(groupId))}/members`,
        {
          user_id: userId,
          access_level: accessLevel,
          expires_at: expiresAt
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to add group member: ${groupId}/${userId}`);
    }
  }

  /**
   * Update a group member
   * 
   * @param groupId ID or URL-encoded path of the group
   * @param userId ID of the user
   * @param accessLevel Access level for the user
   * @param expiresAt Expiration date for the membership
   * @returns Updated group member details
   */
  async updateGroupMember(groupId: string | number, userId: number, accessLevel: number, expiresAt?: string) {
    try {
      const response = await this.axiosInstance.put(
        `/groups/${encodeURIComponent(String(groupId))}/members/${userId}`,
        {
          access_level: accessLevel,
          expires_at: expiresAt
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to update group member: ${groupId}/${userId}`);
    }
  }

  /**
   * Remove a member from a group
   * 
   * @param groupId ID or URL-encoded path of the group
   * @param userId ID of the user
   * @returns Response data
   */
  async removeGroupMember(groupId: string | number, userId: number) {
    try {
      const response = await this.axiosInstance.delete(
        `/groups/${encodeURIComponent(String(groupId))}/members/${userId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to remove group member: ${groupId}/${userId}`);
    }
  }

  /**
   * List project members
   * 
   * @param projectId ID or URL-encoded path of the project
   * @returns List of project members
   */
  async listProjectMembers(projectId: string | number) {
    try {
      const response = await this.axiosInstance.get(
        `/projects/${encodeURIComponent(String(projectId))}/members`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to list project members: ${projectId}`);
    }
  }

  /**
   * Get a specific project member
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param userId ID of the user
   * @returns Project member details
   */
  async getProjectMember(projectId: string | number, userId: number) {
    try {
      const response = await this.axiosInstance.get(
        `/projects/${encodeURIComponent(String(projectId))}/members/${userId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to get project member: ${projectId}/${userId}`);
    }
  }

  /**
   * Add a member to a project
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param userId ID of the user
   * @param accessLevel Access level for the user (10=Guest, 20=Reporter, 30=Developer, 40=Maintainer, 50=Owner)
   * @param expiresAt Expiration date for the membership
   * @returns Added project member details
   */
  async addProjectMember(projectId: string | number, userId: number, accessLevel: number, expiresAt?: string) {
    try {
      const response = await this.axiosInstance.post(
        `/projects/${encodeURIComponent(String(projectId))}/members`,
        {
          user_id: userId,
          access_level: accessLevel,
          expires_at: expiresAt
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to add project member: ${projectId}/${userId}`);
    }
  }

  /**
   * Update a project member
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param userId ID of the user
   * @param accessLevel Access level for the user
   * @param expiresAt Expiration date for the membership
   * @returns Updated project member details
   */
  async updateProjectMember(projectId: string | number, userId: number, accessLevel: number, expiresAt?: string) {
    try {
      const response = await this.axiosInstance.put(
        `/projects/${encodeURIComponent(String(projectId))}/members/${userId}`,
        {
          access_level: accessLevel,
          expires_at: expiresAt
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to update project member: ${projectId}/${userId}`);
    }
  }

  /**
   * Remove a member from a project
   * 
   * @param projectId ID or URL-encoded path of the project
   * @param userId ID of the user
   * @returns Response data
   */
  async removeProjectMember(projectId: string | number, userId: number) {
    try {
      const response = await this.axiosInstance.delete(
        `/projects/${encodeURIComponent(String(projectId))}/members/${userId}`
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, `Failed to remove project member: ${projectId}/${userId}`);
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
