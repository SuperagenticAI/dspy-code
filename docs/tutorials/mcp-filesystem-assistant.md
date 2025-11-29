# 📂 MCP Filesystem Assistant (Experimental)

> ⚠️ **Experimental / advanced tutorial**  
> This flow depends on the evolving `@modelcontextprotocol/server-filesystem` and MCP SDK
> behavior. It is **not guaranteed to work out-of-the-box** across all environments.
> If you just want a solid, end‑to‑end MCP example, start with the
> **🐙 MCP GitHub Triage Copilot** tutorial instead.

Build a "Project Files Assistant" that uses the **filesystem MCP server** to read your code
and a **DSPy module** to explain it back to you.

---

## 🎯 What You’ll Build

- Connect to the `filesystem` MCP server
- Browse and read project files via MCP
- Ask natural language questions like:

  > "Explain what the main CLI entrypoint and interactive command do."

DSPy Code will then generate a summary using your **connected model**.

---

## 🧩 Prerequisites

- DSPy Code installed and working
- A project where you want to explore files
- `uv` installed (recommended)  
- Node.js installed (for `npx`)

---

## 📦 Install the Filesystem MCP Server

The filesystem MCP server is an npm package that will be automatically downloaded and run via `npx` when you use it. However, you need to ensure Node.js is installed first.

### Step 1: Verify Node.js Installation

Check if Node.js is installed:

```bash
node --version
npx --version
```

If Node.js is not installed:

