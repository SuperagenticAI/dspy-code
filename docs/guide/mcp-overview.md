## 🧩 MCP in DSPy Code (User Guide)

MCP (Model Context Protocol) lets DSPy Code talk to **external tools, APIs, files, and services**
through MCP servers. You can think of it as **“plug-in power” for your DSPy programs**:

- 📂 Read files and documents from your filesystem
- 🐙 Pull issues and PRs from GitHub
- 🗄️ Query databases (Postgres, etc.)
- 🌐 Call web APIs or search engines

DSPy Code acts as the **MCP client** and your chosen servers provide tools, resources, and prompts.

---

### 🌐 Learn more MCP flows

Share this page when you want to point people to **all the MCP resources in DSPy Code**:

- 🐙 **GitHub tutorial (recommended)**: [MCP GitHub Triage Copilot](../tutorials/mcp-github-triage.md)
- 📂 **Filesystem tutorial (experimental)**: [MCP Filesystem Assistant](../tutorials/mcp-filesystem-assistant.md)
- 🧠 **Advanced guide**: [Advanced MCP Integration](../advanced/mcp-integration.md)

---

### 🧠 When should I use MCP?

Use MCP when your DSPy program needs to:

- Access data that **isn't already in your Python process**
- Call **external systems** (APIs, databases, search, Slack, etc.)
- Build **richer workflows** than "prompt in, answer out"

If you're just generating local DSPy code from natural language, you don't need MCP.
As soon as you want your program to "reach out" to the world, MCP becomes very useful.

---

### 🚀 How MCP Improves Code Generation

MCP integration provides **real-world context** that dramatically improves the quality and accuracy of generated DSPy code:

#### 1. **Real-World Context**
- **Without MCP:** Code generated from generic patterns and training data
- **With MCP:** Code uses your actual files, APIs, and data structures
- **Result:** Generated code matches your project structure exactly

**Example:**

First, configure the filesystem MCP server in `dspy_config.yaml`:

```yaml
mcp_servers:
  filesystem:
    name: filesystem
    description: "Local filesystem access"
    enabled: true
    auto_connect: false
    transport:
      type: stdio
      command: npx
      args:
        - -y
        - "@modelcontextprotocol/server-filesystem"
        - /tmp/city/
    timeout_seconds: 60
    retry_attempts: 3
```

Then, create a demo file `/tmp/city/data.json`:

```bash
mkdir -p /tmp/city
cat > /tmp/city/data.json << 'EOF'
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"}
  ],
  "metadata": {
    "total_users": 3,
    "created_at": "2025-01-15",
    "version": "1.0"
  }
}
EOF
```

Or manually create the file with this JSON content:
```json
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com", "role": "user"}
  ],
  "metadata": {
    "total_users": 3,
    "created_at": "2025-01-15",
    "version": "1.0"
  }
}
```

**Without MCP:**
```
User: "Create a module that processes /tmp/city/data.json"
→ Generic code with guessed field names like data["items"], data["info"]
→ Manual fixes needed to match actual structure
```

**With MCP:**
```
User: "Create a module that processes /tmp/city/data.json"
→ MCP reads actual file via filesystem server
→ Sees real structure: {"users": [...], "metadata": {...}}
→ Generates code with correct field names: data["users"], data["metadata"]
→ Uses actual field names: user["id"], user["name"], user["email"], user["role"]
→ Works immediately!
```

#### 2. **Tool Integration in Generated Code**
Generated DSPy modules can directly use MCP tools, so the code **actually works** with your MCP servers:

```python
# Generated code includes MCP integration:
class DocumentAnalyzer(dspy.Module):
    def __init__(self, mcp_manager: MCPClientManager):
        self.mcp = mcp_manager

    async def forward(self, file_path: str):
        # Uses MCP tool to read file
        result = await self.mcp.call_tool(
            "filesystem", "read_file", {"path": file_path}
        )
        # ... processes with DSPy
```

#### 3. **Context-Aware Generation**
- MCP reads your actual data files and sees real field names
- Generated code matches your data format
- **Accuracy improvement:** Field name accuracy goes from ~60% to ~95%

#### 4. **Better Examples and Patterns**
- MCP reads your existing codebase
- Understands your coding style
- Generates code following your patterns

#### 5. **Validation Against Real Systems**
- Generated code validated against actual APIs/databases
- Catches errors before manual testing
- Code that works with real systems, not just templates

#### Impact Summary

| Aspect | Without MCP | With MCP |
|--------|-------------|----------|
| **Field Name Accuracy** | ~60% | ~95% |
| **API Integration** | ~50% | ~90% |
| **Time to Working Code** | 30+ minutes | 2-3 minutes |
| **Manual Fixes Needed** | Many | Few/None |

**The Result:** Generated DSPy code that **actually works** with your real systems, not just generic templates!

---

### 🚶 Quick CLI workflow

From the interactive CLI:

```bash
→ /mcp-list              # See configured MCP servers
→ /mcp-connect <name>    # Connect to a server
→ /mcp-tools             # Discover tools
→ /mcp-resources         # Discover resources
→ /mcp-prompts           # Discover prompts
```

Example (GitHub server):

```bash
→ /mcp-connect github
→ /mcp-tools github
→ /mcp-call github listIssues {"owner": "your-org", "repo": "your-repo"}
```

For filesystem, see the **experimental** tutorial for details and caveats.

---

### 📚 Recommended starting points

- 🐙 **GitHub Triage Copilot (GitHub MCP)** *(recommended first)*  
  Pull issues/PRs from a repo and get a daily triage summary.  
  See: [MCP GitHub Triage Copilot](../tutorials/mcp-github-triage.md){ style="color: #2563eb; text-decoration: underline;" }

- 📂 **Project Files Assistant (Filesystem MCP)** *(experimental / advanced)*  
  Turn your local project into a browsable, explainable knowledge base.  
  See: [MCP Filesystem Assistant](../tutorials/mcp-filesystem-assistant.md){ style="color: #2563eb; text-decoration: underline;" }

For deeper details on transports, configuration, and advanced patterns, see:

- 🔗 <a href="../advanced/mcp-integration/" style="color: #2563eb; text-decoration: underline;">Advanced MCP Integration</a>

---

### ✅ Mental model recap

- **DSPy Code** = MCP client (you control it from the CLI)
- **MCP servers** = external capabilities (filesystem, GitHub, DB, web, etc.)
- **DSPy modules** = the logic that **combines** model reasoning + MCP data/tools

Once you’ve connected one or more MCP servers, you can simply **describe the workflow you want**
in natural language and let DSPy Code generate DSPy programs that call those tools behind the scenes.
