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

- Access data that **isn’t already in your Python process**
- Call **external systems** (APIs, databases, search, Slack, etc.)
- Build **richer workflows** than “prompt in, answer out”

If you’re just generating local DSPy code from natural language, you don’t need MCP.
As soon as you want your program to “reach out” to the world, MCP becomes very useful.

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