- **macOS/Linux**: Install via [nvm](https://github.com/nvm-sh/nvm) or download from [nodejs.org](https://nodejs.org/)
- **Windows**: Download from [nodejs.org](https://nodejs.org/)

### Step 2: Test the MCP Server (Optional)

You can test that the MCP server package is accessible:

```bash
npx -y @modelcontextprotocol/server-filesystem /tmp
```

You should see: `Secure MCP Filesystem Server running on stdio`

Press `Ctrl+C` to stop it. This confirms the package can be downloaded and run.

---

## ⚙️ Configure the Filesystem MCP Server

First, make sure your project has a DSPy Code config:

```bash
dspy-code
→ /init
```

This will create a `dspy_config.yaml` in your project root if it doesn’t exist yet.

### Step 1: Create or Edit `dspy_config.yaml`

Edit `dspy_config.yaml` in your project root and add a `filesystem` server configuration.

**Option A: Using the CLI (Recommended)**

```bash
dspy-code
→ /init
```

This creates `dspy_config.yaml` if it doesn't exist. Then manually edit it to add the MCP server config.

**Option B: Manual Configuration**

Create or edit `dspy_config.yaml` in your project root and add:

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

**Note:** This example uses `/tmp/city/` as the accessible directory. You can replace it with your project path or add multiple directories.

### Step 2: Configure Directory Paths

**Important:** Replace `/absolute/path/to/your/project` with the **absolute path** to your project directory.

**Finding your project's absolute path:**

- **macOS/Linux**: Run `pwd` in your project directory
- **Windows**: Run `cd` in your project directory, or use File Explorer to copy the path

**Examples:**
- macOS: `/Users/john/my-project`
- Linux: `/home/john/my-project`
- Windows: `C:\Users\john\my-project` (use forward slashes in YAML: `C:/Users/john/my-project`)

**Multiple directories:**

You can specify multiple directories by adding more paths to the `args` list:

```yaml
args:
  - -y
  - "@modelcontextprotocol/server-filesystem"
  - /Users/john/project1
  - /Users/john/project2
  - /Users/john/shared-data
```

The MCP server will only allow access to these specified directories for security.

### Step 3: Verify Configuration

Check that your configuration is valid:

```bash
dspy-code
→ /mcp-servers
```

You should see your `filesystem` server listed. If there are errors, check:
- YAML syntax (proper indentation, no tabs)
- Absolute paths are correct
- Node.js is installed (`node --version`)

### Step 4: Create Demo Data File (Optional)

For this tutorial, we'll use `/tmp/city/` as our accessible directory. Create a demo data file to test with:

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

Or manually create `/tmp/city/data.json` with this content:

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

This demo file will be used in the examples below to demonstrate how MCP reads actual file structures for better code generation.

---

## 🧪 Try It in the CLI (advanced)

Start DSPy Code in your project:

```bash
dspy-code
```

**First, connect a model** (if you haven't already):

```bash
→ /model openai gpt-4o-mini
# or
→ /model anthropic claude-3-5-sonnet-20241022
```

Then connect to the MCP server and explore **tools** (not resources):

```bash
→ /mcp-connect filesystem
→ /mcp-tools filesystem
```

You should see tools like:

- A tool to **read a file** (for example: `readFile` or `filesystem.readFile`)
- A tool to **list a directory** (for example: `listDirectory`)

### Step 1: Find the exact tool name

**You MUST run this first** to see the actual tool names:

```bash
→ /mcp-tools filesystem
```

You'll see a table like:

```
┌─────────────────────────────────────────────────────────┐
│ Tools from 'filesystem'                                 │
├─────────────────────────┬───────────────────────────────┤
│ Name                    │ Description                  │
├─────────────────────────┼───────────────────────────────┤
│ read_file               │ Read contents of a file       │
│ list_directory          │ List files in a directory    │
└─────────────────────────┴───────────────────────────────┘
```

**Copy the exact tool name** from the "Name" column. Common names are:
- `read_file` (most common)
- `readFile` (camelCase variant)
- `filesystem.readFile` (namespaced variant)

### Step 2: Read a file using the tool (may require debugging)

Once you know the tool name (let's say it's `read_file`), use it like this:

```bash
→ /mcp-call filesystem read_file {"path": "test_mcp_config.py"}
```

**Important notes:**

1. **Do NOT wrap the JSON in single quotes.** The CLI parses JSON directly, so it must start with `{`, not `'`.

2. **Use the exact tool name** from `/mcp-tools filesystem` - don't guess!

3. **Path format:**
   - Use a **relative path** from your allowed root (recommended): `"test_mcp_config.py"`
   - Or an **absolute path** that's still inside the allowed root: `"/Users/you/my-project/test_mcp_config.py"`

4. **Example with different tool name:**
   If `/mcp-tools filesystem` shows `readFile` (camelCase), use:
   ```bash
   → /mcp-call filesystem readFile {"path": "test_mcp_config.py"}
   ```

### Troubleshooting: "Tool call failed" (common with filesystem server)

If you get an error, **this is expected sometimes** with the current filesystem server.
Things to try:

1. **Tool name is correct:** Run `/mcp-tools filesystem` and copy the exact name
2. **File exists:** Make sure the file is in your allowed directory
3. **Path is correct:** Use relative path from allowed root, or absolute path inside it
4. **JSON syntax:** No quotes around the JSON, must start with `{`
5. **Check the raw error:** The CLI will now show detailed MCP error information
6. **If it still fails:** Treat this tutorial as a reference pattern, not a guaranteed flow, and prefer the GitHub tutorial for production use

### Step 3: Test with Demo Data File

Now let's test reading the demo `data.json` file we created:

```bash
→ /mcp-call filesystem read_file {"path": "/tmp/city/data.json"}
```

Or if using relative path from the allowed directory:

```bash
→ /mcp-call filesystem read_file {"path": "data.json"}
```

You should see the JSON content with users and metadata. This demonstrates how MCP can read actual file structures.

### Step 4: See How MCP Improves Code Generation

Now that MCP can read your actual data file, try generating code that uses it:

```text
→ Create a module that processes the users in /tmp/city/data.json
```

**Without MCP:**
- Code would use guessed field names like `data["items"]`, `data["info"]`
- You'd need to manually fix field names to match your actual structure

**With MCP:**
- MCP reads the actual `data.json` file
- Sees real structure: `{"users": [...], "metadata": {...}}`
- Generates code with correct field names: `data["users"]`, `data["metadata"]`
- Uses actual user fields: `user["id"]`, `user["name"]`, `user["email"]`, `user["role"]`
- Code works immediately without manual fixes!

### Use it in natural-language requests

After you've confirmed `/mcp-call` works, you can ask things like:

```text
→ Use the filesystem MCP to read `dspy_code/main.py` and
  explain what this file does at a high level.
```

Or with the demo data:

```text
→ Create a sentiment analyzer for the user data in /tmp/city/data.json
```

DSPy Code will use the MCP tools to fetch file contents and then let your model reason over them, generating code that matches your actual data structure.

---

## 🧠 Optional: Run the example script (for source users)

You **do not** need the DSPy Code source to follow this tutorial.  
Everything above is intended as an **advanced pattern** and may require MCP debugging.

If you’ve cloned the **dspy-code** GitHub repo and are working inside it, you can also run
the companion example script:

```bash
python examples/mcp_filesystem_assistant.py
```

This script lives in the repo and simply automates the same flow:

- Loads your `dspy_config.yaml`
- Connects to the `filesystem` MCP server
- Reads a couple of important files (like `dspy_code/main.py`)
- Uses a DSPy module to summarize what they do

You can adapt the list of paths and the question to match your own project.

---

## 🚀 Next Ideas

- Scan a whole folder for TODOs and generate a prioritized task list
- Compare two versions of a file via MCP and summarize the changes
- Build a "Docs explainer" that reads Markdown files and answers questions

Once you're comfortable with the filesystem server, you can combine it with
other MCP servers (databases, APIs, search) for richer workflows.

---

## 🔧 Troubleshooting

### "Command not found: npx" or "npx: command not found"

**Problem:** Node.js is not installed or not in your PATH.

**Solution:**
1. Install Node.js from [nodejs.org](https://nodejs.org/)
2. Restart your terminal
3. Verify: `node --version` and `npx --version`

### "Cannot connect to MCP server" or Connection timeout

**Problem:** The MCP server failed to start or the configuration is incorrect.

**Solutions:**
1. **Check Node.js is working:**
   ```bash
   npx -y @modelcontextprotocol/server-filesystem /tmp
   ```
   Should show: `Secure MCP Filesystem Server running on stdio`

2. **Verify paths in config:**
   - Use absolute paths (not relative)
   - Paths must exist and be accessible
   - On Windows, use forward slashes in YAML: `C:/Users/...`

3. **Check YAML syntax:**
   - Proper indentation (spaces, not tabs)
   - All required fields present
   - No syntax errors

4. **Test connection manually:**
   ```bash
   dspy-code
   → /mcp-connect filesystem
   ```
   Look for error messages in the output.

### "Permission denied" when reading files

**Problem:** The MCP server doesn't have permission to access the directory.

**Solutions:**
1. Ensure the directory path in `args` includes the folder you want to access
2. Check file permissions: `ls -la /path/to/directory` (macOS/Linux)
3. The MCP server can only access directories listed in the `args` configuration

### "File not found" or empty output when using `/mcp-call`

**Problem:** The path you passed to the filesystem tool is wrong or outside the allowed root.

**Solutions:**
1. Make sure the file is actually inside one of the directories you passed to `@modelcontextprotocol/server-filesystem` in `args`
2. Prefer **relative paths** from the allowed root, e.g. `"src/main.py"` instead of a long absolute path
3. Double-check spelling and case of the filename
4. Use `/mcp-tools filesystem` to confirm the exact tool name and argument shape (the CLI prints the JSON schema)

### Still having issues?

1. Check the DSPy Code logs for detailed error messages
2. Verify your `dspy_config.yaml` matches the example format exactly
3. Test the MCP server standalone: `npx -y @modelcontextprotocol/server-filesystem /your/path`
4. See the [Advanced MCP Integration](../advanced/mcp-integration.md) guide for more details
