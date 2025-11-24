# Configuration Reference

Complete reference for DSPy Code configuration files and settings.

---

## Configuration File

DSPy Code uses `dspy_config.yaml` in your project root for configuration.

**Location:** `./dspy_config.yaml`

---

## File Structure

```yaml
project:
  name: my-dspy-code-project
  version: "1.0.0"
  description: "My DSPy project"

models:
  default: ollama-llama3.1:8b
  providers:
    - name: ollama-llama3.1:8b
      type: ollama
      model: llama3.1:8b
      base_url: http://localhost:11434

    - name: openai-gpt4
      type: openai
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}

    - name: anthropic-claude
      type: anthropic
      model: claude-3-5-sonnet-20241022
      api_key: ${ANTHROPIC_API_KEY}

mcp_servers:
  - name: filesystem
    transport: stdio
    command: uvx
    args:
      - mcp-server-filesystem
    env:
      - name: MCP_SERVER_FILESYSTEM_ROOT
        value: /path/to/root

rag:
  enabled: true
  index_path: .dspy_code/rag_index
  chunk_size: 1000
  chunk_overlap: 200

session:
  auto_save: true
  auto_save_interval: 300  # seconds
  session_dir: .dspy_code/sessions
```

---

## Project Configuration

### `project.name`

**Type:** String  
**Required:** No  
**Default:** `my-dspy-code-project`

Project name identifier.

---

### `project.version`

**Type:** String  
**Required:** No  
**Default:** `"1.0.0"`

Project version.

---

### `project.description`

**Type:** String  
**Required:** No  
**Default:** `""`

Project description.

---

## Model Configuration

### `models.default`

**Type:** String  
**Required:** No

Name of the default model to use. Must match a model name in `models.providers`.

---

### `models.providers`

**Type:** List  
**Required:** No  
**Default:** `[]`

List of model provider configurations.

### Provider Configuration

Each provider has the following structure:

```yaml
- name: <unique-name>        # Required: Unique identifier
  type: <provider-type>      # Required: ollama, openai, anthropic, gemini
  model: <model-name>        # Required: Model identifier
  api_key: <key-or-env-var>  # Optional: API key or ${ENV_VAR}
  base_url: <url>            # Optional: Custom base URL
  temperature: <float>       # Optional: Temperature (0.0-2.0)
  max_tokens: <int>           # Optional: Max tokens
```

### Provider Types

#### Ollama

```yaml
- name: local-llama
  type: ollama
  model: llama3.1:8b
  base_url: http://localhost:11434  # Optional
```

#### OpenAI

```yaml
- name: gpt4
  type: openai
  model: gpt-4o
  api_key: ${OPENAI_API_KEY}  # Or direct key
```

#### Anthropic

```yaml
- name: claude
  type: anthropic
  model: claude-3-5-sonnet-20241022
  api_key: ${ANTHROPIC_API_KEY}
```

#### Gemini

```yaml
- name: gemini
  type: gemini
  model: gemini-pro
  api_key: ${GEMINI_API_KEY}
```

---

## MCP Server Configuration

### `mcp_servers`

**Type:** List  
**Required:** No  
**Default:** `[]`

List of MCP server configurations.

### MCP Server Configuration

```yaml
- name: <server-name>        # Required: Unique identifier
  transport: <type>          # Required: stdio, sse, websocket
  command: <command>         # Required for stdio: Command to run
  args: [<arg1>, ...]        # Optional: Command arguments
  env:                        # Optional: Environment variables
    - name: <VAR_NAME>
      value: <value>
  url: <url>                  # Required for sse/websocket: Server URL
```

### Transport Types

#### stdio

```yaml
- name: filesystem
  transport: stdio
  command: uvx
  args:
    - mcp-server-filesystem
  env:
    - name: MCP_SERVER_FILESYSTEM_ROOT
      value: /path/to/root
```

#### sse (Server-Sent Events)

```yaml
- name: github
  transport: sse
  url: https://api.github.com/mcp
  headers:                    # Optional
    Authorization: Bearer ${GITHUB_TOKEN}
```

#### websocket

```yaml
- name: custom-server
  transport: websocket
  url: wss://example.com/mcp
```

---

## RAG Configuration

### `rag.enabled`

**Type:** Boolean  
**Required:** No  
**Default:** `true`

Enable codebase RAG features.

---

### `rag.index_path`

**Type:** String  
**Required:** No  
**Default:** `.dspy_code/rag_index`

Path to store the RAG index.

---

### `rag.chunk_size`

**Type:** Integer  
**Required:** No  
**Default:** `1000`

Size of text chunks for indexing.

---

### `rag.chunk_overlap`

**Type:** Integer  
**Required:** No  
**Default:** `200`

Overlap between chunks.

---

## Session Configuration

### `session.auto_save`

**Type:** Boolean  
**Required:** No  
**Default:** `true`

Enable automatic session saving.

---

### `session.auto_save_interval`

**Type:** Integer  
**Required:** No  
**Default:** `300` (5 minutes)

Interval in seconds between auto-saves.

---

### `session.session_dir`

**Type:** String  
**Required:** No  
**Default:** `.dspy_code/sessions`

Directory to store session files.

---

## Environment Variables

You can use environment variables in configuration:

```yaml
api_key: ${OPENAI_API_KEY}
base_url: ${OLLAMA_BASE_URL}
```

**Set environment variables:**

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="..."
```

---

## Configuration Management

### View Configuration

```bash
dspy-code
> /config show
```

### Edit Configuration

Edit `dspy_config.yaml` directly or use:

```bash
dspy-code
> /config edit
```

### Reset Configuration

```bash
dspy-code
> /config reset
```

---

## Example Configurations

### Minimal Configuration

```yaml
models:
  providers:
    - name: local-llama
      type: ollama
      model: llama3.1:8b
```

### Full Configuration

See `dspy_code/templates/dspy_config_example.yaml` for a complete example.

---

## Best Practices

1. **Use Environment Variables** - Never commit API keys directly
2. **Version Control** - Add `dspy_config.yaml` to `.gitignore` if it contains secrets
3. **Default Model** - Set a default model for convenience
4. **MCP Servers** - Configure frequently used MCP servers
5. **RAG Settings** - Adjust chunk size based on your codebase

---

## Troubleshooting

### Configuration Not Found

If DSPy Code can't find your config:

1. Ensure `dspy_config.yaml` is in the project root
2. Run `/init` to create a default configuration

### Model Connection Issues

1. Check API keys are set correctly
2. Verify model names match provider documentation
3. Test connection with `/connect <provider> <model>`

### MCP Server Issues

1. Verify transport type matches server capabilities
2. Check command paths and arguments
3. Test with `/mcp-connect <server-name>`

---

**For more details, see [Project Management](../guide/project-management.md)**
