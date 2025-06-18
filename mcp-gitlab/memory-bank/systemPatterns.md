# System Patterns: GitLab MCP Server

## Architecture Overview
The GitLab MCP Server follows a straightforward architecture pattern:

```
┌────────────────┐      ┌────────────────┐      ┌────────────────┐
│                │      │                │      │                │
│  AI Assistant  │◄────►│  MCP Server    │◄────►│  GitLab API    │
│                │      │                │      │                │
└────────────────┘      └────────────────┘      └────────────────┘
```

The server acts as a bridge between AI assistants and the GitLab API, translating MCP protocol requests into GitLab API calls and formatting the responses appropriately.

## Core Design Patterns

### 1. Server Initialization Pattern
The server is initialized with proper capability configuration:
- Explicit declaration of supported capabilities (`canListTools`, `canCallTools`, etc.)
- Proper configuration of tools and resources capabilities objects
- Configuration using the MCP SDK 1.7.0 patterns

### 2. Request Handler Pattern
The server implements request handlers for different MCP protocol operations:
- `ListToolsRequestSchema`: Lists available GitLab tools
- `CallToolRequestSchema`: Executes GitLab API operations
- `ListResourcesRequestSchema`: Lists available GitLab resources
- `ReadResourceRequestSchema`: Reads GitLab resources

### 3. Adapter Pattern
The server adapts GitLab API responses to MCP protocol responses, translating between different data formats and protocols.

### 4. Configuration Pattern
The server uses environment variables for configuration, allowing flexible deployment across different environments.

### 5. Error Handling Pattern
Comprehensive error handling with meaningful error messages passed back through the MCP protocol.

### 6. Documentation Generation Pattern
The server includes a pattern for automatically generating documentation from source code:
- A script parses TypeScript source files to extract tool definitions
- Documentation is generated in markdown format
- Git hooks ensure documentation stays in sync with code
- Special handling for GitHub-compatible anchor links

### 7. Developer Workflow Pattern
The server implements a pattern for streamlined developer workflows:
- Git hooks automatically update documentation on commit
- npm scripts allow easy hook installation
- Consistent formatting and organization of code and documentation

## Component Structure

### Main Components
1. **Server Initialization**: Setup of MCP server with capabilities configuration
2. **Axios Client**: HTTP client configured for GitLab API communication
3. **Domain Managers**: Specialized classes for different GitLab domains
   - **IntegrationsManager**: Handles project integrations and webhooks
   - **CiCdManager**: Manages CI/CD pipelines, variables, and triggers
   - **UsersGroupsManager**: Handles user and group administration
4. **Resource Handlers**: Handle resource listing and reading
5. **Tool Handlers**: Handle tool listing and execution
6. **Error Handling**: Manage and format errors
7. **Documentation Generation**: Script to generate tool documentation from source code
8. **Git Hooks**: Pre-commit hook to ensure documentation stays in sync

### Data Flow
1. AI assistant sends request through MCP protocol
2. Server validates request parameters
3. Server routes the request to the appropriate domain manager (integrations, CI/CD, or users/groups)
4. Domain manager translates request to GitLab API call
5. Domain manager executes API call using the shared axios instance
6. Domain manager processes response and handles any errors
7. Server formats the response according to MCP protocol
8. Server returns formatted response to AI assistant

## Key Technical Decisions

### MCP SDK 1.7.0 Integration
Using the latest MCP SDK version for improved capabilities and compatibility.

### Proper Capability Configuration
Explicit configuration of server capabilities:
- Tools capability with proper structure
- Resources capability with proper structure
- Clear declaration of supported operations

### TypeScript Implementation
Using TypeScript for type safety and improved developer experience.

### Axios for HTTP
Using axios for HTTP requests to the GitLab API for its robust features and ease of use.

### Environment-Based Configuration
Configuration through environment variables for flexibility and security.

### Stdio Communication
Using stdio for MCP protocol communication for compatibility with various AI assistant platforms.

### Error Handling Strategy
Detailed error handling with appropriate error codes and messages to facilitate troubleshooting.

### Documentation Generation
Automated documentation generation from TypeScript source files:
- Parses tool definitions to extract names, descriptions, and parameters
- Generates markdown documentation organized by category
- Updates documentation through git hooks
- Custom handling for GitHub-compatible anchor links
- Special cases for sections with ampersands and other special characters

### Git Workflow
Git hooks ensure documentation stays in sync with code:
- Pre-commit hook checks for changes to tool definitions
- Documentation is automatically regenerated when needed
- Hooks are versioned in the repository for easy installation
- Only updates documentation when relevant files change

## Integration Points

### MCP Protocol Integration
Implements the Model Context Protocol to communicate with AI assistants.

### GitLab API Integration
Connects to GitLab API v4 for repository and project operations.

### Development Workflow Integration
Integrates with git hooks for automated documentation updates.

### GitHub Markdown Integration
Ensures compatibility with GitHub's markdown rendering and anchor link conventions.

## Future Architecture Considerations
1. Support for webhook callbacks
2. Caching of GitLab API responses
3. Additional authentication methods
4. Expansion to more GitLab API endpoints
5. Automated testing through CI/CD pipelines
