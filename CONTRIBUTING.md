# Contributing to DSPy Code

Thank you for considering contributing to DSPy Code! 🎉

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to team@super-agentic.ai.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [issue tracker](https://github.com/SuperagenticAI/dspy-code/issues) to avoid duplicates. When creating a bug report, include:

* Clear and descriptive title
* Exact steps to reproduce the problem
* Expected vs actual behavior
* Screenshots (if applicable)
* Environment details (OS, Python version, DSPy version)

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/SuperagenticAI/dspy-code/issues). Please include:

* Clear and descriptive title
* Step-by-step description of the enhancement
* Specific examples
* Why this enhancement would be useful

### Pull Requests

We welcome pull requests! For major changes, please open an issue first to discuss what you would like to change.

## Development Setup

### Prerequisites

* Python 3.10 or higher
* [uv](https://github.com/astral-sh/uv) (recommended) or pip
* Git

### Quick Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/YOUR-USERNAME/dspy-code.git
cd dspy-code
```

2. **Create virtual environment and install dependencies**

Using uv (recommended):
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev,test,docs]"
```

Or using pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev,test,docs]"
```

3. **Install pre-commit hooks**

```bash
pre-commit install
```

4. **Verify setup**

```bash
# Run tests
pytest

# Run linter
ruff check .

# Run formatter
ruff format .
```

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bugfix-name
```

### 2. Make Your Changes

Follow our coding standards (see below).

### 3. Add Tests

Write tests for new features and bug fixes.

```bash
pytest tests/ -v --cov=dspy_code
```

### 4. Format and Lint

```bash
ruff check --fix .
ruff format .
```

### 5. Commit

Use [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update documentation"
```

Commit types:
* `feat:` - New features
* `fix:` - Bug fixes
* `docs:` - Documentation
* `style:` - Formatting
* `refactor:` - Code restructuring
* `test:` - Tests
* `chore:` - Maintenance

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python Style

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting:

* Line length: 100 characters
* Use type hints for function signatures
* Write docstrings for public functions, classes, and modules
* Follow PEP 8 conventions
* Use meaningful variable and function names

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of what the function does.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When parameter is invalid.
    """
    pass
```

### Import Organization

Organize imports in three groups (Ruff does this automatically):

1. Standard library imports
2. Third-party imports
3. Local application imports

## Testing

### Writing Tests

* Write tests for all new features and bug fixes
* Use descriptive test names: `test_feature_behavior_under_condition`
* Use pytest fixtures for setup/teardown
* Aim for >80% test coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dspy_code --cov-report=html

# Run specific test
pytest tests/test_specific_file.py

# Run in parallel
pytest -n auto
```

## Documentation

Documentation will be available on GitHub Pages once set up.

For now, refer to:
- README.md for overview and quick start
- Code docstrings for API documentation
- Examples in `examples/` directory

## Project Structure

```
dspy-code/
├── dspy_code/          # Main package
│   ├── commands/       # CLI commands
│   ├── core/          # Core functionality
│   ├── models/        # LLM integration
│   ├── validation/    # Code validation
│   └── ...
├── tests/             # Test suite
├── docs/              # Documentation
└── examples/          # Example scripts
```

## Getting Help

* 🐛 [Issue Tracker](https://github.com/SuperagenticAI/dspy-code/issues) - Report bugs
* 📧 Email: team@super-agentic.ai

## Maintainer

* [@Shashikant86](https://github.com/Shashikant86) - Lead Maintainer

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to DSPy Code!** 🚀
