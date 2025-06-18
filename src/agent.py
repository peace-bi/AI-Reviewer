import json
from mcp_use import MCPClient, MCPAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import Tool
from rag_utils import create_or_load_vectorstore
from code_review import CodeReviewPipeline, debug_ai_review_and_comments, post_line_comments_with_mcp
import os
import asyncio

def setup_rag_tool():
    """
    Tạo tool RAG để agent có thể truy vấn codebase
    """
    print("Setting up RAG tool...")
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
        temperature=0
    )
    return llm

async def create_agent(client, llm):
    """
    Tạo agent với client và LLM đã cấu hình
    """
    print("Creating agent...")
    
    # Tạo tool RAG
    rag_tool = setup_rag_tool()
    
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

async def main():
    try:
        # Thiết lập MCP client
        client = await setup_mcp_client()
        
        # Khởi tạo LLM và agent
        llm = setup_llm()
        agent = await create_agent(client, llm)
        
        # Khởi tạo pipeline review code
        review_pipeline = CodeReviewPipeline()

        # Load vectorstore ONCE for related code retrieval
        vectorstore = create_or_load_vectorstore(persist_directory="./chroma")
        
        # Get MR info (now only one call)
        mr_iid = 42197
        project_id = "2419"
    
        print("\nStarting code review...")
        review = await review_pipeline.review_merge_request(agent, mr_iid, project_id, vectorstore)
        print("\nCode Review Result:")
        print(review)

        # Extract and post line comments
        comments = debug_ai_review_and_comments(review)
        await post_line_comments_with_mcp(agent, project_id, mr_iid, comments)
    
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        # Clean up resources
        if 'client' in locals() and client.sessions:
            await client.close_all_sessions()

if __name__ == "__main__":
    asyncio.run(main()) 