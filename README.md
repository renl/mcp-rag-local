# Memory Server (mcp-rag-local)

This MCP server provides a simple API for storing and retrieving text passages based on their semantic meaning, not just keywords. It uses Ollama for generating text embeddings and ChromaDB for vector storage and similarity search. You can "memorize" any text and later retrieve the most relevant stored texts for a given query.

## Example Usage


### Memorize a Text
You can simply ask the LLM to memorize a text for you in natural language:

**User:**
Memorize this text: "Singapore is an island country in Southeast Asia."

**LLM:**
Text memorized successfully.


### Memorize Multiple Texts
You can also ask the LLM to memorize several texts at once:

**User:**
Memorize these texts:
- Singapore is an island country in Southeast Asia.
- It is about one degree of latitude north of the equator.
- It is a major financial and shipping hub.

**LLM:**
All texts memorized successfully.

This will store all provided texts for later semantic retrieval.

### Memorize a PDF File

You can also ask the LLM to memorize the contents of a PDF file via `memorize_pdf_file`. The MCP tool will read up to 20 pages at a time from the PDF, return the extracted text, and have the LLM chunk it into meaningful segments. The LLM then uses the `memorize_multiple_texts` tool to store these chunks.

This process is repeated: the MCP tool continues to read the next 20 pages, the LLM chunks and memorizes them, and so on, until the entire PDF is processed and memorized.

**User:**
Memorize this PDF file: `C:\path\to\document.pdf`

**LLM:**
Reads the first 20 pages, chunks the text, stores the chunks, and continues with the next 20 pages until the whole document is memorized.

You can also specify a starting page if you want to begin from a specific page:

**MCP to LLM:**
Memorize this PDF file starting from page 40: `C:\path\to\document.pdf`

**LLM:**
Reads pages 40–59, chunks and stores the text, then continues with the next set of pages until the end of the document.

### Example: Conversational Chunking and Memorizing Large Text

If you have a long text, you can ask the LLM to help you split it into short, meaningful chunks and store them. For example:

**User:**
Please chunk the following long text and memorize all the chunks.

`{large body of text}`

**LLM:**
Splits the text into short, relevant segments and calls `memorize_multiple_texts` to store them. If the text is too long to store in one go, the LLM will continue chunking and storing until the entire text is memorized.

**User:**
Are all the text chunks stored?

**LLM:**
Checks and, if not all are stored, continues until the process is complete.

This conversational approach ensures that even very large texts are fully chunked and memorized, with the LLM handling the process interactively.

### Retrieve Similar Texts
To recall information, just ask the LLM a question:

**User:**
What is Singapore?

**LLM:**
Returns the most relevant stored texts along with a human-readable description of their relevance.

# Setup Instructions

## 0. Clone this repository
First, clone this git repository and change into the cloned directory:

```
git clone <repository-url>
cd mcp-rag-local
```

## 1. Install uv
Install [uv](https://github.com/astral-sh/uv) (a fast Python package manager):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 1a. Windows Installation

If you are on Windows, install [uv](https://github.com/astral-sh/uv) using PowerShell:

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 2. Start the services
Run the following command to start ChromaDB and Ollama using Docker Compose:

```
docker-compose up
```

## 3. Pull the embedding model
After the containers are running, pull the embedding model for Ollama:

```
docker exec -it ollama ollama pull all-minilm:l6-v2
```

## 4. MCP Server Config
Add the following to your MCP server configuration:

```json
"mcp-rag-local": {
  "command": "uv",
  "args": [
    "--directory",
    "path\\to\\mcp-rag-local",
    "run",
    "main.py"
  ],
  "env": {
    "CHROMADB_PORT": "8321",
    "OLLAMA_PORT": "11434"
  }
}
```

## 5. Viewing and Managing Memory (ChromaDB Admin GUI)

A web-based GUI for ChromaDB(Memory Server's db) is included for easy inspection and management of stored memory.

- The admin UI is available at: [http://localhost:8322](http://localhost:8322)
- You can use this interface to browse, search, and manage the vector database contents.
