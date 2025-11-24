# Project Management

Complete guide to managing DSPy projects with DSPy Code, from initialization to deployment.

## Starting a New Project vs Existing Project

DSPy Code supports two workflows:

1. **Blank Project** - Start from scratch
2. **Existing Project** - Add DSPy Code to existing codebase

### Blank Project (Fresh Start)

Use the `--fresh` flag to create a complete project structure:

```bash
dspy-code
/init --fresh
```

**What gets created:**

```
my-dspy-project/
├── dspy_config.yaml          # Active configuration
├── dspy_config_example.yaml  # Reference configuration
├── README.md                 # Project documentation
├── generated/                # Generated DSPy code
│   └── .gitkeep
├── data/                     # Training data
│   └── .gitkeep
├── modules/                  # Custom modules
│   └── .gitkeep
├── signatures/               # DSPy signatures
│   └── .gitkeep
├── programs/                 # Complete programs
│   └── .gitkeep
├── optimizers/               # Optimization scripts
│   └── .gitkeep
├── tests/                    # Test files
│   └── .gitkeep
├── .cache/                   # Codebase index cache
└── examples/                 # Example programs
    └── hello_dspy.py
```

**Interactive prompts:**

```
Project name [my-dspy-project]: customer-support-ai
✓ Created project structure
✓ Generated configuration files
✓ Created example programs

Would you like to configure a default model? [Y/n]: y

Select provider:
  1. Ollama (local)
  2. OpenAI
  3. Anthropic
  4. Gemini
  5. Skip for now

Choice [1]: 1

Model name [llama3.1:8b]: llama3.1:8b
✓ Model configured

Building codebase knowledge base...
🤖 Teaching the AI to read your code...
✓ Indexed DSPy 3.0.4
✓ Indexed your project
✓ Index built successfully!

Next Steps:
1. Start interactive mode: dspy-code
2. Generate your first module: "Create a sentiment analyzer"
3. Connect to model: /connect ollama llama3.1:8b
```

### Existing Project (Minimal Setup)

Add DSPy Code to an existing project:

```bash
cd my-existing-project
dspy-code
/init
```

**What gets created:**

```
my-existing-project/
├── (your existing files)
├── dspy_config.yaml          # Minimal config
├── dspy_config_example.yaml  # Reference
└── .cache/                   # Index cache
```

**Directories created on-demand:**

- `generated/` - When you save generated code
- `data/` - When you save training data
- `modules/` - When you export modules

**Interactive prompts:**

```
Project name [my-existing-project]:
✓ Minimal configuration created

Scanning existing project...
✓ Found 15 Python files
✓ Detected existing DSPy code in 3 files

Building codebase knowledge base...
📚 Indexing your installed DSPy...
📁 Scanning your project files...
✓ Index built successfully!

Your existing DSPy code:
  • modules/sentiment.py
  • programs/classifier.py
  • signatures/analysis.py

Next Steps:
1. Ask about your code: "Explain my sentiment module"
2. Generate new code: "Create a RAG module"
3. Optimize existing: /optimize modules/sentiment.py
```

## Project Initialization Options

### Command-Line Options

```bash
# Fresh project with full structure
dspy-code /init --fresh

# Specify project name
dspy-code /init --name "my-project"

# Specify directory
dspy-code /init --path /path/to/project

# Configure model during init
dspy-code /init --provider ollama --model llama3.1:8b

# Verbose output
dspy-code /init --verbose
```

### Interactive Mode

Within DSPy Code:

```
/init
```

**Prompts you'll see:**

1. **Project name** - Defaults to directory name
2. **Reinitialize?** - If already initialized
3. **Model configuration** - Optional model setup
4. **Fresh structure?** - Create full directories

## Configuration Files

### dspy_config.yaml

Active configuration for your project:

