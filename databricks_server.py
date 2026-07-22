"""
Databricks MCP Server

This is a Model Context Protocol (MCP) server that provides tools for interacting
with Databricks services. It exposes three main capabilities:
1. Unity Catalog Functions - Query and execute UDFs in Unity Catalog
2. Vector Search - Perform similarity searches on vector indexes
3. Genie Agents - Interact with Databricks Genie for natural language data querying

This server is designed for beginners with comprehensive comments and docstrings
to help understand how MCP servers work and how to integrate with Databricks.

Author: Your Name
Version: 1.0.0
"""

from typing import Any, Optional, List, Dict
import os
import json
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Import Databricks SDK components
# These are the official Python libraries for interacting with Databricks
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.catalog import FunctionInfo
from databricks.vector_search.client import VectorSearchClient

# =============================================================================
# SECTION 1: LOAD ENVIRONMENT VARIABLES
# =============================================================================

# Load environment variables from .env file
# This reads the .env file in the project directory and makes the variables available
# to the Python process via os.getenv()
load_dotenv()

# =============================================================================
# SECTION 2: MCP SERVER INITIALIZATION
# =============================================================================

# Initialize the FastMCP server
# FastMCP is a simplified way to create MCP servers without dealing with low-level protocol details
# The name "databricks" will be displayed to clients connecting to this server
mcp = FastMCP("databricks")

# =============================================================================
# SECTION 2: DATABRICKS CLIENT INITIALIZATION
# =============================================================================

def get_databricks_client() -> WorkspaceClient:
    """
    Initialize and return a Databricks WorkspaceClient.
    
    This function creates a connection to Databricks using environment variables.
    The Databricks SDK automatically reads these environment variables:
    - DATABRICKS_HOST: The workspace URL (e.g., https://your-workspace.cloud.databricks.com)
    - DATABRICKS_TOKEN: A personal access token for authentication
    
    Returns:
        WorkspaceClient: A configured Databricks workspace client
        
    Raises:
        ValueError: If required environment variables are not set
        
    Example:
        >>> client = get_databricks_client()
        >>> print(client.config.host)
        'https://your-workspace.cloud.databricks.com'
    """
    # Get the workspace URL from environment variable
    host = os.getenv("DATABRICKS_HOST")
    if not host:
        raise ValueError(
            "DATABRICKS_HOST environment variable is not set. "
            "Please set it to your Databricks workspace URL."
        )
    
    # Get the personal access token from environment variable
    token = os.getenv("DATABRICKS_TOKEN")
    if not token:
        raise ValueError(
            "DATABRICKS_TOKEN environment variable is not set. "
            "Please create a personal access token in Databricks and set it as an environment variable."
        )
    
    # Create and return the WorkspaceClient with explicit token authentication
    # We explicitly set auth_type to 'pat' to ensure it uses personal access token
    # instead of trying OAuth registration
    client = WorkspaceClient(
        host=host,
        token=token,
        auth_type='pat'  # Force personal access token authentication
    )
    
    return client



# Global variables to hold client instances
# These will be initialized when the server starts
_db_client: Optional[WorkspaceClient] = None



def initialize_clients():
    """
    Initialize the global Databricks clients.
    
    This function is called when the server starts to set up the connections
    to Databricks. It stores the clients in global variables so they can be
    reused across multiple tool calls without re-authenticating each time.
    
    Raises:
        ValueError: If client initialization fails
    """
    global _db_client
    
    try:
        _db_client = get_databricks_client()
   
        print("Successfully initialized Databricks clients")
    except Exception as e:
        print(f"Failed to initialize Databricks clients: {e}")
        raise


# =============================================================================
# SECTION 3: UNITY CATALOG FUNCTIONS TOOLS
# =============================================================================

