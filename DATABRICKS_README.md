# Databricks MCP Server

A comprehensive Model Context Protocol (MCP) server for interacting with Databricks services, designed for beginners with extensive documentation and comments.

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [Understanding the Code](#understanding-the-code)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This MCP server provides tools to interact with three main Databricks services:

1. **Unity Catalog Functions** - Query and manage User-Defined Functions (UDFs)
2. **Vector Search** - Perform similarity searches on vector embeddings
3. **Genie Agents** - Natural language data querying with AI-powered assistants

The server is built with FastMCP, a simplified framework for creating MCP servers, and includes comprehensive comments to help beginners understand how everything works.

## ✨ Features

### Unity Catalog Functions
- List all functions in a catalog/schema
- Get detailed information about specific functions
- View function parameters, return types, and descriptions

### Vector Search
- List Vector Search endpoints
- List indexes on endpoints
- Perform similarity searches with natural language queries
- Retrieve results with similarity scores

### Genie Agents
- List available Genie Agents
- Query agents with natural language questions
- Support for multi-turn conversations

## 📋 Prerequisites

Before using this server, you need:

1. **Databricks Workspace** - Access to a Databricks workspace with:
   - Unity Catalog enabled
   - SQL Warehouse (Pro or Serverless)
   - Appropriate permissions for the data you want to access

2. **Python 3.13+** - The server requires Python 3.13 or higher

3. **Personal Access Token** - Create a token in Databricks:
   - Go to your workspace settings
   - Navigate to "Personal Access Tokens"
   - Generate a new token with appropriate permissions

4. **uv** - Python package manager (for dependency management)

## 🚀 Installation

### Step 1: Install Dependencies

```bash
# Navigate to the project directory
cd /Users/as-mac-1241/Downloads/MCPwork/mcpMain

# Install dependencies using uv
uv sync
```

This will install:
- `mcp[cli]` - The MCP framework
- `databricks-sdk` - Official Databricks Python SDK
- `databricks-vectorsearch` - Vector Search client library
- `httpx` - HTTP client library

### Step 2: Configure Environment Variables

Copy the example environment file and add your credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your actual values
# You'll need to set:
# - DATABRICKS_HOST: Your workspace URL
# - DATABRICKS_TOKEN: Your personal access token
```

Example `.env` file:
```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef...
```

### Step 3: Configure MCP Client

The server is already configured in `.vscode/mcp.json`. If you're using Windsurf or Claude Desktop, the configuration should work automatically after reload.

For Claude Desktop, also update `~/Library/Application Support/Claude/claude_desktop_config.json` with the same configuration.

### Step 4: Reload Your IDE

- **Windsurf**: Press `Cmd+Shift+P`, type "Reload Window", press Enter
- **Claude Desktop**: Restart the application

## 🔧 Available Tools

### Unity Catalog Functions

#### `list_uc_functions`
List all User-Defined Functions in a catalog and schema.

**Parameters:**
- `catalog_name` (required): The catalog name
- `schema_name` (required): The schema name
- `max_results` (optional): Maximum results to return (default: 50)

**Example:**
```
List all functions in catalog "main" and schema "default"
```

#### `get_uc_function`
Get detailed information about a specific function.

**Parameters:**
- `catalog_name` (required): The catalog name
- `schema_name` (required): The schema name
- `function_name` (required): The function name

**Example:**
```
Get details for function "calculate_revenue" in main.default
```

### Vector Search

#### `list_vector_search_endpoints`
List all Vector Search endpoints in the workspace.

**Parameters:** None

**Example:**
```
List all Vector Search endpoints
```

#### `list_vector_search_indexes`
List all indexes on a specific endpoint.

**Parameters:**
- `endpoint_name` (required): The endpoint name

**Example:**
```
List indexes on endpoint "my-vector-endpoint"
```

#### `similarity_search`
Perform a similarity search on a Vector Search index.

**Parameters:**
- `endpoint_name` (required): The endpoint name
- `index_name` (required): The full index name (catalog.schema.index)
- `query_text` (required): Natural language query
- `num_results` (optional): Number of results (default: 5)
- `columns` (optional): Columns to return in results

**Example:**
```
Search for "machine learning tutorials" in index main.default.documents
```

### Genie Agents

#### `list_genie_agents`
List all available Genie Agents in the workspace.

**Parameters:** None

**Example:**
```
List all Genie Agents
```

#### `query_genie_agent`
Ask a question to a Genie Agent.

**Parameters:**
- `agent_id` (required): The Genie Agent ID
- `question` (required): Natural language question
- `conversation_id` (optional): For follow-up questions

**Example:**
```
Ask agent "abc123..." about "What were total sales last quarter?"
```

## 💡 Usage Examples

### Example 1: Listing Unity Catalog Functions

In your IDE's chat panel:

```
List all functions in the main catalog and default schema
```

The server will call `list_uc_functions("main", "default")` and return a formatted list of all functions with their details.

### Example 2: Performing Vector Search

```
Search for documents about "customer churn prediction" in the analytics vector index
```

This will:
1. Connect to the Vector Search endpoint
2. Query the specified index with your search text
3. Return the most similar documents with similarity scores

### Example 3: Querying a Genie Agent

```
Ask the Sales Analytics agent: "What were our top-selling products last month?"
```

The Genie Agent will:
1. Understand the natural language question
2. Generate appropriate SQL queries
3. Execute the queries against your data
4. Return a human-readable answer

## 📖 Understanding the Code

### Project Structure

```
mcpMain/
├── server/
│   ├── databricks/
│   │   └── databricks_server.py    # Main server implementation
│   └── weather.py                   # Weather server (separate)
├── .vscode/
│   └── mcp.json                     # MCP configuration
├── pyproject.toml                   # Python dependencies
├── .env.example                     # Environment variables template
└── DATABRICKS_README.md            # This file
```

### Code Organization

The server is organized into logical sections:

1. **Server Initialization** - Sets up the FastMCP server
2. **Client Initialization** - Creates Databricks connections
3. **Unity Catalog Tools** - Functions for UDF management
4. **Vector Search Tools** - Functions for similarity search
5. **Genie Agents Tools** - Functions for natural language querying
6. **Main Entry Point** - Server startup logic

### Key Concepts

#### MCP Tools
Tools are functions decorated with `@mcp.tool()`. These are the functions that clients can call. Each tool:
- Has a descriptive name
- Takes parameters with type hints
- Returns a string (formatted for readability)
- Includes comprehensive docstrings

#### Async Functions
Most tools are `async` functions because they perform I/O operations (network requests to Databricks). This allows the server to handle multiple requests efficiently.

#### Error Handling
Each tool includes try-except blocks to catch and report errors gracefully. If something goes wrong, the tool returns an error message instead of crashing.

#### Client Reuse
Databricks clients are initialized once and stored in global variables. This avoids re-authenticating for every request, improving performance.

## 🔍 Troubleshooting

### Common Issues

#### "DATABRICKS_HOST environment variable is not set"
**Solution:** Make sure you've created a `.env` file with your credentials and that the environment variables are properly set in your MCP configuration.

#### "Failed to initialize Databricks clients"
**Solution:** 
- Verify your DATABRICKS_HOST URL is correct
- Check that your personal access token is valid and not expired
- Ensure the token has the necessary permissions

#### "No Vector Search endpoints found"
**Solution:** You need to create a Vector Search endpoint in your Databricks workspace before using Vector Search tools.

#### "Genie Agents API not available"
**Solution:** The Genie Agents API may require additional setup or specific workspace entitlements. Check your Databricks workspace configuration.

### Debug Mode

To see detailed error messages, you can run the server directly in a terminal:

```bash
# Set environment variables
export DATABRICKS_HOST="your-workspace-url"
export DATABRICKS_TOKEN="your-token"

# Run the server
uv run --with mcp mcp run server/databricks/databricks_server.py
```

This will show initialization errors and connection issues in real-time.

## 📚 Additional Resources

- [Databricks SDK for Python](https://databricks-sdk-py.readthedocs.io/)
- [Vector Search Documentation](https://docs.databricks.com/en/machine-learning/vector-search.html)
- [Genie Agents Documentation](https://docs.databricks.com/en/genie/index.html)
- [Unity Catalog Documentation](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

## 🤝 Contributing

This server is designed as a learning resource. Feel free to:
- Add more tools for other Databricks services
- Improve error handling
- Add more comprehensive examples
- Enhance documentation

## 📄 License

This project is provided as-is for educational purposes.
