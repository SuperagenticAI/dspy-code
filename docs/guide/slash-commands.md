# Slash Commands Reference

All commands in DSPy Code start with `/`. This page lists every command with examples.

## Project Commands

### /init

Initialize or scan your DSPy project.

```
/init
```

**What it does:**

- Creates `dspy_config.yaml` if it doesn't exist
- Scans your project code
- Indexes your installed DSPy version
- Shows entertaining jokes while indexing!

**When to use:**

- Starting a new project
- After installing new packages
- When you want to refresh the code index

!!! example "Example Output"
    ```
    📖 Building Codebase Knowledge Base

    What's being indexed:
      • Your installed DSPy
      • Your project code
      • GEPA optimizer (if installed)

    🤖 Teaching the AI to read your code...
    ✓ Index built successfully!

    💡 You can now ask questions about:
      • DSPy concepts
      • Your project code
      • Code examples
    ```

### /status

Show your current session status.

```
/status
```

**What it shows:**

- Generated code in context
- Training data (if any)
- Conversation message count
- Connected model status
- Available commands

!!! tip "Use This When"
    - You're not sure if code was generated
    - You want to see what's in your session
    - You forgot if you saved your code

**Example:**

```
/status
```

Output:
```
📊 Session Status

✓ Generated Code: module
  Lines: 45
  Characters: 1234
  Available commands: /save, /validate, /run

💬 Conversation: 6 messages
🤖 Connected Model: llama3.1:8b (ollama)

💡 Next Steps:
  /save <filename>.py - Save your code
  /validate - Check for issues
  /run - Test execution
```

### /clear

Clear conversation history and start fresh.

```
/clear
```

**What it does:**

- Clears all conversation messages
- Removes generated code from context
- Gives you a clean slate

!!! warning "This Cannot Be Undone"
    Make sure to save any code you want to keep before clearing!

## Code Generation Commands

### /create

Interactive wizard for creating DSPy components.

```
/create
```

**What it does:**

- Asks you questions about what you want to build
- Guides you through the process
- Generates complete code

**Or just describe what you want:**

```
Create a sentiment analyzer
```

```
Build a question answering system
```

```
Make a text classifier for emails
```

!!! tip "Natural Language Works!"
    You don't need to use `/create`. Just describe what you want in plain English!

### /demo

See example DSPy programs in action.

```
/demo
```

**What it shows:**

- Complete working examples
- Different DSPy patterns
- Code you can learn from

**Run a specific demo:**

```
/demo sentiment
```

```
/demo qa
```

```
/demo rag
```

### /examples

Browse DSPy templates and patterns.

```
/examples
```

**What you'll see:**

- Signature templates
- Module patterns
- Complete program templates
- Industry-specific examples

**Generate from a template:**

```
/examples generate rag
```

## Model Connection Commands

### /model

Interactively select and connect to a model.

**Basic usage:**

```bash
/model
```

You will be prompted to choose:

- Local models via **Ollama** (auto-detected from your Ollama installation)
- Cloud providers: **OpenAI**, **Anthropic**, **Gemini** (you then type the model name, e.g. `gpt-5-nano`, `claude-sonnet-4.5`, `gemini-2.5-flash`)

**Shortcuts:**

```bash
/model ollama   # Only show local Ollama models and pick one by number
/model cloud    # Pick a cloud provider, then type the model name
```

### /connect

Directly connect to a specific model if you already know the name.

**Ollama (Local):**

```bash
/connect ollama gpt-oss:120b
```

**OpenAI:**

```bash
/connect openai gpt-5-nano
```

**Anthropic Claude:**

```bash
/connect anthropic claude-sonnet-4.5
```

**Google Gemini:**

```bash
/connect gemini gemini-2.5-flash
```

!!! info "API Keys"
    For cloud providers, set your API key first:
    ```bash
    export OPENAI_API_KEY=sk-...
    export ANTHROPIC_API_KEY=sk-ant-...
    export GEMINI_API_KEY=AIza...
    ```

### /disconnect

Disconnect from the current model.

```
/disconnect
```

**When to use:**

- Switching to a different model
- Working offline with templates
- Troubleshooting connection issues

## Code Management Commands

### /save

Save generated code to a file.

```
/save sentiment.py
```

```
/save my_module.py
```

**Where it saves:**

- Default: `generated/` directory
- Creates directory if it doesn't exist
- Won't overwrite without confirmation

!!! tip "Always Save!"
    After generating code you like, save it immediately. Use `/status` to check if you have code to save.

### /validate

Check your code for issues and best practices.

```
/validate
```

