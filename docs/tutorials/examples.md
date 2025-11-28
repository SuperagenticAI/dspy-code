# Running Examples with Ollama

This tutorial shows you how to run all the example scripts from the DSPy Code repository using Ollama for local execution. All examples are configured to work without API keys, making them perfect for learning and experimentation.

## Prerequisites

Before running the examples, you'll need:

1. **Python 3.10+** installed
2. **Ollama** installed and running locally
3. **DSPy Code** repository cloned or installed
4. **Required Python packages**

### Step 1: Install Ollama

If you haven't installed Ollama yet:

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

### Step 2: Start Ollama and Pull the Model

Start the Ollama service:
```bash
ollama serve
```

In a new terminal, pull the model used by the examples:
```bash
ollama pull llama3.1:8b
```

This will download the `llama3.1:8b` model (approximately 4.7GB). The examples use this model for all LLM operations.

### Step 3: Clone the Repository

If you haven't already, clone the DSPy Code repository:

```bash
git clone https://github.com/SuperagenticAI/dspy-code.git
cd dspy-code
```

### Step 4: Install Dependencies

Install the required Python packages:

```bash
pip install dspy dspy-code
```

Or if you want to install from source:

```bash
pip install -e .
pip install dspy
```

## Available Examples

The `examples/` directory contains several ready-to-run scripts:

### 1. Complete Workflow Example

**File:** `examples/complete_workflow_example.py`

**What it demonstrates:**
- Creating a DSPy Signature for sentiment analysis
- Building a Module with Chain of Thought reasoning
- Preparing training examples
- Optimizing with GEPA (Genetic Pareto)
- Evaluating the optimized module

**How to run:**
```bash
cd /path/to/dspy-code
python examples/complete_workflow_example.py
```

**Expected output:**
- Model configuration
- Module creation
- Pre-optimization test
- GEPA optimization progress (takes 3-10 minutes)
- Post-optimization validation results

**Key features:**
- Uses `ollama/llama3.1:8b` for both main LM and reflection LM
- Demonstrates the full DSPy workflow from signature to optimization
- Shows GEPA optimization with 30 metric calls budget
- Includes validation evaluation

---

### 2. Email Classifier Demo

**File:** `examples/email_classifier_demo.py`

**What it demonstrates:**
- Email classification by priority (urgent, normal, low)
- Multi-field signature (subject, body, sender)
- Chain of Thought reasoning for classification
- Training data preparation
- Module optimization

**How to run:**
```bash
cd /path/to/dspy-code
python examples/email_classifier_demo.py
```

**Expected output:**
- Email classification examples
- Module predictions before optimization
- Training data preparation
- Optimization process
- Improved accuracy after optimization

**Key features:**
- Realistic use case (email triage)
- Multi-input signature design
- Priority classification with reasoning

---

### 3. MCP Filesystem Assistant

**File:** `examples/mcp_filesystem_assistant.py`

**What it demonstrates:**
- Integrating MCP (Model Context Protocol) filesystem server
- Reading project files via MCP
- Using DSPy modules with MCP tools
- File summarization workflow

**Prerequisites:**
- Node.js installed (for MCP server)
- MCP filesystem server configured

**How to run:**

First, ensure you have Node.js installed:
```bash
node --version  # Should show v18 or higher
```

Then run the example:
```bash
cd /path/to/dspy-code
python examples/mcp_filesystem_assistant.py
```

**Configuration:**
The script expects a `dspy_config.yaml` with MCP filesystem server configuration. See `examples/mcp_config_examples.yaml` for reference.

**Expected output:**
- MCP server connection
- File reading via MCP tools
- File content summarization
- Project file analysis

**Note:** This example is experimental. For a more stable MCP example, see the GitHub triage assistant below.

---

### 4. MCP GitHub Triage Assistant

**File:** `examples/mcp_github_triage_assistant.py`

**What it demonstrates:**
- MCP GitHub server integration
- Fetching GitHub issues and pull requests
- Summarizing and triaging issues with DSPy
- Using MCP tools for external API access

**Prerequisites:**
- GitHub personal access token (optional, for private repos)
- Node.js installed
- MCP GitHub server configured

**How to run:**

