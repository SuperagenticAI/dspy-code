# Command Reference

Complete reference for all DSPy Code slash commands available in interactive mode.

---

## Overview

All DSPy Code commands are **slash commands** executed in interactive mode. Simply type `/` followed by the command name.

---

## Project Management

### `/init` - Initialize Project

Initialize a new DSPy project or scan an existing one.

**Usage:**
```
/init [--fresh]
```

**Options:**
- `--fresh` - Create a complete project structure with all directories

**Examples:**
```
/init              # Minimal setup (just dspy_config.yaml)
/init --fresh      # Full project structure
```

**What it does:**
- Creates `dspy_config.yaml` configuration file
- Indexes your codebase for RAG features
- Sets up project structure (if `--fresh`)
- Displays entertaining messages during indexing

---

## Code Generation

### `/create` - Generate DSPy Components

Generate DSPy Signatures, Modules, or complete programs.

**Usage:**
```
/create <type> <description>
```

**Types:**
- `signature` - Create a DSPy Signature
- `module` - Create a DSPy Module
- `program` - Create a complete DSPy program

**Examples:**
```
/create signature sentiment analysis with text input and sentiment output
/create module email classifier with subject and body inputs
/create program question answering system with RAG
```

---

## Model Connection

### `/model` - Interactive model selection

Interactively choose and connect to a model (local via Ollama or cloud).

**Usage:**
```
/model
```

Use this if you're not sure which model to pick or don't want to type the full `/connect` command.

### `/connect` - Connect to LLM

Connect to a language model for code generation and execution when you already know the model name.

**Usage:**
```
/connect <provider> <model>
```

**Providers:**
- `ollama` - Local models via Ollama
- `openai` - OpenAI models (GPT-4, GPT-5 family)
- `anthropic` - Claude models
- `gemini` - Google Gemini models

**Examples:**
```
/connect ollama gpt-oss:120b
/connect openai gpt-5-nano
/connect anthropic claude-sonnet-4.5
/connect gemini gemini-2.5-flash
```

**Note:** You may need to install provider SDKs separately. DSPy Code will guide you if needed.

---

## Code Operations

### `/save` - Save Generated Code

Save the last generated code to a file.

**Usage:**
```
/save <filename>
```

**Examples:**
```
/save sentiment_analyzer.py
/save modules/email_classifier.py
```

**Note:** Code must be generated first using natural language or `/create`.

---

### `/validate` - Validate Code

Validate DSPy code for best practices and correctness.

**Usage:**
```
/validate [filename]
```

**Examples:**
```
/validate                    # Validate last generated code
/validate my_module.py       # Validate specific file
```

**What it checks:**
- Syntax correctness
- DSPy best practices
- Signature definitions
- Module structure
- Import statements

---

### `/run` - Execute Program

Run a DSPy program in a sandboxed environment.

**Usage:**
```
/run <filename> [--input key=value] [--test-file data.jsonl]
```

**Options:**
- `--input` - Provide input values as key=value pairs
- `--test-file` - Run with test dataset

**Examples:**
```
/run sentiment_analyzer.py
/run my_program.py --input text="This is great!"
/run classifier.py --test-file test_data.jsonl
```

---

## Optimization

### `/optimize` - Optimize with GEPA

Optimize a DSPy program using GEPA (Genetic Pareto).

**Usage:**
```
/optimize <program.py> [training_data.jsonl]
```

**Examples:**
```
/optimize my_program.py
/optimize classifier.py training_data.jsonl
```

**Requirements:**
- A DSPy program file
- Training data (JSONL format) with input/output examples
- Connected LLM model

**What it does:**
- Evolves prompts using GEPA
- Improves reasoning steps
- Tests on validation set
- Reports performance improvements

---

## Data Generation

### `/generate data` - Create Training Data

Generate training examples for optimization.

**Usage:**
```
/generate data <count> for <task>
```

**Examples:**
```
/generate data 20 for sentiment analysis
/generate data 50 for email classification
```

**Output:** Creates a JSONL file with training examples.

---

## MCP Integration

### `/mcp-add` - Add MCP Server

Add an MCP server configuration.

**Usage:**
```
/mcp-add <name> --transport <type> [options]
```

**Transport Types:**
- `stdio` - Standard input/output
- `sse` - Server-Sent Events
- `websocket` - WebSocket connection

**Examples:**
```
/mcp-add filesystem --transport stdio --command uvx --args mcp-server-filesystem
/mcp-add github --transport sse --url https://api.github.com/mcp
```

---

### `/mcp-connect` - Connect to MCP Server

Connect to a configured MCP server.

**Usage:**
```
/mcp-connect <server-name>
```

**Examples:**
```
/mcp-connect filesystem
/mcp-connect github
```

