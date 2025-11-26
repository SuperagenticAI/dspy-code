# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Planned:
  - **Plan / Code modes** in interactive CLI (explicit “planning” vs “coding” flows for complex tasks).
  - First‑class support for **open‑source models via third‑party providers** (e.g. OpenRouter, Groq and similar gateways), alongside existing Ollama + cloud integrations.

### Changed
- Intent routing to further reduce/eliminate **duplicate code generation**, especially with large open‑source models and remote providers.

### Fixed
- TBC

---

## [0.1.0] - 2025-11-26

### Overview
- **First public release** of DSPy Code: an AI-powered, interactive development and optimization assistant for DSPy (think "Claude Code for DSPy").

### Added
- **Interactive CLI & Workflows**
  - Rich TUI with animated thinking indicators, status panels, and history-aware prompts.
  - Fully conversational flow: describe what you want in natural language, get DSPy code, ask follow‑ups.
  - Two core workflows:
    - **Development**: `/init` → describe task → generate → `/validate` → `/run` → iterate.
    - **Optimization**: `/data` → `/optimize` → `/eval` → `/export`.
- **Model Connection & Providers**
  - Support for local **Ollama** models.
  - Cloud providers: **OpenAI**, **Anthropic (Claude)**, **Google Gemini**.
  - New interactive `/model` command:
    - Auto-detect and list Ollama models, pick by number.
    - Cloud flow to pick provider, then type model name (e.g. `gpt-5-nano`, `claude-sonnet-4.5`, `gemini-2.5-flash`).
  - Direct `/connect <provider> <model>` command for advanced users.
  - `/models`, `/status`, `/disconnect` for model management.
- **LLM Integration & SDK Support**
  - OpenAI integration compatible with `openai>=2.x` chat completions API.
  - Anthropic integration via the current `anthropic` Python SDK.
  - Gemini integration via the official `google-genai` SDK, with fallback to `google-generativeai` when present.
  - Local Ollama integration with configurable HTTP timeouts for large models (`OLLAMA_HTTP_TIMEOUT`, `OLLAMA_TEST_TIMEOUT`).
  - Optional extras in `pyproject.toml`:
    - `dspy-code[openai]`, `dspy-code[anthropic]`, `dspy-code[gemini]`, `dspy-code[llm-all]`.
- **DSPy-Aware Code Generation**
  - Natural language → DSPy **Signatures**, **Modules**, and full **Programs**.
  - Support for major DSPy patterns: predictors, ChainOfThought, ReAct, RAG, etc.
  - Templates and examples for:
    - RAG systems
    - Question answering
    - Classification (e.g. sentiment analyzer)
    - Optimization/evaluation workflows
- **Validation & Execution**
  - `/validate` to check generated code against DSPy best practices and structure.
  - `/run` and `/test` to execute and test generated programs within a sandboxed engine.
  - Validation support for signatures, modules, predictors, adapters, metrics, and anti‑patterns.
- **GEPA Optimization**
  - End‑to‑end optimization workflows:
    - `/optimize` for one‑shot optimization scripts.
    - `/optimize-start`, `/optimize-status`, `/optimize-resume`, `/optimize-cancel` for long‑running GEPA jobs.
  - Integration with evaluation metrics (Accuracy, F1, ROUGE, BLEU, etc.).
  - Documentation and warnings about cloud costs and recommended hardware (32 GB RAM for heavy local optimization).
- **MCP (Model Context Protocol) Integration**
  - Built‑in MCP client with commands:
    - `/mcp-connect`, `/mcp-disconnect`, `/mcp-servers`, `/mcp-tools`, `/mcp-call`, `/mcp-resources`, `/mcp-read`, `/mcp-prompts`, `/mcp-prompt`.
  - Enables connecting DSPy Code to external tools and data sources.
- **Project & Session Management**
  - `/init` and `/project` for initializing and inspecting DSPy projects.
  - Codebase indexing and RAG support for answering questions about your own code.
  - Session management commands: `/sessions`, `/session`, `/history`, `/clear`, `/save-data`, export/import.
  - Export/import of sessions and packages for deployment via `/export` and `/import`.
- **Documentation & Examples**
  - Full docs site (MkDocs Material) with:
    - Getting Started (installation, quick start, first program, understanding DSPy Code).
    - Guides (model connection, interactive mode, natural language commands, optimization, project management, validation, slash commands).
    - Tutorials (RAG system, question answering, sentiment analyzer, GEPA optimization).
    - Reference (commands, configuration, templates, troubleshooting, FAQ, security).
  - Homepage and README aligned around DSPy Code as:
    - **Development assistant** (build DSPy apps quickly).
    - **Optimization engine** (real GEPA).
    - **Learning environment** for DSPy concepts.

### Changed
- Default Ollama generation timeout increased to 120 seconds to better support large models.
- Examples across README and docs updated to use modern models (e.g. `gpt-5-nano`, `claude-sonnet-4.5`, `gemini-2.5-flash`, `gpt-oss:120b`) and to recommend `/model` as the primary way to connect.
- Quick Start and model‑connection docs now make model connection mandatory and show clear virtual‑env + provider‑SDK installation flows using `dspy-code[...]` extras and `uv`/`pip`.
- Interactive UI improved with modern Rich versions and a `DSPY_CODE_SIMPLE_UI` mode for environments with limited emoji/spinner support.
- Natural language intent routing in interactive mode refined to:
  - Prefer natural‑language answers for questions.
  - Avoid double code generation and incorrect `/explain` follow‑ups.
- MkDocs navigation configuration tuned (tabs, sections) to keep the left nav stable and highlight the active page correctly.

### Fixed
- OpenAI deprecation issues (`APIRemovedInV1`) by migrating from `ChatCompletion` to the new client API, and removing unsupported `max_tokens`/`temperature` parameters for models like `gpt-5-nano`.
- Interactive mode errors:
  - `name 'explanations' is not defined` during `/explain`.
  - Syntax errors in `nl_command_router` debug logging.
- Ollama timeout handling for large models, with clearer error messages on connection/generation failures.
- Documentation glitches:
  - Stray `\n` in callouts.
  - Navigation behavior that caused pages to disappear or not highlight correctly.
