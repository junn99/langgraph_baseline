from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()


def create_retriever() -> Any:
    """
    Creates and returns a document retriever based on FAISS vector store.
    
    This function performs the following steps:
    1. Loads a PDF document(place your PDF file in the data folder)
    2. Splits the document into manageable chunks
    3. Creates embeddings for each chunk
    4. Builds a FAISS vector store from the embeddings
    5. Returns a retriever interface to the vector stroe

    Returns:
        Any: A retriever object that can be used to query the document database
    """

    # Step 1: Load Documents
    loader = PyMuPDFLoader("C:\\cursor\\DealMakers\\langgraph_baseline\\notebook\\server\\data\\Agent_guide.pdf")
    docs = loader.load()

    # Step 2: Split Documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_documents = text_splitter.split_documents(docs)

    # Step 3: Create Embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Step 4: Create Vector Database
    vectorstore = FAISS.from_documents(
        documents=split_documents, 
        embedding=embeddings)

    # Step 5: Create Retriever
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    return retriever


# Initialize FastMCP server with configuration
mcp = FastMCP(
    "Retriever",
    instructions="A Retriever that can retrieve information from the database.",
    host="0.0.0.0",
    port=8005,
)

@mcp.tool()
async def retrieve(query: str) -> str:
    """
    Retrieves information from the document database on the query.

    This function creates a retriever, queries it with the provided input,
    and returns the concatenated content of all retrieved documents.

    Args:
        query (str): The search query to find relevant information.

    Returns:
        str: Concatenated text content from all retrieved documents.
    """
    retriever = create_retriever()

    retrieved_docs = retriever.invoke(query)

    return "\n".join([doc.page_content for doc in retrieved_docs])


if __name__ == "__main__":
    # mcp.run(transport="stdio")
    mcp.run(transport="sse")