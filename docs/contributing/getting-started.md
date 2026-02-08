# Developer Getting Started Guide

This guide helps you set up a development environment for contributing to DSPy Code.

## Prerequisites

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

## Setting Up the Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/SuperagenticAI/dspy-code.git
cd dspy-code
```

### 2. Create a Virtual Environment

Using uv (recommended):
```bash
uv venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

Using pip:
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

Using uv:
```bash
uv pip install -e ".[dev,test,docs]"
```

Using pip:
```bash
pip install -e ".[dev,test,docs]"
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

## Project Structure

```
dspy-code/
├── dspy_code/           # Main package
│   ├── commands/        # CLI commands
│   ├── core/            # Core infrastructure
│   ├── execution/       # Code execution
│   ├── mcp/             # MCP integration
│   ├── models/          # LLM and code generation
│   ├── rag/             # RAG system
│   ├── validation/      # Code validation
│   └── ui/              # User interface
├── tests/               # Test suite
├── docs/                # Documentation
└── examples/            # Example programs
```

## Running Tests

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_property_validators.py -v
```

### Run with Coverage

```bash
uv run pytest tests/ --cov=dspy_code --cov-report=html
```

### Run Property-Based Tests

```bash
uv run pytest tests/test_property_validators.py -v --hypothesis-show-statistics
```

## Code Quality

### Linting with Ruff

```bash
uv run ruff check dspy_code/
```

### Auto-fix Linting Issues

```bash
uv run ruff check --fix dspy_code/
```

### Format Code

```bash
uv run ruff format dspy_code/
```

### Type Checking with mypy

```bash
uv run mypy dspy_code/
```

## Building Documentation

### Serve Locally

```bash
uv run mkdocs serve
```

Then open http://localhost:8000 in your browser.

### Build Static Site

```bash
uv run mkdocs build
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the existing patterns
- Add docstrings to all public methods
- Add tests for new functionality

### 3. Run Tests and Linting

```bash
uv run pytest tests/ -v
uv run ruff check dspy_code/
uv run mypy dspy_code/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: description of your changes"
```

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Testing Guidelines

### Property-Based Tests

We use [Hypothesis](https://hypothesis.readthedocs.io/) for property-based testing. Each correctness property from the design document should have a corresponding test:

```python
# **Feature: feature-name, Property N: Property Name**
@given(...)
def test_property_name(self, ...):
    """
    Property N: Property Name
    
    Description of what this property tests.
    
    **Validates: Requirements X.Y**
    """
    # Test implementation
```

### Unit Tests

- Test specific examples and edge cases
- Use descriptive test names
- Group related tests in classes

## Architecture Overview

See the [Architecture Documentation](../reference/architecture.md) for a detailed overview of the system design.

## Key Components

### Configuration (`dspy_code/core/config.py`)

Manages project configuration with typed dataclasses.

### MCP Client (`dspy_code/mcp/`)

Handles Model Context Protocol integration for tool access.

### Validation (`dspy_code/validation/`)

Validates DSPy code for correctness and best practices.

### Code Generation (`dspy_code/models/`)

Generates DSPy components from task definitions.

## Getting Help

- Check the [FAQ](../reference/faq.md)
- Open an issue on [GitHub](https://github.com/SuperagenticAI/dspy-code/issues)
- Read the [Contributing Guide](../about/contributing.md)
