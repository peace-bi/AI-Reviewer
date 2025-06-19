import json
from mcp_use import MCPClient, MCPAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from rag_utils import create_or_load_vectorstore
from code_review import CodeReviewPipeline, debug_ai_review_and_comments, post_line_comments_direct
import os
import asyncio
from typing import Optional

def setup_rag_tool(vectorstore=None):
    """
    Tạo tool RAG để agent có thể truy vấn codebase
    """
    print("Setting up RAG tool...")
    if vectorstore is None:
        vectorstore = create_or_load_vectorstore(persist_directory="./chroma")
    
    def query_codebase(query: str) -> str:
        """
        Truy vấn codebase để tìm code liên quan
        """
        docs = vectorstore.similarity_search(query, k=3)
        results = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            content = doc.page_content
            results.append(f"Result {i} from {source}:\n{content}\n")
        return "\n".join(results)
    
    return Tool(
        name="query_codebase",
        description="Use this tool to search for relevant code in the codebase. Input should be a natural language query describing what you're looking for.",
        func=query_codebase
    )

async def setup_mcp_client():
    """
    Thiết lập MCP client để kết nối với GitLab server
    """
    # Cấu hình cho MCP server
    config = {
        "mcpServers": {
            "gitlab": {
                "command": "node",
                "args": ["./mcp-gitlab/build/index.js"],
                "env": {
                    "GITLAB_API_TOKEN": os.getenv("GITLAB_API_TOKEN"),
                    "GITLAB_API_URL": os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
                }
            }
        }
    }
    
    print("Initializing MCP client...")
    client = MCPClient.from_dict(config)
    return client

def setup_llm():
    """
    Khởi tạo Language Model (ở đây dùng Gemini, có thể thay bằng OpenAI hoặc Claude)
    """
    print("Initializing LLM...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.5
    )
    return llm

async def create_agent(client, llm, vectorstore=None):
    """
    Tạo agent với client và LLM đã cấu hình
    """
    print("Creating agent...")
    
    # Tạo tool RAG với vectorstore đã có hoặc tạo mới
    rag_tool = setup_rag_tool(vectorstore)
    
    # Khởi tạo agent
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=30,
        verbose=True
    )
    
    # Initialize the agent explicitly
    print("Initializing agent...")
    await agent.initialize()
    
    # Add RAG tool to agent's tools after initialization
    agent._tools.append(rag_tool)
    
    return agent

async def review_merge_request(
    mr_iid: int,
    project_id: str,
    client: Optional[MCPClient] = None,
    llm: Optional[ChatGoogleGenerativeAI] = None,
    agent: Optional[MCPAgent] = None,
    review_pipeline: Optional[CodeReviewPipeline] = None,
    vectorstore = None
):
    """
    Hàm review merge request với khả năng tái sử dụng resources
    """
    try:
        # Sử dụng resources đã có hoặc tạo mới nếu cần
        if client is None:
            client = await setup_mcp_client()
        
        if llm is None:
            llm = setup_llm()
            
        if agent is None:
            agent = await create_agent(client, llm, vectorstore)
            
        if review_pipeline is None:
            review_pipeline = CodeReviewPipeline()

        if vectorstore is None:
            vectorstore = create_or_load_vectorstore(persist_directory="./chroma")
        
        print("\nStarting code review...")
        review, mr_info = await review_pipeline.review_merge_request(agent, mr_iid, project_id, vectorstore)
        print("\nCode Review Result:")
        print(review)

        # Extract and post line comments
        comments = debug_ai_review_and_comments(review)
        diffs = mr_info.get("changes", []) if mr_info else []
        post_line_comments_direct(project_id, mr_iid, comments, diffs=diffs)
        
        return review
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise

async def main():
    """
    Main function for standalone usage (không qua server)
    """
    review = await review_merge_request(
        mr_iid=42197,
        project_id="2419"
    )
    return review

if __name__ == "__main__":
    asyncio.run(main()) 