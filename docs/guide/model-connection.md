# Model Connection

Connect DSPy Code to local and cloud LLM providers for code generation and optimization.

## Provider Overview

DSPy Code supports both **local** and **cloud** LLMs:

- **Ollama (Local)** – Runs models on your machine (free, private)
- **OpenAI (Cloud)** – GPT‑4o, gpt‑5 family (e.g. gpt‑5‑nano)
- **Anthropic (Cloud)** – Claude Sonnet/Opus 4.5 (paid only)
- **Google Gemini (Cloud)** – Gemini 2.5 family (via `google-genai`)

!!! info "Local vs Cloud"
    - **Local (Ollama)**: Best for experimentation, zero API cost, but uses your CPU/GPU and RAM.
    - **Cloud (OpenAI, Anthropic, Gemini)**: Best quality and scale, but **billed per token**. Optimization workflows can generate *many* calls.

## Quick Connect

### Easiest: Interactive Model Selector

```bash
/model
```

This walks you through:

- Picking **Ollama** (local) vs **cloud** providers
- For Ollama: selecting from detected models (for example `gpt-oss:120b`, `llama3.2`) by number
- For cloud: picking **OpenAI**, **Anthropic**, or **Gemini** and then typing a model name (for example `gpt-5-nano`, `claude-sonnet-4.5`, `gemini-2.5-flash`)

### Ollama (Local - Recommended for Beginners)

```bash
/connect ollama gpt-oss:120b
```

**Advantages:**
- ✅ Free
- ✅ Private (runs locally)
- ✅ No API key needed
- ✅ Fast

**Requirements:**
- Ollama installed
- Model downloaded: `ollama pull gpt-oss:120b`

### OpenAI (Cloud)

```bash
/connect openai gpt-5-nano
```

**Requirements:**

- OpenAI Python SDK (installed via `dspy-code[openai]`)
- OpenAI API key: `export OPENAI_API_KEY=sk-...`

!!! tip "Use the Best Model You Have"
    `gpt-5-nano` is a good starter model. For higher quality, switch to **gpt‑4o** or newer gpt‑5 family models your account supports.

### Anthropic (Cloud, Paid Only)

```bash
/connect anthropic claude-sonnet-4.5
```

**Requirements:**

- Anthropic Python SDK (installed via `dspy-code[anthropic]`)
- Anthropic API key: `export ANTHROPIC_API_KEY=sk-ant-...`

> Anthropic no longer offers free API keys. DSPy Code fully supports Claude if you have a paid key; otherwise, just skip Anthropic.

### Google Gemini (Cloud)

```bash
/connect gemini gemini-2.5-flash
```

**Requirements:**

- Google Gen AI SDK (`google-genai`, installed via `dspy-code[gemini]`)
- API key: `export GEMINI_API_KEY=...` (or `GOOGLE_API_KEY=...`)

!!! tip "Check Your Quotas"
    All cloud providers enforce quotas and rate limits. If you see 429 or quota errors during optimization, check your usage dashboards and billing settings.

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
