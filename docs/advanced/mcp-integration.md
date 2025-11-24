# MCP Integration

Learn how to integrate Model Context Protocol (MCP) servers with DSPy Code for extended capabilities.

## What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol that allows AI applications to:

- Access external tools and APIs
- Read from various data sources
- Execute commands and scripts
- Integrate with third-party services

**In DSPy Code**, MCP enables your DSPy programs to:

- Query databases
- Search the web
- Read files and documents
- Call external APIs
- Execute system commands

## MCP Architecture

```
DSPy Code
    ↓
MCP Client
    ↓
MCP Server (stdio/SSE)
    ↓
Tools / Resources / Prompts
```

### Components

**1. MCP Server:**

- Provides tools, resources, and prompts
- Can be local (stdio) or remote (SSE)
- Implements MCP protocol

**2. MCP Client:**

- Connects to MCP servers
- Manages sessions
- Routes requests

**3. Tools:**

- Functions that can be called
- Take parameters, return results
- Examples: search, calculate, query

**4. Resources:**

- Data sources that can be read
- Files, databases, APIs
- Examples: documents, configs

**5. Prompts:**

- Pre-defined prompt templates
- Can include dynamic data
- Examples: analysis templates

## Quick Start

### Step 1: Add an MCP Server

Add a server configuration:

```
/mcp-add my-server --transport stdio --command "python server.py"
```

**Parameters:**

- `name`: Server identifier
- `--transport`: `stdio` or `sse`
- `--command`: Command to start server (for stdio)
- `--url`: Server URL (for SSE)

### Step 2: Connect to Server

```
/mcp-connect my-server
```

DSPy Code establishes connection and discovers available tools.

### Step 3: List Available Tools

```
/mcp-tools my-server
```

**Example output:**

```
Available tools from my-server:

1. search_web
   Description: Search the web for information
   Parameters:
     - query (string): Search query
     - max_results (integer): Maximum results (default: 10)

2. read_file
   Description: Read contents of a file
   Parameters:
     - path (string): File path

3. execute_python
   Description: Execute Python code
   Parameters:
     - code (string): Python code to execute
```

### Step 4: Use Tools in DSPy Programs

Generate code that uses MCP tools:

```
Create a module that searches the web and summarizes results
```

DSPy Code generates code with MCP integration!

## MCP Server Types

### 1. stdio Transport

**Local servers** that communicate via standard input/output.

**Add stdio server:**

```
/mcp-add local-tools --transport stdio --command "python tools_server.py"
```

**Configuration in `dspy_config.yaml`:**

```yaml
mcp_servers:
  local-tools:
    transport: stdio
    command: python tools_server.py
    args: []
    env: {}
```

**Example server (`tools_server.py`):**

```python
import sys
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("local-tools")

@app.list_tools()
async def list_tools():
    return [
        {
            "name": "calculate",
            "description": "Perform calculations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"}
                },
                "required": ["expression"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "calculate":
        result = eval(arguments["expression"])
        return {"result": result}

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### 2. SSE Transport

**Remote servers** that communicate via Server-Sent Events over HTTP.

**Add SSE server:**

```
/mcp-add remote-api --transport sse --url "http://api.example.com/mcp"
```

**Configuration:**

```yaml
mcp_servers:
  remote-api:
    transport: sse
    url: http://api.example.com/mcp
    headers:
      Authorization: Bearer YOUR_TOKEN
```

## Working with MCP Tools

### Discovering Tools

**List all tools:**

```
/mcp-tools
```

**List tools from specific server:**

```
/mcp-tools my-server
```

**Tool information includes:**

- Name
- Description
- Input schema (parameters)
- Output format

### Calling Tools

**From DSPy Code:**

```
/mcp-call my-server search_web query="DSPy framework" max_results=5
```

**From DSPy Programs:**

```python
import dspy
from dspy_code.mcp import MCPClientManager

