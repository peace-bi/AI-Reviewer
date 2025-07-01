# CVS-AI: AI-Powered Code Review System

An intelligent code review system that leverages AI to analyze merge requests and provide comprehensive code reviews using GitLab integration and advanced language models.

## Features

- 🤖 **AI-Powered Code Review**: Automated analysis of merge requests using advanced language models
- 🔗 **GitLab Integration**: Seamless integration with GitLab API for merge request processing
- 📊 **Vector Search**: Code indexing and semantic search using ChromaDB
- 🚀 **FastAPI Server**: High-performance REST API for code review requests
- 🔍 **RAG Pipeline**: Retrieval-Augmented Generation for context-aware reviews

## Prerequisites

- Python 3.8 or higher
- Git
- GitLab account with API access
- Google API key (for Gemini integration)

## Installation

### 1. Clone the Repository

```bash
git clone https://gitlab.mservice.com.vn/cvs-app-modules/ai/cvs-ai.git
cd cvs-ai
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit the .env file with your configuration
nano .env  # or use your preferred editor
```

#### Required Environment Variables

Update the `.env` file with the following variables:

```env
# Source directory for codebase indexing
SOURCE_DIR=/path/to/your/codebase

# Vector store persistence directory
PERSIST_DIRECTORY=./chroma

# Embedding model name
EMBEDDING_MODEL=all-MiniLM-L6-v2 

# GitLab Configuration
GITLAB_API_TOKEN=your_gitlab_api_token_here
GITLAB_API_URL=https://gitlab.mservice.com.vn

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key_here
```

#### Getting API Keys

**GitLab API Token:**
1. Go to your GitLab profile settings
2. Navigate to "Access Tokens"
3. Create a new token with `api` scope
4. Copy the token to `GITLAB_API_TOKEN`

**Google API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to `GOOGLE_API_KEY`

## Running the Server

### Development Mode

```bash
# Make sure your virtual environment is activated
source venv/bin/activate

# Run the server
python src/server.py
```

The server will start on `http://localhost:8000`

### Production Mode

```bash
# Using uvicorn directly
uvicorn src.server:app --host 0.0.0.0 --port 8000 --workers 1
```

## API Endpoints

### Health Check
```bash
GET /health
```
Check if the server and all resources are properly initialized.

### Code Review
```bash
POST /review
Content-Type: application/json

{
  "project_id": "your_project_id",
  "mr_iid": 123
}
```
Submit a merge request for AI-powered code review.

## Project Structure

```
cvs-ai/
├── src/
│   ├── server.py          # FastAPI server implementation
│   ├── agent.py           # AI agent setup and configuration
│   ├── code_review.py     # Code review pipeline
│   └── rag_utils.py       # Vector store utilities
├── chroma/                # Vector database storage
├── venv/                  # Python virtual environment
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
└── README.md             # This file
```

## Development

### Code Formatting

The project uses `autopep8` for code formatting:

```bash
# Format all Python files
autopep8 --in-place --recursive src/
```

### Adding New Dependencies

```bash
# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure your virtual environment is activated
2. **API Key Issues**: Verify your GitLab and Google API keys are correctly set
3. **Port Already in Use**: Change the port in `server.py` or kill the existing process
4. **ChromaDB Issues**: Delete the `chroma/` directory and restart the server

### Logs

The server provides detailed logging. Check the console output for:
- Resource initialization status
- API request processing
- Error messages and stack traces

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a merge request

## License

This project is proprietary software owned by MService.

## Support

For issues and questions:
- Create an issue in the GitLab repository
- Contact the development team
- Check the troubleshooting section above
