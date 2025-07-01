from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def load_codebase(source_dir: str, file_pattern: str = "**/*") -> list:
    """
    Load all code files from the specified directory while ignoring specified paths
    """
    print(f"Loading codebase from {source_dir}")
    documents = []
    
    # Define supported file extensions
    code_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".h", ".cs"]
    
    # Define ignore patterns
    ignore_patterns = [
        "node_modules",
        "dist",
        "build",
        "__pycache__",
        ".git",
        "venv",
        ".env",
        ".venv",
        ".idea",
        ".vscode",
        "coverage",
        "test",
        "tests"
    ]
    
    def should_ignore(path: Path) -> bool:
        """Check if a path should be ignored based on ignore patterns"""
        path_parts = path.parts
        return any(ignore in path_parts for ignore in ignore_patterns)
    
    try:
        # Try using language parser first
        from langchain.document_loaders import GenericLoader
        from langchain.document_loaders.parsers import LanguageParser
        
        loader = GenericLoader.from_filesystem(
            source_dir,
            glob=file_pattern,
            suffixes=code_extensions,
            exclude=["**/node_modules/**", "**/dist/**", "**/build/**", "**/__pycache__/**"],
            parser=LanguageParser(language_hints={"ts": "typescript", "js": "javascript"})
        )
        documents = loader.load()
        print(f"Successfully loaded {len(documents)} documents using language parser")
        
    except Exception as e:
        print(f"Warning: Language parser failed ({str(e)}), falling back to simple text loading")
        # Fallback to simple text splitting
        from langchain_community.document_loaders import TextLoader
        
        # Recursively find all files with supported extensions
        for ext in code_extensions:
            for file_path in Path(source_dir).rglob(f"*{ext}"):
                # Skip if path matches any ignore pattern
                if should_ignore(file_path):
                    print(f"Ignoring {file_path}")
                    continue
                    
                try:
                    loader = TextLoader(str(file_path))
                    documents.extend(loader.load())
                    print(f"Loaded {file_path}")
                except Exception as file_error:
                    print(f"Error loading {file_path}: {str(file_error)}")
                    continue
                    
        print(f"Successfully loaded {len(documents)} documents using text loader")
    
    return documents

def split_documents(documents: list) -> list:
    """
    Split documents into manageable chunks
    """
    print("Splitting documents into chunks")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,      # Max characters per chunk
        chunk_overlap=200,    # Overlap between chunks to maintain context
        length_function=len,
        add_start_index=True  # Add metadata about chunk position
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")
    return chunks

def create_or_load_vectorstore(chunks: list = None, persist_directory: str = None) -> Chroma:
    """
    Create new vector store or load existing one
    """
    # Use environment variable for persist directory if not provided
    if persist_directory is None:
        persist_directory = os.getenv("PERSIST_DIRECTORY", "./chroma")
    
    # Initialize the embedding model
    print("Initializing embedding model")
    embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    # Check if vector store exists
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print(f"Loading existing Chroma DB from {persist_directory}")
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    else:
        print("Creating new Chroma DB")
        os.makedirs(persist_directory, exist_ok=True)
        
        # If no chunks provided, create an empty vectorstore
        if chunks is None or len(chunks) == 0:
            print("No documents provided, creating empty vectorstore")
            vectorstore = Chroma(
                embedding_function=embeddings,
                persist_directory=persist_directory
            )
        else:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=persist_directory
            )
        
        print("Chroma DB created and persisted")
    
    return vectorstore

def index_codebase(source_dir: str = None, persist_directory: str = None):
    """
    Main function to index the codebase
    """
    # Use environment variable for source directory if not provided
    if source_dir is None:
        source_dir = os.getenv("SOURCE_DIR")
        if not source_dir:
            raise ValueError("SOURCE_DIR environment variable is required. Please set it in your .env file or pass it as a parameter.")
    
    # Load and process the codebase
    documents = load_codebase(source_dir)
    chunks = split_documents(documents)
    
    # Create or load vector store
    vectorstore = create_or_load_vectorstore(chunks, persist_directory)
    
    return vectorstore

def get_related_code(vectorstore, query: str, k: int = 3) -> str:
    """
    Retrieve related code snippets from the vectorstore for a given query.
    Returns a formatted string with source and content.
    """
    docs = vectorstore.similarity_search(query, k=k)
    related = []
    for doc in docs:
        source = doc.metadata.get('source', 'Unknown')
        content = doc.page_content
        related.append(f"Source: {source}\n{content}")
    return "\n\n".join(related)

if __name__ == "__main__":
    # Example usage - will use environment variables from .env file
    vectorstore = index_codebase()
    
    # Test queries
    test_queries = [
        "Find me function reloadHomeWhenNotOpenRegularAccount?",
    ]
    
    print("\nTesting retrieval with different queries:")
    for query in test_queries:
        print(f"\nQuery: {query}")
        docs = vectorstore.similarity_search(query, k=2)  # Get top 2 results
        print(f"Found {len(docs)} relevant documents")
        for i, doc in enumerate(docs, 1):
            print(f"\nResult {i}:")
            print(f"Source: {doc.metadata.get('source', 'Unknown')}")
            print(f"Content: {doc.page_content}") 