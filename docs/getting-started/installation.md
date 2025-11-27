# Installation

Get DSPy Code up and running in just a few minutes!

## Requirements

Before installing DSPy Code, make sure you have:

- **Python 3.10 or higher** - Check your version with `python --version`
- **pip** - Python's package installer (comes with Python)

## Installation Steps

!!! warning "CRITICAL: Create Virtual Environment IN Your Project"
    **For security and isolation, ALWAYS create your virtual environment INSIDE your project directory!**

    This ensures:

    - 🔒 All file scanning stays within your project
    - 📦 Complete project isolation
    - 🚀 Easy sharing and deployment
    - 🧹 Clean removal (just delete the project folder)

### Step 1: Create Your Project Directory

```bash
# Create a dedicated directory for your DSPy project
mkdir my-dspy-project
cd my-dspy-project
```

### Step 2: Create Virtual Environment IN This Directory

=== "uv (Recommended)"

    ```bash
    # Create .venv INSIDE your project directory (not elsewhere!)
    uv venv

    # Activate it
    # For bash/zsh (macOS/Linux):
    source .venv/bin/activate
    # For fish shell:
    source .venv/bin/activate.fish
    # On Windows:
    .venv\Scripts\activate
    ```

=== "python -m venv"

    ```bash
    # Create .venv INSIDE your project directory (not elsewhere!)
    python -m venv .venv

    # Activate it
    # For bash/zsh (macOS/Linux):
    source .venv/bin/activate
    # For fish shell:
    source .venv/bin/activate.fish
    # On Windows:
    .venv\Scripts\activate
    ```

!!! tip "Why uv?"
    `uv` is a fast Python package manager written in Rust. It's 10-100x faster than pip and provides better dependency resolution. [Learn more about uv](https://docs.astral.sh/uv/)

!!! success "Why .venv in the Project?"
    When you create the virtual environment inside your project:

    - All packages install to `my-dspy-project/.venv/`
    - All dspy-code data goes to `my-dspy-project/.dspy_code/`
    - Everything stays in one place!

    **Result**: One directory = one complete project

### Step 3: Install DSPy Code

=== "uv (Recommended)"

    ```bash
    # This installs into .venv/ in your project
    uv pip install --upgrade dspy-code

    # Or add it to your project dependencies (pyproject.toml) in one step
    uv add dspy-code
    ```

=== "pip"

    ```bash
    # This installs into .venv/ in your project
    pip install --upgrade dspy-code
    ```

That's it! DSPy Code is now installed in your project.

### Step 4: Install DSPy (Optional)

DSPy Code will install DSPy automatically if needed, but you can install/upgrade it explicitly:

!!! tip "Use the same tool you used for venv"
    If you created your venv with `uv venv`, use `uv pip install` for consistency. If you used `python -m venv`, use `pip install`.

=== "uv (Recommended)"

    ```bash
    uv pip install --upgrade dspy
    ```

=== "pip"

    ```bash
    pip install --upgrade dspy
    ```

!!! info "DSPy Version"
    DSPy Code adapts to YOUR installed DSPy version and indexes it for accurate code generation and Q&A.

## Verify Installation

Check that everything is installed correctly:

```bash
# Make sure you're in your project directory
cd my-dspy-project

# Activate your virtual environment if not already active
source .venv/bin/activate  # For fish: source .venv/bin/activate.fish

# Check DSPy Code
dspy-code --help

# You should see:
# Usage: dspy-code [OPTIONS]
# DSPy Code - Interactive DSPy Development Environment
```

If you see the help text, you're all set! 🎉

## Your Project Structure

After installation, your project looks like this:

```
my-dspy-project/          # Your project root
├── .venv/                # Virtual environment (packages here!)
│   ├── bin/
│   ├── lib/
│   │   └── python3.x/
│   │       └── site-packages/
│   │           ├── dspy/          # DSPy package
│   │           └── dspy_code/     # dspy-code package
│   └── ...
└── (your files will be created by dspy-code)
```

**When you run `/init`, dspy-code will create:**

```
my-dspy-project/
├── .venv/                # Your packages (already created)
├── .dspy_cache/          # DSPy's LLM response cache
├── .dspy_code/           # dspy-code's internal data
│   ├── cache/            # RAG index cache
│   ├── sessions/         # Session state
│   ├── optimization/     # GEPA workflows
│   └── exports/          # Export history
├── generated/            # Your generated code
├── modules/              # Your modules
├── signatures/           # Your signatures
└── dspy_config.yaml      # Your configuration
```

**Everything in one place!** 📦

## Optional Dependencies

DSPy Code has optional dependencies for different features. Install only what you need.

### Cloud Model Providers (via dspy-code extras)

Use extras so versions stay aligned with dspy-code's tested matrix.

!!! tip "Use the same tool you used for venv"
    If you created your venv with `uv venv`, use `uv pip install` for consistency. If you used `python -m venv`, use `pip install`.

=== "uv (Recommended)"

    ```bash
    # OpenAI support
    uv pip install "dspy-code[openai]"

    # Google Gemini support
    uv pip install "dspy-code[gemini]"

    # Anthropic (paid key required)
    uv pip install "dspy-code[anthropic]"

    # Or install all cloud providers at once
    uv pip install "dspy-code[llm-all]"
    ```

=== "pip"

    ```bash
    # OpenAI support
    pip install "dspy-code[openai]"

    # Google Gemini support
    pip install "dspy-code[gemini]"

    # Anthropic (paid key required)
    pip install "dspy-code[anthropic]"

    # Or install all cloud providers at once
    pip install "dspy-code[llm-all]"
    ```

> **Note:** Anthropic has discontinued free API keys. DSPy Code fully supports Claude **if you already have a paid API key**, but Anthropic integration will simply not work without one.

### Semantic Similarity Metrics

```bash
pip install sentence-transformers scikit-learn
```

!!! tip "Install as Needed"
    Don't worry about installing these now. DSPy Code will tell you if you need something and show you exactly how to install it!

## Troubleshooting

### "command not found: dspy-code"

If you see this error:

```bash
# Make sure your virtual environment is activated
source .venv/bin/activate  # For fish: source .venv/bin/activate.fish

# Verify installation
pip list | grep dspy-code

# If not installed, install it
pip install dspy-code
```

### Running from Wrong Directory

If you see security warnings when starting dspy-code:

```
🚨 SECURITY WARNING
You are running dspy-code from your home directory!
```

**Solution**: Always run from your project directory:

```bash
cd my-dspy-project
source .venv/bin/activate  # For fish: source .venv/bin/activate.fish
dspy-code
```

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

### Virtual Environment Outside Project

If you created the venv outside your project:

```bash
# Wrong way:
cd ~/
python -m venv my_venv  # ❌ Don't do this!

# Right way:
cd ~/my-dspy-project
python -m venv .venv     # ✅ Do this!
```

### Permission Denied

If you get permission errors, **don't use --user or sudo**. Use a virtual environment:

```bash
cd my-dspy-project
python -m venv .venv
source .venv/bin/activate  # For fish: source .venv/bin/activate.fish
pip install dspy-code
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

# Set working directory
WORKDIR /project

# Create virtual environment in the project
RUN python -m venv .venv

# Activate venv and install
RUN . .venv/bin/activate && \
    pip install dspy-code dspy

# Run with venv activated
CMD [".venv/bin/dspy-code"]
```

Build and run:

```bash
docker build -t dspy-code .
docker run -it -v $(pwd):/project dspy-code
```

This mounts your current directory as `/project` in the container!

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
