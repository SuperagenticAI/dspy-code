# Changelog

All notable changes to DSPy Code will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2025-11-21

### Added

- Initial release of DSPy Code (formerly DSPy CLI)
- Interactive mode with natural language interface
- Slash commands for all operations
- Code generation for Signatures, Modules, and complete programs
- Model connection support (Ollama, OpenAI, Anthropic, Gemini)
- Built-in MCP client integration
- Real GEPA optimization support
- Codebase RAG for project understanding
- Code validation and sandboxed execution
- Project initialization (fresh and existing projects)
- Session management with auto-save
- Export/import functionality
- Comprehensive documentation with MkDocs

### Changed

- Renamed from "DSPy CLI" to "DSPy Code" with tagline "Claude Code for DSPy"
- Updated branding to Superagentic AI
- Made all commands interactive-only (slash commands)
- Moved codebase indexing to `/init` command
- Enhanced error handling and user feedback

### Fixed

- Context sharing between interactive session and slash commands
- Codebase indexing to use installed packages instead of reference directory
- Permission handling for restricted environments
- Model connection error messages

---

## [Unreleased]

### Planned

- Enhanced MCP tool integration
- Additional DSPy module templates
- Improved optimization workflows
- Extended evaluation capabilities
- Performance optimizations

---

**For detailed development history, see [GitHub Commits](https://github.com/superagentic-ai/dspy-code/commits/main)**