@mcp.tool()
async def list_uc_functions(
    catalog_name: str,
    schema_name: str,
    max_results: int = 50
) -> str:
    """
    List all User-Defined Functions (UDFs) in a specific catalog and schema.
    
    Unity Catalog Functions are reusable SQL functions that you can define
    and call in your SQL queries. They reside in Unity Catalog at the same
    level as tables, with the structure: catalog.schema.function_name
    
    Args:
        catalog_name: The name of the catalog (e.g., "main", "production")
        schema_name: The name of the schema (e.g., "default", "analytics")
        max_results: Maximum number of functions to return (default: 50)
        
    Returns:
        str: A formatted string listing all functions with their details
        
    Example:
        >>> result = await list_uc_functions("main", "default")
        >>> print(result)
        Functions in main.default:
        1. calculate_revenue - Calculates total revenue
           Parameters: (amount DECIMAL, tax_rate DECIMAL) RETURNS DECIMAL
           Owner: admin
    """
    # Ensure clients are initialized
    if _db_client is None:
        initialize_clients()
    
    try:
        # Use the WorkspaceClient to list functions
        # The functions API is part of the workspace catalog service
        functions_iterator = _db_client.functions.list(
            catalog_name=catalog_name,
            schema_name=schema_name,
            max_results=max_results
        )
        
        # Convert the iterator to a list for easier processing
        functions = list(functions_iterator)
        
        if not functions:
            return f"No functions found in {catalog_name}.{schema_name}"
        
        # Format the output for better readability
        result = f"Functions in {catalog_name}.{schema_name}:\n"
        result += "=" * 60 + "\n"
        
        for idx, func in enumerate(functions, 1):
            result += f"{idx}. {func.name}\n"
            result += f"   Full Name: {func.full_name}\n"
            result += f"   Comment: {func.comment or 'No description'}\n"
            
            # Format the function signature if available
            if func.input_params:
                params = ", ".join([f"{p.name} {p.type_text}" for p in func.input_params.parameters])
                result += f"   Parameters: ({params})\n"
            
            if func.data_type:
                result += f"   Returns: {func.data_type}\n"
            
            result += f"   Owner: {func.owner}\n"
            result += "-" * 60 + "\n"
        
        return result
        
    except Exception as e:
        return f"Error listing functions: {str(e)}"


@mcp.tool()
async def get_uc_function(
    catalog_name: str,
    schema_name: str,
    function_name: str
) -> str:
    """
    Get detailed information about a specific Unity Catalog function.
    
    This tool retrieves complete metadata about a function including its
    parameters, return type, implementation details, and owner information.
    
    Args:
        catalog_name: The name of the catalog
        schema_name: The name of the schema
        function_name: The name of the function
        
    Returns:
        str: Detailed information about the function
        
    Example:
        >>> result = await get_uc_function("main", "default", "calculate_revenue")
        >>> print(result)
        Function: main.default.calculate_revenue
        Description: Calculates total revenue with tax
        Parameters: amount DECIMAL, tax_rate DECIMAL
        Returns: DECIMAL
    """
    # Ensure clients are initialized
    if _db_client is None:
        initialize_clients()
    
    try:
        # Construct the full function name in three-part notation
        full_name = f"{catalog_name}.{schema_name}.{function_name}"
        
        # Get the function details
        function_info = _db_client.functions.get(name=full_name)
        
        # Format the output
        result = f"Function: {function_info.full_name}\n"
        result += "=" * 60 + "\n"
        result += f"Name: {function_info.name}\n"
        result += f"Catalog: {catalog_name}\n"
        result += f"Schema: {schema_name}\n"
        result += f"Comment: {function_info.comment or 'No description'}\n"
        result += f"Owner: {function_info.owner}\n"
        result += f"Created At: {function_info.created_at}\n"
        result += f"Updated At: {function_info.updated_at}\n"
        
        # Add parameter information
        if function_info.input_params:
            result += "\nParameters:\n"
            for param in function_info.input_params.parameters:
                result += f"  - {param.name}: {param.type_text}"
                if param.comment:
                    result += f" ({param.comment})"
                result += "\n"
        
        # Add return type information
        if function_info.data_type:
            result += f"\nReturns: {function_info.data_type}\n"
        
        # Add external language if applicable (for Python UDFs)
        if function_info.external_language:
            result += f"\nLanguage: {function_info.external_language}\n"
        
        return result
        
    except Exception as e:
        return f"Error getting function details: {str(e)}"


def main():
    """
    Main entry point for the Databricks MCP server.
    
    This function initializes the Databricks clients and starts the MCP server.
    The server will listen for incoming MCP requests and respond with the
    appropriate tool results.
    
    The server runs indefinitely until interrupted.
    """
    print("Starting Databricks MCP Server...")
    
    # Initialize Databricks clients on startup
    try:
        initialize_clients()
    except Exception as e:
        print(f"Failed to initialize Databricks clients: {e}")
        print("Please ensure DATABRICKS_HOST and DATABRICKS_TOKEN are set.")
        return
    
    # Start the MCP server
    # This will listen for incoming connections and handle tool requests
    print("Databricks MCP Server is running and ready to accept requests.")
    mcp.run()


if __name__ == "__main__":
    """
    This block runs when the script is executed directly.
    It calls the main() function to start the server.
    """
    main()
