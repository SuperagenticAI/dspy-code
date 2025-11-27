# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Planned:
  - **Plan / Code modes** in interactive CLI (explicit "planning" vs "coding" flows for complex tasks).
  - First‑class support for **open‑source models via third‑party providers** (e.g. OpenRouter, Groq and similar gateways), alongside existing Ollama + cloud integrations.

### Changed
- Intent routing to further reduce/eliminate **duplicate code generation**, especially with large open‑source models and remote providers.

### Fixed
- TBC

---

## [0.1.1] - 2025-11-27

### Added
- **UV Support**: Full support for `uv` as an alternative to `python -m venv` for creating virtual environments. Documentation updated to recommend `uv` as the primary method.
- **Performance Toggles**: New `/fast-mode [on|off]`, `/disable-rag`, and `/enable-rag` commands for controlling RAG indexing and response speed. Performance settings now visible in welcome screen and `/status` command.
- **Venv Detection**: Automatic detection of virtual environment in project root with startup warnings if missing.

### Changed
- Welcome screen now displays RAG Mode and Fast Mode status with context-aware tips.
- Code execution prefers Python from project's `.venv/bin/python` when available.
- Documentation updated to recommend `uv` as the primary installation method.

---

## [0.1.0] - 2025-11-26

### Added
- **Interactive CLI**: Rich TUI with natural language interface for generating DSPy Signatures, Modules, and Programs. Core workflows: development (`/init` → generate → `/validate` → `/run`) and optimization (`/data` → `/optimize` → `/eval`).
- **Model Support**: Local Ollama models and cloud providers (OpenAI, Anthropic, Gemini) with interactive `/model` command for easy connection. SDK support via optional extras: `dspy-code[openai]`, `dspy-code[anthropic]`, `dspy-code[gemini]`, `dspy-code[llm-all]`.
- **Code Generation**: Natural language to DSPy code with support for major patterns (ChainOfThought, ReAct, RAG, etc.) and templates for common use cases.
- **Validation & Execution**: `/validate` for code checks, `/run` and `/test` for sandboxed execution.
- **GEPA Optimization**: End-to-end optimization workflows with `/optimize` commands and evaluation metrics integration.
- **MCP Integration**: Built-in MCP client for connecting to external tools and data sources.
- **Project Management**: `/init`, codebase indexing, RAG support, session management, and export/import functionality.
- **Documentation**: Complete docs site (MkDocs Material) with getting started guides, tutorials, and reference documentation.

### Changed
- Default Ollama timeout increased to 120 seconds for large models.
- Examples updated to use modern models (`gpt-5-nano`, `claude-sonnet-4.5`, `gemini-2.5-flash`).
- Interactive UI improved with Rich library and `DSPY_CODE_SIMPLE_UI` mode for limited emoji support.
- Natural language routing refined to prefer answers for questions and avoid duplicate code generation.

### Fixed
- OpenAI SDK migration to new client API, removed unsupported parameters for newer models.
- Interactive mode errors (`name 'explanations' is not defined`, syntax errors).
- Ollama timeout handling and error messages.
- Documentation formatting and navigation issues.
