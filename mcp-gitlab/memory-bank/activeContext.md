# Active Context: GitLab MCP Server

## Current Focus
The current development focus has been on enhancing the documentation and developer workflow for the GitLab MCP server:

1. **Documentation Improvements**: Added a centralized tools documentation in TOOLS.md generated from the source code to make it easier for developers to understand the available tools
2. **Developer Workflow Enhancements**: Implemented git hooks to automatically keep documentation in sync with code
3. **License Clarification**: Added MIT license file to clarify the project's licensing
4. **Project Attribution**: Updated README.md to acknowledge this is an extension of the Model Context Protocol project

Most recently, we focused on:
1. Creating a script that automatically generates TOOLS.md from the src/utils/tools-data.ts file
2. Setting up a git pre-commit hook to regenerate TOOLS.md whenever tools-data.ts changes
3. Ensuring proper anchor links in the TOOLS.md table of contents using GitHub-compatible formats
4. Adding the MIT license file to formally license the project
5. Updating the README.md to mention the project's origin and link to the tools documentation

## Recent Changes
- Added a script (`scripts/generate-tools-md.js`) to convert tools-data.ts to TOOLS.md in a well-formatted markdown table
- Created a pre-commit git hook that automatically regenerates TOOLS.md when tools-data.ts changes
- Created a versioned copy of the git hook in the repository for other developers
- Updated package.json to add an `install-hooks` script for easier hook installation
- Updated README.md installation instructions to mention the git hooks
- Fixed anchor link generation in TOOLS.md for sections with special characters, particularly:
  - "Integrations & Webhooks" → "#integrations--webhooks"
  - "User & Group Management" → "#user--group-management"
- Added the MIT license file to the project
- Updated README.md to mention that this is an extended version of the MCP GitLab server from the Model Context Protocol project
- Restructured the README.md to use TOOLS.md as the source of truth for tool documentation

## Active Decisions

### Auto-generated Documentation
- Created a script that parses the tools-data.ts TypeScript file and generates a markdown table of all tools
- Used regex patterns to extract tool names, descriptions, parameters, and required flags
- Implemented special handling for anchor links with ampersands
- Created a git hook to ensure documentation stays in sync with code

### Git Hook Implementation
- Created a git pre-commit hook that detects changes to tools-data.ts and automatically regenerates TOOLS.md
- Added the hook to both .git/hooks (local) and git-hooks/ (versioned) directories
- Added an npm script for easy installation of the hooks
- Configured the hook to only run when relevant files change to avoid unnecessary processing

### Documentation Organization
- Moved detailed tool documentation from README.md to TOOLS.md
- Organized tools by category in the documentation:
  - Repository Management
  - Integrations & Webhooks
  - CI/CD Management
  - User & Group Management
- Added proper anchors for each section to make navigation easier
- Updated README.md to link to TOOLS.md instead of containing duplicate information

### Anchor Link Handling
- Identified issues with GitHub's anchor link format for sections with special characters
- Implemented hardcoded special cases for sections with ampersands to ensure correct navigation
- Used single-dash format for ampersands (e.g., "User & Group Management" → "#user--group-management")
- Ensured all table of contents links correctly point to their respective sections

### License and Attribution
- Added the MIT license file to clarify the project's licensing
- Updated README.md to acknowledge that this is an extended version of the MCP GitLab server
- Added a link to the original project repository for attribution

## Next Steps

### Short-term Tasks
1. Complete unit tests for all tools
2. Add support for pagination in list operations
3. Support for wiki management
4. Support for repository commits and tags

### Medium-term Goals
1. Expand tool set to cover more GitLab API endpoints
2. Implement caching for improved performance
3. Add support for webhook callbacks
4. Create helper functions for common operations

### Long-term Vision
1. Support for GitLab GraphQL API
2. Support for advanced authentication methods
3. Implementation of resource streaming for large files
4. Integration with CI/CD pipelines for automated testing and deployment

## Open Questions
1. How to handle GitLab API rate limiting effectively?
2. What's the best approach for handling large repository files?
3. How to structure more complex GitLab operations that require multiple API calls?
4. What additional metadata should be provided to AI assistants for better context?

## Current Challenges
1. Ensuring consistent type safety across all GitLab API interactions
2. Managing GitLab API token security
3. Supporting various GitLab API versions and endpoints
4. Handling large responses efficiently within MCP protocol constraints