```yaml
# Project Information
project_name: customer-support-ai
dspy_version: "3.0.4"
created_at: "2025-01-15T10:30:00"

# Model Configuration
models:
  default: ollama/llama3.1:8b

  ollama:
    llama3.1:8b:
      base_url: http://localhost:11434
      timeout: 60

  openai:
    gpt-4:
      api_key: ${OPENAI_API_KEY}
      max_tokens: 2000
      temperature: 0.7

  anthropic:
    claude-3-sonnet:
      api_key: ${ANTHROPIC_API_KEY}
      max_tokens: 4000

# Directory Structure
paths:
  generated: generated/
  data: data/
  modules: modules/
  signatures: signatures/
  programs: programs/
  optimizers: optimizers/
  tests: tests/
  cache: .cache/

# Codebase RAG
rag:
  enabled: true
  cache_ttl: 86400  # 24 hours
  index_patterns:
    - "*.py"
    - "!__pycache__"
    - "!.venv"
    - "!venv"

# Optimization
optimization:
  default_budget: medium
  save_checkpoints: true
  checkpoint_dir: .cache/checkpoints/

# Validation
validation:
  enabled: true
  min_quality_score: 80
  auto_fix: false

# MCP Servers
mcp_servers: {}
```

### dspy_config_example.yaml

Reference configuration with all options:

```yaml
# Complete configuration example with all available options
# Copy sections you need to dspy_config.yaml

project_name: example-project
dspy_version: "3.0.4"

# Model providers
models:
  default: ollama/llama3.1:8b

  # Local Ollama
  ollama:
    llama3.1:8b:
      base_url: http://localhost:11434
      timeout: 60

    mistral:
      base_url: http://localhost:11434
      timeout: 60

  # OpenAI
  openai:
    gpt-4:
      api_key: ${OPENAI_API_KEY}
      max_tokens: 2000
      temperature: 0.7
      organization: ${OPENAI_ORG}  # Optional

    gpt-3.5-turbo:
      api_key: ${OPENAI_API_KEY}
      max_tokens: 1000
      temperature: 0.7

  # Anthropic
  anthropic:
    claude-3-sonnet:
      api_key: ${ANTHROPIC_API_KEY}
      max_tokens: 4000
      temperature: 0.7

    claude-3-opus:
      api_key: ${ANTHROPIC_API_KEY}
      max_tokens: 4000

  # Google Gemini
  gemini:
    gemini-pro:
      api_key: ${GOOGLE_API_KEY}
      max_tokens: 2048

# Paths
paths:
  generated: generated/
  data: data/
  modules: modules/
  signatures: signatures/
  programs: programs/
  optimizers: optimizers/
  tests: tests/
  cache: .cache/
  exports: exports/

# Codebase RAG configuration
rag:
  enabled: true
  cache_ttl: 86400
  max_file_size: 1048576  # 1MB
  index_patterns:
    - "*.py"
    - "!__pycache__"
    - "!*.pyc"
    - "!.venv"
    - "!venv"
    - "!node_modules"

  # Codebases to index
  codebases:
    - name: dspy
      auto_discover: true
    - name: gepa
      auto_discover: true
    - name: project
      path: .

# Optimization settings
optimization:
  default_budget: medium
  budgets:
    light:
      breadth: 5
      depth: 2
      max_iterations: 10
    medium:
      breadth: 10
      depth: 3
      max_iterations: 20
    heavy:
      breadth: 15
      depth: 4
      max_iterations: 30

  save_checkpoints: true
  checkpoint_dir: .cache/checkpoints/
  checkpoint_interval: 5

# Validation settings
validation:
  enabled: true
  min_quality_score: 80
  auto_fix: false
  rules:
    - signature_structure
    - module_structure
    - best_practices
    - type_hints
    - documentation

  ignore_patterns:
    - "test_*.py"
    - "*_test.py"

# Execution settings
execution:
  sandbox: true
  timeout: 30
  max_memory_mb: 512

# MCP server configurations
mcp_servers:
  # Example stdio server
  local-tools:
    transport: stdio
    command: python
    args:
      - tools_server.py
    env:
      PYTHONPATH: /path/to/modules
    working_dir: ./mcp_servers

  # Example SSE server
  remote-api:
    transport: sse
    url: https://api.example.com/mcp
    headers:
      Authorization: Bearer ${MCP_API_TOKEN}
      X-Custom-Header: value

# Logging
logging:
  level: INFO
  file: .cache/dspy-code.log
  max_size_mb: 10
  backup_count: 3
```

## Project Structure Best Practices

### Organizing Generated Code

**By feature:**

```
generated/
├── sentiment/
│   ├── signature.py
│   ├── module.py
│   └── program.py
├── classification/
│   ├── signature.py
│   └── module.py
└── rag/
    ├── retrieval.py
    ├── generation.py
    └── rag_module.py
```

