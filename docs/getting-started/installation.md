# Installation

Get DSPy Code up and running in just a few minutes!

## Requirements

Before installing DSPy Code, make sure you have:

- **Python 3.10 or higher** - Check your version with `python --version`
- **pip** - Python's package installer (comes with Python)

!!! tip "Using Virtual Environments"
    We recommend using a virtual environment to keep your projects isolated:
    ```bash
    python -m venv dspy-env
    source dspy-env/bin/activate  # On Windows: dspy-env\Scripts\activate
    ```

## Install DSPy Code

### From PyPI (Recommended)

The easiest way to install DSPy Code:

```bash
pip install dspy-code
```

That's it! DSPy Code is now installed.

### From Source

If you want the latest development version:

```bash
# Clone the repository
git clone https://github.com/superagentic-ai/dspy-code.git
cd dspy-code

# Install in development mode
pip install -e .
```

## Install DSPy

DSPy Code requires DSPy to be installed. If you don't have it yet:

```bash
pip install dspy
```

!!! info "DSPy Version"
    DSPy Code works with any DSPy version (2.x, 3.x, or newer). It adapts to YOUR installed version!

## Verify Installation

Check that everything is installed correctly:

```bash
# Check DSPy Code
dspy-code --help

# You should see:
# Usage: dspy-code [OPTIONS]
# DSPy Code - Interactive DSPy Development Environment
```

If you see the help text, you're all set! 🎉

## Optional Dependencies

DSPy Code has optional dependencies for different features. Install only what you need:

### For OpenAI Models

```bash
pip install openai
```

### For Anthropic Claude

```bash
pip install anthropic
```

### For Google Gemini

```bash
pip install google-generativeai
```

### For Semantic Similarity Metrics

```bash
pip install sentence-transformers scikit-learn
```

!!! tip "Install as Needed"
    Don't worry about installing these now. DSPy Code will tell you if you need something and show you exactly how to install it!

## Troubleshooting

### Python Version Too Old

If you see an error about Python version:

```bash
# Check your Python version
python --version

# If it's less than 3.10, upgrade Python:
# - On macOS: brew install python@3.11
# - On Ubuntu: sudo apt install python3.11
# - On Windows: Download from python.org
```

### pip Not Found

If `pip` is not found:

```bash
# Try python -m pip instead
python -m pip install dspy-code
```

### Permission Denied

If you get permission errors:

```bash
# Use --user flag
pip install --user dspy-code

# Or use a virtual environment (recommended)
python -m venv myenv
source myenv/bin/activate
pip install dspy-code
```

### DSPy Not Found

If DSPy Code can't find DSPy:

```bash
# Make sure DSPy is installed
pip install dspy

# Check it's installed
python -c "import dspy; print(dspy.__version__)"
```

## Next Steps

Now that you have DSPy Code installed, let's run it!

[Quick Start Guide →](quick-start.md){ .md-button .md-button--primary }

## System-Specific Notes

### macOS

DSPy Code works great on macOS. If you use Homebrew:

```bash
# Install Python (if needed)
brew install python@3.11

# Install DSPy Code
pip3 install dspy-code
```

### Linux

On Ubuntu/Debian:

```bash
# Install Python (if needed)
sudo apt update
sudo apt install python3.11 python3-pip

# Install DSPy Code
pip3 install dspy-code
```

### Windows

On Windows, use PowerShell or Command Prompt:

```powershell
# Install DSPy Code
pip install dspy-code

# Run it
dspy-code
```

!!! tip "Windows Terminal"
    For the best experience on Windows, use Windows Terminal with PowerShell. The colors and formatting will look much better!

## Docker

Want to run DSPy Code in Docker?

```dockerfile
FROM python:3.11-slim

# Install DSPy Code
RUN pip install dspy-code dspy

# Run it
CMD ["dspy-code"]
```

Build and run:

```bash
docker build -t dspy-code .
docker run -it dspy-code
```

## Upgrading

To upgrade to the latest version:

```bash
pip install --upgrade dspy-code
```

## Uninstalling

If you need to uninstall:

```bash
pip uninstall dspy-code
```

---

**Installation complete!** Let's start using DSPy Code.

[Quick Start Guide →](quick-start.md){ .md-button .md-button--primary }
