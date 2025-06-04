
import requests
import chromadb
import uuid
from mcp.server.fastmcp import FastMCP, Context
import os
from pypdf import PdfReader

OLLAMA_PORT = os.getenv("OLLAMA_PORT", "11434")
CHROMADB_PORT = os.getenv("CHROMADB_PORT", "8321")

mcp = FastMCP(name="Memory server", description="A server for memorizing and retrieving texts based on their meaning.")

def get_embedding(text: str):
    """
    Generate an embedding for the given text using the local Ollama API.
    Args:
        text (str): The input text to embed.
    Returns:
        list: The embedding vector as a list of floats, or None if failed.
    """
    url = f"http://localhost:{OLLAMA_PORT}/api/embeddings"
    payload = {"model": "all-minilm:l6-v2", "prompt": text}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("embedding")
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return None

@mcp.tool()
async def memorize_pdf_file(ctx: Context, file_path: str, page: int = 0, metadata: dict = {"topic": "memory"}) -> str:
    """Chunk the contents of a PDF file into meaningful segments and store them in memory for later retrieval based on relevance 
    in meaning, not just keywords.

    Args:
        ctx (Context): The context of the request.
        file_path (str): The path to the PDF file.
        page (int, optional): The starting page number to read from the PDF file. Defaults to 0.
        metadata (dict, optional): Metadata to associate with the memorized content.

    Returns:
        str: A message indicating success or failure of the operation.
    """

    await ctx.info(f"Processing PDF file: {file_path}")
    await ctx.report_progress(0, 100, "Starting PDF processing...")
    if not os.path.exists(file_path):
        return "File not found. Inform the user to provide the full path to the PDF file."
    if not os.path.isfile(file_path):
        return "Provided path is not a file. Inform the user to provide the full path to the PDF file."
    if not file_path.lower().endswith('.pdf'):
        return "File is not a PDF. Inform the user to provide the full path to a PDF file."
    await ctx.report_progress(30, 100, "File validation complete.")
    try:
        reader = PdfReader(file_path)
        if page < 0 or page >= len(reader.pages):
            return "Invalid page number. Please provide a valid page number."
        text_content_20_pages = ""
        for i in range(page, min(page + 20, len(reader.pages))):
            text_content_20_pages += reader.pages[i].extract_text()
        await ctx.report_progress(100, 100, "PDF file read successfully.")
    except Exception as e:
        await ctx.error(f"Error reading PDF file: {e}")
        return "Failed to read PDF file. Please ensure it is a valid PDF file and the arguments are correct and using the correct types."
    message = (
        f"Chunk the following text between START_TEXT and END_TEXT meaningfully and memorize the chunks using memorize_multiple_texts:\n\n"
        f"START_TEXT\n{text_content_20_pages}\nEND_TEXT\n\n"
        "Ensure all chunks are memorized. To be clear, memorize_pdf_file does not invoke memorize_multiple_texts directly,"
        "but rather prepares the text for it, so you need to call memorize_multiple_texts with the prepared chunks.\n\n"
    )
    if page + 20 < len(reader.pages):
        message += (
            f"\nAfter memorizing, call memorize_pdf_file with {file_path} and page {page + 20} to continue."
        )
    return message

@mcp.tool()
def greet_user():
    """Greet the user with their name and the server's name.

    Returns:
        str: A greeting message.
    """
    return f"Hello! I am {mcp.name}."

@mcp.tool()
def memorize_multiple_texts(texts: list, metadata: dict = {"topic": "memory"}) -> str:
    """Memorize multiple texts for later retrieval based on relevance in meaning, not just keywords.
    
    Args:
        texts (list): A list of texts to memorize.
    Returns:
        str: A message indicating success or failure of the operation.
    """
    collection_name = "texts_collection"
    client = chromadb.HttpClient(host="localhost", port=CHROMADB_PORT)
    collection = client.get_or_create_collection(collection_name)
    embeddings = []
    
    for text in texts:
        embedding = get_embedding(text)
        if embedding is None:
            return "One or more texts were not stored due to an error with embedding."
        embeddings.append(embedding)
    
    try:
        doc_ids = [str(uuid.uuid4()) for _ in texts]
        collection.add(
            ids=doc_ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=[metadata] * len(texts)
        )
        return """Texts stored successfully. Please ensure all the chunks prepared have been memorized,
        if not please call memorize_multiple_texts with the prepared chunks that have not been memorized."""
    except Exception as e:
        return f"One or more texts were not stored due to an error: {e}"

@mcp.tool()
def memorize_text(text: str, metadata: dict = {"topic": "memory"}) -> str:
    """Memorize a text for later retrieval based on relevance in meaning, not just keywords. 
    
    Args:
        text (str): The text to memorize.
    Returns:
        str: A message indicating success or failure of the operation.
    """
    collection_name = "texts_collection"
    client = chromadb.HttpClient(host="localhost", port=CHROMADB_PORT)
    collection = client.get_or_create_collection(collection_name)
    embedding = get_embedding(text)
    if embedding is None:
        return "Text was not stored due to an error with embedding."
    try:
        doc_id = str(uuid.uuid4())
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
        return "Text stored successfully."
    except Exception as e:
        return f"Text was not stored due to an error: {e}"

# Function to query ChromaDB for N closest texts to a query
@mcp.tool()
def remember_similar_texts(query_text: str, n_results: int = 5) -> str:
    """Query memory for texts similar in meaning to the query text.

    Args:
        query_text (str): The text to find similar meanings for.
        n_results (int): The number of results to return.
    Returns:
        str: A human-readable string with the results and their relevance.
    """
    collection_name = "texts_collection"
    client = chromadb.HttpClient(host="localhost", port=CHROMADB_PORT)
    collection = client.get_or_create_collection(collection_name)
    embedding = get_embedding(query_text)
    if embedding is None:
        return "Could not process the query due to an error."
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["distances", "documents"]
    )
    texts = results.get("documents", [[]])[0]
    distances = results.get("distances", [[]])[0]
    if not texts:
        return "No similar texts found."
    # Build a human-readable result string
    output_lines = []
    for i, (text, distance) in enumerate(zip(texts, distances), 1):
        if distance < 20:
            relevance = "Highly relevant"
        elif distance < 30:
            relevance = "Somewhat relevant"
        elif distance < 60:
            relevance = "Slightly relevant"
        else:
            relevance = "Not very relevant"
        output_lines.append(f"Result {i}: {text}\nRelevance: {relevance}\nDistance: {distance:.4f}\n")
    return "\n".join(output_lines)

if __name__ == "__main__":
    mcp.run()