**By type:**

```
signatures/
├── sentiment_signature.py
├── classification_signature.py
└── rag_signatures.py

modules/
├── sentiment_analyzer.py
├── classifier.py
└── rag_module.py

programs/
├── sentiment_app.py
├── classification_app.py
└── rag_app.py
```

### Organizing Training Data

```
data/
├── sentiment/
│   ├── train.jsonl
│   ├── val.jsonl
│   └── test.jsonl
├── classification/
│   ├── emails_train.jsonl
│   └── emails_val.jsonl
└── rag/
    ├── qa_pairs.jsonl
    └── documents.jsonl
```

### Organizing Optimization Scripts

```
optimizers/
├── sentiment_gepa.py
├── classification_gepa.py
└── rag_gepa.py
```

## Codebase Indexing

### What Gets Indexed

**1. Your Installed DSPy:**

```
Discovering codebases...
✓ Found DSPy 3.0.4 at /path/to/site-packages/dspy
  - 150 Python files
  - 234 classes
  - 1,456 functions
```

**2. Your Installed GEPA (if available):**

```
✓ Found GEPA 1.2.0 at /path/to/site-packages/gepa
  - 45 Python files
  - 89 classes
  - 456 functions
```

**3. Your Installed MCP (if available):**

```
✓ Found MCP 1.2.1 at /path/to/site-packages/mcp
  - 87 Python files
  - 156 classes
  - 678 functions
```

**4. Your Project Code:**

```
✓ Scanning project at /path/to/project
  - 12 Python files
  - 15 classes
  - 78 functions
```

**5. Configured MCP Servers:**

```
✓ Found MCP server 'local-tools' at ./mcp_servers
  - 3 Python files
  - 8 tools defined
```

### Index Contents

The index includes:

- **Classes** - Names, docstrings, methods
- **Functions** - Signatures, docstrings, parameters
- **Signatures** - DSPy signatures with fields
- **Modules** - DSPy modules with predictors
- **Imports** - Dependencies and usage
- **Comments** - Inline documentation

### Using the Index

**Ask about DSPy concepts:**

```
How does ChainOfThought work?
```

Response uses YOUR installed DSPy version!

**Ask about your code:**

```
What modules do I have?
Explain my sentiment analyzer
How does my RAG module work?
```

**Ask for examples:**

```
Show me a ChainOfThought example
How do I use ReAct?
```

### Refreshing the Index

**Manual refresh:**

```
/refresh-index
```

**Check index status:**

```
/index-status
```

**Output:**

```
Codebase Index Status:

✓ Index loaded: 3,421 elements
  - DSPy: 1,890 elements
  - GEPA: 545 elements
  - MCP: 834 elements
  - Project: 152 elements

Last updated: 2 hours ago
Cache size: 2.3 MB

Index is stale (>24 hours old)
Run /refresh-index to rebuild
```

## Project Scanning

### Automatic Scanning

DSPy Code automatically scans your project during `/init`:

```
Scanning existing project...
✓ Found 15 Python files
✓ Detected existing DSPy code in 3 files

Your existing DSPy code:
  • modules/sentiment.py - SentimentAnalyzer
  • programs/classifier.py - EmailClassifier
  • signatures/analysis.py - AnalysisSignature
```

### Manual Scanning

```
/project scan
```

**Output:**

```
Project Scan Results:

DSPy Components Found:
  Signatures: 5
    - SentimentSignature (signatures/sentiment.py)
    - ClassificationSignature (signatures/classification.py)
    - QASignature (signatures/qa.py)
    - RetrievalSignature (signatures/rag.py)
    - GenerationSignature (signatures/rag.py)

  Modules: 3
    - SentimentAnalyzer (modules/sentiment.py)
    - EmailClassifier (modules/classifier.py)
    - RAGModule (modules/rag.py)

  Programs: 2
    - sentiment_app.py
    - classification_app.py

Training Data:
  - data/sentiment_train.jsonl (50 examples)
  - data/classification_train.jsonl (100 examples)

Optimization Scripts:
  - optimizers/sentiment_gepa.py
```

### Project Context

View project context:

```
/project context
```

**Output:**