---

### `/mcp-tools` - List MCP Tools

List available tools from connected MCP servers.

**Usage:**
```
/mcp-tools [server-name]
```

**Examples:**
```
/mcp-tools              # List all tools from all servers
/mcp-tools filesystem   # List tools from specific server
```

---

### `/mcp-resources` - List MCP Resources

List available resources from connected MCP servers.

**Usage:**
```
/mcp-resources [server-name]
```

---

### `/mcp-prompts` - List MCP Prompts

List available prompts from connected MCP servers.

**Usage:**
```
/mcp-prompts [server-name]
```

---

## RAG & Performance

### `/refresh-index` - Rebuild Codebase Index

Rebuild the RAG codebase index for better code generation context.

**Usage:**
```
/refresh-index [--force]
```

**Options:**
- `--force` - Force rebuild even if cache is fresh

**Examples:**
```
/refresh-index           # Rebuild if stale
/refresh-index --force   # Force rebuild
```

**What it does:**
- Re-indexes installed packages (dspy, gepa, mcp)
- Updates project code index
- Improves code generation quality

---

### `/index-status` - Show RAG Index Status

Display current RAG index statistics and status.

**Usage:**
```
/index-status
```

**Shows:**
- Total indexed elements
- Number of codebases
- Cache size
- Index age
- Per-codebase statistics

---

### `/fast-mode` - Toggle Fast Mode

Enable or disable fast mode for faster responses (disables RAG context building).

**Usage:**
```
/fast-mode [on|off]
```

**Options:**
- `on` - Enable fast mode (faster responses, lower code quality)
- `off` - Disable fast mode (slower responses, better code quality)
- (no args) - Show current status

**Examples:**
```
/fast-mode on    # Enable fast mode
/fast-mode off   # Disable fast mode
/fast-mode       # Show current status
```

**Trade-offs:**
- ✅ Faster responses (0.5-1s vs 2-5s)
- ⚠️ Lower code generation quality (no real DSPy examples)
- ✅ Still uses templates and reference docs

---

### `/disable-rag` - Disable RAG Completely

Disable RAG indexing for maximum speed.

**Usage:**
```
/disable-rag
```

**What it does:**
- Disables RAG index loading
- Disables all RAG searches
- Fastest mode (0.3-0.8s responses)
- Code generation uses templates only

**Note:** Code generation quality will be significantly reduced. Use only if speed is critical.

---

### `/enable-rag` - Re-enable RAG

Re-enable RAG indexing for better code quality.

**Usage:**
```
/enable-rag
```

**What it does:**
- Re-enables RAG indexing
- Restores code generation quality
- Slower responses (2-5s) but better code

**Note:** Run `/init` to build index if not already built.

---

## Session Management

### `/status` - Show Session Status

Display current session information.

**Usage:**
```
/status
```

**Shows:**
- Connected models
- Active MCP servers
- Last generated code
- Project configuration

---

### `/history` - View Command History

View your command history in the current session.

**Usage:**
```
/history
```

---

### `/clear` - Clear Screen

Clear the terminal screen.

**Usage:**
```
/clear
```

---

## Help & Information

### `/help` - Show Help

Display help information for all commands.

**Usage:**
```
/help [command]
```

**Examples:**
```
/help              # Show all commands
/help optimize     # Show help for /optimize
```

---

### `/intro` - Introduction Guide

Show comprehensive introduction to DSPy Code.

**Usage:**
```
/intro
```

**Includes:**
- What is DSPy Code
- Key features
- Getting started guide
- Tips and best practices

---

### `/version` - Show Version

Display DSPy Code and DSPy versions.

**Usage:**
```
/version
```

---

## Exit

### `/exit` - Exit Interactive Mode

Exit the DSPy Code interactive session.

**Usage:**
```
/exit
```

**Note:** Your session state is automatically saved.

---

## Natural Language

You can also use natural language instead of slash commands:

**Examples:**
```
Build a sentiment analyzer module
Create a signature for email classification
Generate 20 training examples for sentiment analysis
Optimize my_program.py with training_data.jsonl
```

DSPy Code will understand your intent and execute the appropriate action.

---

## Command Aliases

Some commands have shorter aliases:

- `/h` → `/help`
- `/q` → `/exit`
- `/v` → `/validate`
- `/s` → `/save`

---

## Tips

1. **Tab Completion**: Use tab to autocomplete command names
2. **Command History**: Use up/down arrows to navigate history
3. **Natural Language**: Describe what you want instead of remembering commands
4. **Help**: Use `/help` anytime to see available commands
5. **Status**: Use `/status` to see what's currently loaded

---

**For more details, see the [User Guide](../guide/interactive-mode.md)**