**Validates last generated code**

```
/validate my_program.py
```

**Validates a specific file**

**What it checks:**

- Signature correctness
- Module structure
- Best practices
- Common mistakes
- Security issues

!!! success "Quality Assurance"
    Always validate before running. It catches issues early!

### /run

Execute your DSPy program safely.

```
/run
```

**Runs last generated code**

```
/run my_program.py
```

**Runs a specific file**

**Safety features:**

- Runs in a sandbox
- Timeout protection
- Error handling
- Safe execution

!!! warning "Sandbox Execution"
    Your code runs in a safe sandbox. Some operations (like file I/O) may be restricted.

### /test

Run tests on your code.

```
/test
```

```
/test my_program.py
```

**What it does:**

- Runs unit tests
- Checks functionality
- Reports results

## Optimization Commands

### /optimize

Generate GEPA optimization code.

```
/optimize
```

!!! warning "Be Aware of Optimization Cost"
    GEPA optimization can issue **many LLM calls**, especially when using cloud providers (OpenAI, Anthropic, Gemini). Make sure you understand your API pricing and quotas before running `/optimize`, and prefer small budgets when starting out. For local models, we recommend at least **32 GB RAM** for comfortable optimization runs.

**What it creates:**

- Complete GEPA optimization script
- Metric with feedback
- Training data loaders
- Configuration

**Options:**

```
/optimize --budget light
```

```
/optimize --budget medium
```

```
/optimize --budget heavy
```

!!! info "Real GEPA"
    This generates code that uses REAL GEPA optimization from your installed DSPy version!

### /eval

Generate evaluation code for your program.

```
/eval
```

**What it creates:**

- Evaluation metrics
- Test harness
- Reporting code

## Help Commands

### /help

Show all available commands.

```
/help
```

**What you'll see:**

- Complete command list
- Usage examples
- Tips and tricks

### /intro

Complete guide to DSPy Code.

```
/intro
```

**Perfect for:**

- New users
- Learning all features
- Understanding workflows

### /explain

Get explanations of DSPy concepts.

```
/explain signatures
```

```
/explain modules
```

```
/explain optimizers
```

**Topics you can ask about:**

- Signatures
- Modules
- Predictors
- Optimizers
- GEPA
- Metrics

## Session Commands

### /session save

Save your current session.

```
/session save my-work
```

**What it saves:**

- Conversation history
- Generated code
- Session context

### /session load

Load a saved session.

```
/session load my-work
```

**Restores:**

- All conversation messages
- Generated code
- Session state

### /sessions

List all saved sessions.

```
/sessions
```

### /session delete

Delete a saved session.

```
/session delete my-work
```

## Data Commands

### /save-data

Save generated training data.

```
/save-data examples.jsonl
```

```
/save-data training.json
```

**When to use:**

- After generating training examples
- Before optimization
- For backup

## MCP Commands

### /mcp-add

Add an MCP server.

```
/mcp-add my-server --transport stdio --command "python server.py"
```

### /mcp-connect

Connect to an MCP server.

```
/mcp-connect my-server
```

### /mcp-disconnect

Disconnect from an MCP server.

```
/mcp-disconnect my-server
```

### /mcp-list

List all MCP servers.

```
/mcp-list
```

### /mcp-tools

List tools from an MCP server.

```
/mcp-tools my-server
```

## Utility Commands

### /history

Show conversation history.

```
/history
```

**Show all messages:**

```
/history all
```

### /refresh-index

Rebuild the codebase index.

```
/refresh-index
```

**When to use:**

- After updating DSPy
- After adding new code
- If index seems stale

### /index-status

Check the status of your codebase index.

```
/index-status
```

**Shows:**

- Index age
- Number of files indexed
- Cache size
- Staleness warning

### /exit

Exit DSPy Code.

```
/exit
```

**Or use:**

```
exit
```

```
quit
```

```
bye
```

## Command Tips

!!! tip "Tab Completion"
    Many terminals support tab completion. Type `/` and press Tab to see available commands!

!!! tip "Command History"
    Use the up arrow to recall previous commands.

!!! tip "Partial Commands"
    You can often use shortcuts:
    - `/h` for `/help`
    - `/s` for `/status`
    - `/v` for `/validate`

!!! tip "Case Insensitive"
    Commands are case insensitive:
    - `/HELP` works
    - `/Help` works
    - `/help` works

## Next Steps

Now that you know all the commands, learn how to use them effectively:

[Generating Code →](generating-code.md){ .md-button .md-button--primary }
[Model Connection →](model-connection.md){ .md-button }
