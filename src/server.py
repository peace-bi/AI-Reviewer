from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from agent import setup_mcp_client, setup_llm, create_agent, review_merge_request
from code_review import CodeReviewPipeline
from rag_utils import create_or_load_vectorstore
import asyncio
from typing import Optional
import signal
import sys

app = FastAPI(title="AI Code Review API")

# Global resources
client = None
llm = None
agent = None
review_pipeline = None
vectorstore = None
should_exit = False

class ReviewRequest(BaseModel):
    project_id: str
    mr_iid: int

@app.on_event("startup")
async def startup_event():
    """Initialize all resources on server startup"""
    global client, llm, agent, review_pipeline, vectorstore
    
    print("Initializing resources...")
    try:
        client = await setup_mcp_client()
        llm = setup_llm()
        vectorstore = create_or_load_vectorstore(persist_directory="./chroma")
        agent = await create_agent(client, llm, vectorstore)
        review_pipeline = CodeReviewPipeline()
        print("All resources initialized successfully!")
    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        # Cleanup any partially initialized resources
        await cleanup_resources()
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup resources when server shuts down"""
    print("Shutting down server...")
    await cleanup_resources()

async def cleanup_resources():
    """Helper function to cleanup resources"""
    global client, llm, agent, review_pipeline, vectorstore
    
    print("Cleaning up resources...")
    try:
        if client and client.sessions:
            await client.close_all_sessions()
        # Reset all global resources
        client = None
        llm = None
        agent = None
        review_pipeline = None
        vectorstore = None
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")

@app.get("/health")
async def health_check():
    """Check if server and resources are healthy"""
    if not all([client, llm, agent, review_pipeline, vectorstore]):
        raise HTTPException(status_code=503, detail="Server resources not fully initialized")
    return {"status": "healthy", "message": "All resources initialized"}

@app.post("/review")
async def handle_review_request(request: ReviewRequest):
    """Handle merge request review"""
    try:
        review = await review_merge_request(
            mr_iid=request.mr_iid,
            project_id=request.project_id,
            client=client,
            llm=llm,
            agent=agent,
            review_pipeline=review_pipeline,
            vectorstore=vectorstore
        )
        return {"status": "success", "review": review}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def signal_handler(signum, frame):
    """Handle shutdown signals by setting the exit flag"""
    global should_exit
    print(f"\nReceived signal {signum}. Starting graceful shutdown...")
    should_exit = True

class UvicornServer(uvicorn.Server):
    """Custom Uvicorn server with graceful shutdown support"""
    
    def handle_exit(self, sig: int, frame) -> None:
        """Handle exit cleanly by letting the server finish its work"""
        print("Shutting down server...")
        return super().handle_exit(sig, frame)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Configure and run server
    config = uvicorn.Config(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid resource initialization issues
        log_level="info"
    )
    server = UvicornServer(config=config)
    
    # Run server
    server.run() 