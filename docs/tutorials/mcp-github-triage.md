# 🐙 MCP GitHub Triage Copilot

Build a **GitHub triage assistant** that pulls issues/PRs via an MCP server and uses
DSPy to summarize and suggest next actions.

---

## 🎯 What You’ll Build

- Connect to a `github` MCP server
- Fetch recent issues (and optionally PRs) for a repository
- Ask questions like:

  > "Give me a morning triage summary of open issues for this repo and what I should do first."

DSPy Code uses your connected model to turn raw MCP data into a concise triage report.

---

## 🧩 Prerequisites

- DSPy Code installed and working
- A GitHub repository you can access
- `GITHUB_TOKEN` with appropriate scopes (e.g. `repo`)

```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

---

## ⚙️ Configure the GitHub MCP Server

First, make sure your project has a DSPy Code config:

```bash
dspy-code
→ /init
```

This will create a `dspy_config.yaml` in your project root if it doesn’t exist yet.

Then add a `github` server to your `dspy_config.yaml`. You can base it on
the example in `examples/mcp_config_examples.yaml`:

```yaml
mcp_servers:
  github:
    name: github
    description: "GitHub API access"
    enabled: true
    auto_connect: false
    transport:
      type: sse
      url: https://api.github.com/mcp
      headers:
        Authorization: "Bearer ${GITHUB_TOKEN}"
        Accept: "application/vnd.github.v3+json"
    timeout_seconds: 60
    retry_attempts: 3
```

Make sure `GITHUB_TOKEN` is set in your shell before you start DSPy Code.

---

## 🧪 Try It in the CLI

Start DSPy Code:

```bash
dspy-code
```

Connect and explore tools:

```bash
→ /mcp-connect github
→ /mcp-tools github
```

Then try calling a GitHub tool (tool names may vary by server implementation):

```bash
→ /mcp-call github list_issues owner="your-user" repo="your-repo" state="open"
```

Now ask DSPy Code to help with triage:

```text
→ Use the GitHub MCP data we just fetched to summarize the top 10 open issues
  by severity, add suggested labels, and list the 3 most important next actions.
```

---

## 🧠 Optional: Run the triage script (for source users)

You **do not** need the DSPy Code source repository to follow this tutorial.  
Everything above works with a normal `pip install dspy-code` and the `dspy-code` CLI only.

If you’ve cloned the **dspy-code** GitHub repo and are working inside it, you can also run
the companion example script:

```bash
python examples/mcp_github_triage_assistant.py
```

This script lives in the repo and automates the same flow:

- Loads your `dspy_config.yaml`
- Connects to the `github` MCP server
- Calls a tool (e.g. `list_issues`) to fetch open issues
- Uses a DSPy module to generate a triage summary and prioritized actions

You can change the owner/repo values at the bottom of the script to point to your own project.

---

## 🚀 Next Ideas

- Include PRs and generate a combined "review + issues" dashboard
- Auto-suggest labels based on content and MCP data
- Create a daily triage cron job that runs this script and posts results to Slack (via another MCP server)

Once this pattern is working, you can layer more MCP servers (databases, Slack, CI, etc.)
to build a fully automated triage pipeline powered by DSPy.
