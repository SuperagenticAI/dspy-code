# Contributing to DSPy Code

Thank you for your interest in contributing to DSPy Code! We welcome contributions from the community.

**DSPy Code** is built by **[Superagentic AI](https://super-agentic.ai)** and is part of our commitment to open source leadership in the Agentic AI space.

---

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on [GitHub](https://github.com/superagentic-ai/dspy-code/issues) with:

- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, DSPy version)
- Any relevant error messages or logs

### Suggesting Features

We welcome feature suggestions! Please open an issue with:

- A clear description of the feature
- Use cases and examples
- Why this feature would be valuable
- Any implementation ideas (optional)

### Code Contributions

1. **Fork the repository**
   ```bash
   git clone https://github.com/superagentic-ai/dspy-code.git
   cd dspy-code
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

4. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed
   - Ensure all tests pass

5. **Test your changes**
   ```bash
   pytest tests/
   mkdocs build  # Verify documentation builds
   ```

6. **Commit your changes**
   ```bash
   git commit -m "Add: Description of your changes"
   ```

7. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

---

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and single-purpose

### Testing

- Write tests for new features
- Ensure existing tests still pass
- Aim for good test coverage

### Documentation

- Update relevant documentation pages
- Add examples for new features
- Keep documentation clear and beginner-friendly

### Commit Messages

Use clear, descriptive commit messages:

```
Add: Feature description
Fix: Bug description
Update: Change description
Refactor: Refactoring description
Docs: Documentation update
```

---

## Project Structure

```
dspy-code/
├── dspy_code/          # Main package
│   ├── commands/       # Slash command handlers
│   ├── core/           # Core functionality
│   ├── models/         # Code generation
│   ├── optimization/   # GEPA integration
│   ├── mcp/            # MCP client
│   ├── rag/            # Codebase RAG
│   └── ...
├── docs/               # Documentation
├── tests/              # Test suite
├── examples/           # Example scripts
└── pyproject.toml      # Project configuration
```

---

## Areas for Contribution

### High Priority

- Additional DSPy module templates
- Enhanced MCP tool integrations
- Performance optimizations
- Extended validation rules
- More evaluation metrics

### Documentation

- Tutorial improvements
- Code examples
- Best practices guides
- Video tutorials (external)

### Testing

- Additional test coverage
- Integration tests
- Performance benchmarks

---

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Be respectful and considerate
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Celebrate diverse perspectives

---

## Questions?

- **GitHub Issues**: [https://github.com/superagentic-ai/dspy-code/issues](https://github.com/superagentic-ai/dspy-code/issues)
- **Website**: [https://super-agentic.ai](https://super-agentic.ai)

---

## Recognition

Contributors will be recognized in:

- Release notes
- Project documentation
- GitHub contributors page

Thank you for helping make DSPy Code better! 🚀

---

**Built by [Superagentic AI](https://super-agentic.ai) - The Home of Agentic AI**