```
Project Context:

Name: customer-support-ai
DSPy Version: 3.0.4
Created: 2025-01-15

Components:
  - 5 Signatures
  - 3 Modules
  - 2 Programs
  - 150 training examples
  - 1 optimization script

Recent Activity:
  - Generated SentimentAnalyzer (2 hours ago)
  - Optimized EmailClassifier (1 day ago)
  - Created 50 training examples (1 day ago)

Model Configuration:
  Default: ollama/llama3.1:8b
  Connected: Yes
```

## Environment Variables

### Model API Keys

```bash
# OpenAI
export OPENAI_API_KEY=sk-...
export OPENAI_ORG=org-...  # Optional

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
export GOOGLE_API_KEY=...

# MCP
export MCP_API_TOKEN=...
```

### DSPy Code Configuration

```bash
# Override config file location
export DSPY_CLI_CONFIG=/path/to/config.yaml

# Override cache directory
export DSPY_CLI_CACHE=/path/to/cache

# Enable debug logging
export DSPY_CLI_DEBUG=1

# Disable codebase RAG
export DSPY_CLI_RAG_DISABLED=1
```

## Migration Guide

### From Manual DSPy to DSPy Code

**1. Initialize in existing project:**

```bash
cd my-dspy-project
dspy-code
/init
```

**2. Scan existing code:**

```
/project scan
```

**3. Ask about your code:**

```
Explain my existing modules
What signatures do I have?
```

**4. Generate new code:**

```
Create a new module for [task]
```

**5. Optimize existing code:**

```
/optimize modules/my_module.py data/train.jsonl
```

### From Other Tools

**From LangChain:**

DSPy Code can help convert:

```
I have a LangChain chain that does [description]. Create equivalent DSPy code.
```

**From Prompt Engineering:**

Convert manual prompts:

```
I have this prompt: "[your prompt]". Create a DSPy signature and module.
```

## Troubleshooting

### Project Already Initialized

```
This directory already contains a DSPy project. Reinitialize? [y/N]:
```

Choose `y` to:
- Update configuration
- Rebuild index
- Keep existing files

### Permission Errors During Indexing

```
⚠️  Could not index /path/to/package (permission denied)
✓ DSPy Code will still work!
```

**Solutions:**

1. Run with appropriate permissions
2. Install packages in user directory: `pip install --user`
3. Use virtual environment

### Index Build Fails

```
⚠️  Could not build codebase index
You can still use DSPy Code, but Q&A about code will be limited
```

**Solutions:**

1. Check Python package installations
2. Verify project directory is readable
3. Try `/refresh-index` later

### Model Not Configured

```
⚠️  No default model configured
```

**Solutions:**

```
/connect ollama llama3.1:8b
```

Or edit `dspy_config.yaml`:

```yaml
models:
  default: ollama/llama3.1:8b
```

## Best Practices

### 1. Use Fresh for New Projects

```bash
dspy-code /init --fresh
```

Creates complete structure from the start.

### 2. Use Minimal for Existing Projects

```bash
cd existing-project
dspy-code /init
```

Doesn't interfere with existing structure.

### 3. Keep Configuration in Version Control

```bash
git add dspy_config.yaml
git commit -m "Add DSPy Code configuration"
```

But ignore cache:

```
# .gitignore
.cache/
```

### 4. Use Environment Variables for Secrets

Never commit API keys!

```yaml
# dspy_config.yaml
models:
  openai:
    gpt-4:
      api_key: ${OPENAI_API_KEY}  # From environment
```

### 5. Refresh Index Regularly

After major changes:

```
/refresh-index
```

### 6. Organize by Feature or Type

Choose one structure and stick with it.

### 7. Use Descriptive Project Names

```
customer-support-ai  # Good
project1            # Bad
```

## Summary

Project management in DSPy Code:

- ✅ Blank projects with `--fresh`
- ✅ Existing projects with minimal setup
- ✅ Automatic codebase indexing
- ✅ Project scanning
- ✅ Configuration management
- ✅ Environment variables
- ✅ Migration support

**Key commands:**

- `/init` - Initialize project
- `/init --fresh` - Create full structure
- `/project scan` - Scan existing code
- `/project context` - View project info
- `/refresh-index` - Rebuild index
- `/index-status` - Check index

[Learn About Code Generation →](generating-code.md){ .md-button .md-button--primary }
[See Complete Workflow →](../tutorials/sentiment-analyzer.md){ .md-button }
