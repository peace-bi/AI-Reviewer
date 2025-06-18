# Technical Context: GitLab MCP Server

## Technologies Used

### Core Technologies
- **Node.js**: Runtime environment (v16 or higher required)
- **TypeScript**: Programming language for type safety and better developer experience
- **Model Context Protocol (MCP)**: Protocol for communication with AI assistants
- **GitLab API v4**: RESTful API for GitLab operations

### Dependencies
- **@modelcontextprotocol/sdk (v1.7.0)**: MCP SDK for server implementation
- **axios**: HTTP client for GitLab API communication
- **TypeScript**: For type definitions and compilation

### Development Dependencies
- **@types/node**: TypeScript definitions for Node.js
- **typescript**: TypeScript compiler

## Development Setup

### Prerequisites
- Node.js (v16 or higher)
- npm
- A GitLab account with API token

### Installation Steps
1. Clone the repository
2. Run `npm install` to install dependencies
3. Run `npm run build` to compile TypeScript to JavaScript
4. Configure GitLab API token in environment variables

### Environment Configuration
Required environment variables:
- `GITLAB_API_TOKEN`: Personal access token from GitLab
- `GITLAB_API_URL` (optional): URL for GitLab API, defaults to 'https://gitlab.com/api/v4'

### Build Process
The build process uses TypeScript compiler (tsc) to generate JavaScript files in the `build` directory. After compilation, the main executable file is made executable with chmod.

## Technical Constraints

### GitLab API Limitations
- Rate limiting according to GitLab's policies
- API token permissions define available operations
- Some operations require specific user permissions in GitLab
- Integration modification may require OAuth tokens that can't be obtained through the API alone
- Webhook test operations have stricter rate limiting (5 requests per minute)

### MCP Protocol Constraints
- Limited to operations defined in MCP protocol
- Communication through stdio only
- Limited support for streaming or large data transfers
- Server must properly configure capabilities for tools and resources

### Security Considerations
- API tokens must be kept secure
- Sensitive repository data should be handled carefully
- No persistent storage of credentials

## Integration Points

### GitLab API Integration
- Uses GitLab API v4
- Authenticates with personal access token
- Supports both GitLab.com and self-hosted instances

### AI Assistant Integration
- Uses MCP protocol for communication
- Integrates with MCP-compatible AI assistants
- Provides tools and resources for GitLab operations

## Deployment

### Local Deployment
Configure in MCP settings file for local AI assistant applications:

#### For Cursor/Roo Cline
```json
{
  "mcpServers": {
    "gitlab": {
      "command": "node",
      "args": [
        "/path/to/mcp-gitlab/build/index.js"
      ],
      "env": {
        "GITLAB_API_TOKEN": "YOUR_GITLAB_API_TOKEN",
        "GITLAB_API_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

#### For Claude Desktop
```json
{
  "mcpServers": {
    "gitlab": {
      "command": "node",
      "args": [
        "/path/to/mcp-gitlab/build/index.js"
      ],
      "env": {
        "GITLAB_API_TOKEN": "YOUR_GITLAB_API_TOKEN",
        "GITLAB_API_URL": "https://gitlab.com/api/v4"
      }
    }
  }
}
```

### Production Deployment
- Can be deployed as a service on a server
- Configure with appropriate environment variables
- Ensure security of API tokens in production environments