class WebSearchModule(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager
        self.summarizer = dspy.ChainOfThought("context, query -> summary")

    async def forward(self, query):
        # Call MCP tool
        results = await self.mcp.call_tool(
            server="my-server",
            tool="search_web",
            arguments={"query": query, "max_results": 5}
        )

        # Process with DSPy
        context = "\n".join([r["snippet"] for r in results])
        summary = self.summarizer(context=context, query=query)

        return summary
```

### Tool Parameters

**Required parameters:**

```python
arguments = {
    "query": "machine learning",  # Required
    "max_results": 10             # Optional with default
}
```

**Schema validation:**

MCP validates parameters against the tool's input schema.

## Working with MCP Resources

### Discovering Resources

**List all resources:**

```
/mcp-resources
```

**List resources from specific server:**

```
/mcp-resources my-server
```

**Resource information includes:**

- URI
- Name
- Description
- MIME type

### Reading Resources

**From DSPy Code:**

```
/mcp-read my-server file:///path/to/document.txt
```

**From DSPy Programs:**

```python
class DocumentAnalyzer(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager
        self.analyzer = dspy.ChainOfThought("document -> analysis")

    async def forward(self, resource_uri):
        # Read resource
        content = await self.mcp.read_resource(
            server="my-server",
            uri=resource_uri
        )

        # Analyze with DSPy
        analysis = self.analyzer(document=content)

        return analysis
```

## Working with MCP Prompts

### Discovering Prompts

**List all prompts:**

```
/mcp-prompts
```

**Prompt information includes:**

- Name
- Description
- Arguments
- Template

### Using Prompts

**Get prompt:**

```
/mcp-prompt my-server analysis-template topic="AI safety"
```

**From DSPy Programs:**

```python
class TemplatedAnalysis(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager
        self.executor = dspy.Predict("prompt -> response")

    async def forward(self, topic):
        # Get prompt template
        prompt = await self.mcp.get_prompt(
            server="my-server",
            name="analysis-template",
            arguments={"topic": topic}
        )

        # Execute with DSPy
        response = self.executor(prompt=prompt)

        return response
```

## Advanced MCP Usage

### Multiple Servers

Connect to multiple MCP servers:

```
/mcp-add web-tools --transport stdio --command "python web_server.py"
/mcp-add db-tools --transport stdio --command "python db_server.py"
/mcp-add api-tools --transport sse --url "http://api.example.com/mcp"

/mcp-connect web-tools
/mcp-connect db-tools
/mcp-connect api-tools
```

**Use in programs:**

```python
class MultiSourceAnalyzer(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager
        self.analyzer = dspy.ChainOfThought("data -> insights")

    async def forward(self, query):
        # Get data from multiple sources
        web_data = await self.mcp.call_tool(
            "web-tools", "search", {"query": query}
        )

        db_data = await self.mcp.call_tool(
            "db-tools", "query", {"sql": f"SELECT * FROM data WHERE topic='{query}'"}
        )

        api_data = await self.mcp.call_tool(
            "api-tools", "fetch", {"endpoint": f"/data/{query}"}
        )

        # Combine and analyze
        all_data = {
            "web": web_data,
            "database": db_data,
            "api": api_data
        }

        insights = self.analyzer(data=str(all_data))
        return insights
```

### Error Handling

**Handle MCP errors:**

```python
from dspy_code.mcp.exceptions import MCPError, MCPConnectionError, MCPToolError

class RobustMCPModule(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager
        self.processor = dspy.Predict("input -> output")

    async def forward(self, query):
        try:
            # Try MCP tool
            data = await self.mcp.call_tool(
                "my-server", "search", {"query": query}
            )
        except MCPConnectionError:
            # Server not connected
            return {"error": "MCP server not available"}
        except MCPToolError as e:
            # Tool execution failed
            return {"error": f"Tool failed: {e}"}
        except MCPError as e:
            # Other MCP error
            return {"error": f"MCP error: {e}"}

        # Process data
        result = self.processor(input=data)
        return result
```

### Async/Await Pattern

MCP operations are asynchronous:

```python
import asyncio

class AsyncMCPModule(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager

    async def forward(self, query):
        # Parallel MCP calls
        results = await asyncio.gather(
            self.mcp.call_tool("server1", "tool1", {"q": query}),
            self.mcp.call_tool("server2", "tool2", {"q": query}),
            self.mcp.call_tool("server3", "tool3", {"q": query})
        )

        return results

# Usage
async def main():
    module = AsyncMCPModule(mcp_manager)
    result = await module(query="test")
    print(result)

asyncio.run(main())
```

## Creating Custom MCP Servers

### Basic Server Template

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import asyncio

# Create server
app = Server("my-custom-server")

# Define tools
@app.list_tools()
async def list_tools():
    return [
        {
            "name": "my_tool",
            "description": "Does something useful",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "First parameter"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Second parameter"
                    }
                },
                "required": ["param1"]
            }
        }
    ]

# Implement tool
@app.call_tool()
async def call_tool(name, arguments):
    if name == "my_tool":
        param1 = arguments["param1"]
        param2 = arguments.get("param2", 0)

        # Do something
        result = f"Processed {param1} with {param2}"

        return {"result": result}

    raise ValueError(f"Unknown tool: {name}")

# Define resources
@app.list_resources()
async def list_resources():
    return [
        {
            "uri": "file:///data/example.txt",
            "name": "Example Data",
            "description": "Example data file",
            "mimeType": "text/plain"
        }
    ]

# Implement resource reading
@app.read_resource()
async def read_resource(uri):
    if uri == "file:///data/example.txt":
        with open("/path/to/example.txt") as f:
            content = f.read()
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": content
                }
            ]
        }

    raise ValueError(f"Unknown resource: {uri}")

# Run server
async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Server with Database Access

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
import sqlite3
import json

app = Server("database-server")

# Database connection
conn = sqlite3.connect("data.db")

@app.list_tools()
async def list_tools():
    return [
        {
            "name": "query",
            "description": "Execute SQL query",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string"}
                },
                "required": ["sql"]
            }
        }
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "query":
        sql = arguments["sql"]

        # Execute query
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()

        # Format results
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in rows]

        return {"results": results}

# ... rest of server code
```

## MCP Configuration

### Server Configuration

`dspy_config.yaml`:

```yaml
mcp_servers:
  # stdio server
  local-tools:
    transport: stdio
    command: python
    args:
      - tools_server.py
    env:
      PYTHONPATH: /path/to/modules

  # SSE server
  remote-api:
    transport: sse
    url: https://api.example.com/mcp
    headers:
      Authorization: Bearer ${API_TOKEN}
      X-Custom-Header: value

  # Another stdio server
  database:
    transport: stdio
    command: node
    args:
      - db_server.js
    working_dir: /path/to/server
```

### Environment Variables

Use environment variables in configuration:

```yaml
mcp_servers:
  api-server:
    transport: sse
    url: ${MCP_API_URL}
    headers:
      Authorization: Bearer ${MCP_API_TOKEN}
```

Set in environment:

```bash
export MCP_API_URL="https://api.example.com/mcp"
export MCP_API_TOKEN="your-token-here"
```

## Best Practices

### 1. Server Lifecycle

**Connect when needed:**

```python
# Connect at module initialization
class MyModule(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager
        # Server should already be connected
```

**Disconnect when done:**

```
/mcp-disconnect my-server
```

### 2. Error Handling

Always handle MCP errors:

```python
try:
    result = await mcp.call_tool(server, tool, args)
except MCPError as e:
    # Handle error
    logger.error(f"MCP error: {e}")
    result = None
```

### 3. Timeouts

Set timeouts for MCP calls:

```python
import asyncio

try:
    result = await asyncio.wait_for(
        mcp.call_tool(server, tool, args),
        timeout=30.0
    )
except asyncio.TimeoutError:
    # Handle timeout
    result = None
```

### 4. Caching

Cache MCP results when appropriate:

```python
from functools import lru_cache

class CachedMCPModule(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager

    @lru_cache(maxsize=100)
    async def cached_call(self, server, tool, args_tuple):
        args = dict(args_tuple)
        return await self.mcp.call_tool(server, tool, args)

    async def forward(self, query):
        # Convert args to hashable tuple for caching
        args_tuple = tuple(sorted({"query": query}.items()))
        result = await self.cached_call("server", "search", args_tuple)
        return result
```

### 5. Resource Management

Clean up resources:

```python
class ResourceAwareMCPModule(dspy.Module):
    def __init__(self, mcp_manager):
        super().__init__()
        self.mcp = mcp_manager

    async def __aenter__(self):
        # Setup
        await self.mcp.connect("my-server")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup
        await self.mcp.disconnect("my-server")

# Usage
async with ResourceAwareMCPModule(mcp_manager) as module:
    result = await module(query="test")
```

## Troubleshooting

### Server Won't Connect

**Check configuration:**

```
/mcp-list
```

**Test command manually:**

```bash
python tools_server.py
```

**Check logs:**

```
/mcp-connect my-server --verbose
```

### Tool Not Found

**List available tools:**

```
/mcp-tools my-server
```

**Check tool name spelling**

**Verify server is connected**

### Invalid Parameters

**Check tool schema:**

```
/mcp-tools my-server
```

**Validate arguments match schema**

**Check required vs optional parameters**

## Summary

MCP integration enables:

- ✅ External tool access
- ✅ Data source integration
- ✅ API connectivity
- ✅ Extended DSPy capabilities

**Key concepts:**

- Servers provide tools/resources/prompts
- stdio for local, SSE for remote
- Async operations
- Error handling essential
- Configuration in `dspy_config.yaml`

[See MCP Examples →](https://github.com/superagentic-ai/dspy-code/tree/main/examples){ .md-button .md-button--primary }
[Back to Advanced Topics →](../advanced/custom-modules.md){ .md-button }
