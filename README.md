# Memory Server (mcp-rag-local)

This MCP server provides a simple API for storing and retrieving text passages based on their semantic meaning, not just keywords. It uses Ollama for generating text embeddings and ChromaDB for vector storage and similarity search. You can "memorize" any text and later retrieve the most relevant stored texts for a given query.

## Example Usage

### Memorize a Text
Call the `memorize_text` tool with your text:

```
memory_server.memorize_text("Singapore is an island country in Southeast Asia.")
```

### Retrieve Similar Texts
Call the `remember_similar_texts` tool with your query:

```
memory_server.remember_similar_texts("What is Singapore?", n_results=3)
```

This will return the most relevant stored texts along with a human-readable description of their relevance.



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
  ]
}
```