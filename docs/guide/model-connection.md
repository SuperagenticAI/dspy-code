# Model Connection

Connect DSPy Code to any LLM provider for code generation and optimization.

## Supported Providers

DSPy Code supports all major LLM providers:

- **Ollama** - Local models (free, private)
- **OpenAI** - GPT-4, GPT-3.5-turbo
- **Anthropic** - Claude 3 (Opus, Sonnet, Haiku)
- **Gemini** - Google's Gemini Pro

## Quick Connect

### Ollama (Local - Recommended for Beginners)

```
/connect ollama llama3.1:8b
```

**Advantages:**
- ✅ Free
- ✅ Private (runs locally)
- ✅ No API key needed
- ✅ Fast

**Requirements:**
- Ollama installed
- Model downloaded: `ollama pull llama3.1:8b`

### OpenAI

```
/connect openai gpt-4
```

**Requirements:**
- OpenAI API key
- Set environment variable: `export OPENAI_API_KEY=sk-...`

### Anthropic

```
/connect anthropic claude-3-sonnet
```

**Requirements:**
- Anthropic API key
- Set environment variable: `export ANTHROPIC_API_KEY=sk-ant-...`

### Gemini

```
/connect gemini gemini-pro
```

**Requirements:**
- Google API key
- Set environment variable: `export GOOGLE_API_KEY=...`

## Connection Status

Check your connection:

```
/status
```

Output shows:
- ✅ Model Connected: llama3.1:8b (ollama)
- Or: ❌ No Model Connected

## Disconnect

```
/disconnect
```

## Configure Default Model

Edit `dspy_config.yaml`:

```yaml
models:
  default: ollama/llama3.1:8b
```

## Troubleshooting

### Ollama Not Running

```
Error: Could not connect to Ollama
```

**Solution:** Start Ollama: `ollama serve`

### Invalid API Key

```
Error: Invalid API key
```

**Solution:** Check environment variable is set correctly

### Model Not Found

```
Error: Model not found
```

**Solution:** For Ollama: `ollama pull llama3.1:8b`

[Learn About Code Generation →](generating-code.md){ .md-button .md-button--primary }