1. Create or edit `dspy_config.yaml` in your project root:
```yaml
mcp_servers:
  github:
    name: github
    description: "GitHub API access via MCP"
    enabled: true
    auto_connect: false
    transport:
      type: stdio
      command: npx
      args:
        - -y
        - "@modelcontextprotocol/server-github"
    timeout_seconds: 30
    retry_attempts: 3
```

2. If using a GitHub token, set it as an environment variable:
```bash
export GITHUB_TOKEN=your_token_here
```

3. Run the example:
```bash
cd /path/to/dspy-code
python examples/mcp_github_triage_assistant.py
```

**Expected output:**
- MCP GitHub server connection
- Issue/PR fetching
- Summarization and triage recommendations
- Priority classification

**Key features:**
- Stable MCP integration example
- Real-world use case (GitHub issue triage)
- External API integration via MCP

---

## Common Issues and Solutions

### Issue: "Connection refused" or "Failed to connect to Ollama"

**Solution:**
1. Ensure Ollama is running: `ollama serve`
2. Check if the model is pulled: `ollama list`
3. Verify the API base URL in the script matches your Ollama setup (default: `http://localhost:11434`)

### Issue: "Model not found" or "Model llama3.1:8b not found"

**Solution:**
```bash
ollama pull llama3.1:8b
```

### Issue: "Module 'dspy' not found"

**Solution:**
```bash
pip install dspy
```

### Issue: MCP examples fail with "Connection failed"

**Solution:**
1. Ensure Node.js is installed: `node --version`
2. Check `dspy_config.yaml` exists and is correctly configured
3. Verify MCP server package names are correct:
   - Filesystem: `@modelcontextprotocol/server-filesystem`
   - GitHub: `@modelcontextprotocol/server-github`
4. Try running the MCP server command manually to test:
   ```bash
   npx -y @modelcontextprotocol/server-filesystem /path/to/directory
   ```

### Issue: GEPA optimization takes too long

**Solution:**
- The examples use `max_metric_calls=30` for reasonable demo times
- For faster testing, reduce this value in the script
- For production, increase to 100+ for better optimization

### Issue: "Out of memory" errors

**Solution:**
- The `llama3.1:8b` model requires ~8GB RAM
- Close other applications
- Consider using a smaller model: `ollama pull llama3.1:3b`

## Customizing Examples

All examples use the same Ollama configuration. To customize:

1. **Change the model:**
   ```python
   lm = dspy.LM(model="ollama/your-model:tag", api_base="http://localhost:11434")
   ```

2. **Change the API base:**
   If Ollama is running on a different host/port:
   ```python
   lm = dspy.LM(model="ollama/llama3.1:8b", api_base="http://your-host:11434")
   ```

3. **Adjust GEPA budget:**
   In optimization examples, modify:
   ```python
   optimizer = GEPA(
       metric=your_metric,
       reflection_lm=reflection_lm,
       max_metric_calls=50,  # Increase for better results, decrease for speed
   )
   ```

## Next Steps

After running the examples:

1. **Modify the examples** to suit your use case
2. **Create your own signatures** and modules
3. **Build your own training data** using the patterns shown
4. **Explore the interactive CLI** to build programs interactively:
   ```bash
   dspy-code
   ```
5. **Read the tutorials** for deeper understanding:
   - [Build a Sentiment Analyzer](sentiment-analyzer.md)
   - [Create a RAG System](rag-system.md)
   - [Optimize with GEPA](gepa-optimization.md)

## Example File Reference

| File | Purpose | Runtime | Complexity |
|------|---------|---------|------------|
| `complete_workflow_example.py` | Full DSPy workflow with GEPA | 5-15 min | Intermediate |
| `email_classifier_demo.py` | Email classification use case | 5-10 min | Intermediate |
| `mcp_filesystem_assistant.py` | MCP filesystem integration | 1-2 min | Advanced |
| `mcp_github_triage_assistant.py` | MCP GitHub integration | 2-5 min | Advanced |
| `mcp_config_examples.yaml` | MCP server configurations | Reference | - |

## Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [DSPy Documentation](https://dspy-docs.vercel.app/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [DSPy Code GitHub Repository](https://github.com/SuperagenticAI/dspy-code)

---

**💡 Tip:** Start with `complete_workflow_example.py` to understand the full DSPy workflow, then explore the other examples based on your interests!
