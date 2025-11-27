# Quick Start

Get started with DSPy Code in 5 minutes! This guide will walk you through creating your first DSPy program.

## Prerequisites (One‑Time Setup)

You only need to do this once for each new DSPy project.

```bash
# 1. Create a project directory
mkdir my-dspy-project
cd my-dspy-project

# 2. Create a virtual environment INSIDE this directory
# Recommended: Use uv (faster and more reliable)
uv venv

# Alternative: Use standard Python venv
# python -m venv .venv

# 3. Activate the virtual environment
# For bash/zsh (macOS/Linux):
source .venv/bin/activate
# For fish:
source .venv/bin/activate.fish
# On Windows:
.venv\Scripts\activate

# 4. Install dspy-code (always upgrade for latest features)
# Recommended: Use uv
uv pip install --upgrade dspy-code

# Alternative: Use pip
# pip install --upgrade dspy-code

# 5. (Optional but recommended) Install provider SDKs via dspy-code extras

# If you ONLY want local models (Ollama), you can skip this step.

# If using uv (recommended):
uv pip install "dspy-code[openai]"      # OpenAI support
uv pip install "dspy-code[gemini]"     # Google Gemini support
uv pip install "dspy-code[anthropic]"  # Anthropic (paid key required)
uv pip install "dspy-code[llm-all]"   # Or install all cloud providers at once

# If using pip:
# pip install "dspy-code[openai]"
# pip install "dspy-code[gemini]"
# pip install "dspy-code[anthropic]"
# pip install "dspy-code[llm-all]"
```

For more details, see the [Installation Guide](installation.md).

## Step 1: Navigate to Your Project

```bash
# Go to your project directory
cd my-dspy-project

# Activate your virtual environment
# For bash/zsh (macOS/Linux):
source .venv/bin/activate
# For fish shell:
source .venv/bin/activate.fish
# On Windows:
.venv\Scripts\activate
```

!!! tip "Always Activate Your Venv"
    Make sure your virtual environment is activated before running dspy-code. You should see `(.venv)` in your terminal prompt.

## Step 2: Start the CLI

Open your terminal and run:

```bash
dspy-code
```

You'll see a beautiful welcome screen with the DSPy version and helpful tips.

!!! success "What You'll See"
    ```
    ✓ DSPy Version: 3.0.4

    ╔══════════════════════════════════════╗
    ║   DSPy Code - Interactive Mode        ║
    ╚══════════════════════════════════════╝

    💡 Get Started:
      /init     - Initialize your project
      /demo     - See it in action
      /help     - View all commands

    💬 Or just describe what you want to build!
    ```

## Step 3: Connect a Model (Required)

Before you do anything else in the CLI, you **must connect to a model**. DSPy Code relies on an LLM for code generation and understanding.

**Easiest (recommended): use the interactive selector**

```bash
/model
```

This lets you:

- Choose **Ollama** local models from a numbered list
- Choose a **cloud provider** (OpenAI, Anthropic, Gemini) and then type a model name (for example `gpt-5-nano`, `claude-sonnet-4.5`, `gemini-2.5-flash`)

**Direct connect (advanced users):**

```bash
# Ollama (local, free)
/connect ollama gpt-oss:120b

# Or OpenAI (example small model)
/connect openai gpt-5-nano

# Or Google Gemini (example model)
/connect gemini gemini-2.5-flash
```

> 💡 **Tip:** These are just starting points. Use the latest models your account supports (for example gpt‑4o / gpt‑5 family, Gemini 2.5, latest Claude Sonnet/Opus) for best quality.

!!! warning "Cloud Cost & Optimization"
    - When you're connected to **cloud providers** (OpenAI, Anthropic, Gemini), remember that API usage is **billed per token**.
    - GEPA **optimization** (via `/optimize` or generated optimization scripts) can make a *lot* of LLM calls. Only run optimization if you understand the potential cost and have quotas/billing configured.
    - For local optimization runs with larger models, we recommend at least **32 GB RAM**.
    - For more details, see [Model Connection (Cloud & Local)](../guide/model-connection.md) and the [Optimization Guide](../guide/optimization.md).

## Step 4: Initialize Your Project

Inside the CLI, type:

```
/init
```

This will:

- Create a `dspy_config.yaml` file
- Set up project directories
- Index your code for intelligent Q&A (with entertaining jokes!)

!!! tip "What's Happening?"
    The `/init` command scans your installed DSPy version and your project code. This lets DSPy Code answer questions about DSPy and understand your project!

## Step 5: Generate Your First Program

Now for the fun part! Just describe what you want in plain English:

```
Create a sentiment analyzer that takes text and outputs positive or negative
```

DSPy Code will:

1. Understand your request
2. Generate a complete DSPy program
3. Show you the code with syntax highlighting
4. Give you next steps

!!! example "What You'll Get"
    ```python
    import dspy

    class SentimentSignature(dspy.Signature):
        """Analyze the sentiment of text."""
        text: str = dspy.InputField(desc="Text to analyze")
        sentiment: str = dspy.OutputField(desc="positive or negative")

    class SentimentAnalyzer(dspy.Module):
        def __init__(self):
            super().__init__()
            self.predictor = dspy.ChainOfThought(SentimentSignature)

        def forward(self, text):
            return self.predictor(text=text)
    ```

## Step 6: Save Your Code

Save the generated code to a file:

```
/save sentiment.py
```

The file will be saved to your `generated/` directory.

!!! success "Saved!"
    ```
    ✓ Code saved to: generated/sentiment.py
    ```

## Step 7: Validate Your Code

Check if your code follows DSPy best practices:

```
/validate
```

DSPy Code will check for:

- Correct Signature usage
- Proper Module structure
- Best practices
- Potential issues

!!! tip "Quality Checks"
    The validator catches common mistakes and suggests improvements. It's like having an expert review your code!

## Step 8: Run Your Program

Test your program:

```
/run
```

DSPy Code will execute your code in a safe sandbox and show you the results.

## That's It!

You just:

1. ✅ Started DSPy Code
2. ✅ Connected a model
3. ✅ Initialized a project
4. ✅ Generated a DSPy program
5. ✅ Saved it to a file
6. ✅ Validated the code
7. ✅ Ran it successfully

## What's Next?

!!! info "Why Model Connection is Required"
    DSPy Code needs an LLM to understand your requests and generate DSPy code. Without a connected model, most interactive features will not work.

### Try More Examples

See what else you can build:

```
/demo
```

This shows you complete example programs you can learn from.

### Explore Commands

See all available commands:

```
/help
```

### Ask Questions

DSPy Code can answer questions about DSPy:

```
How do Signatures work?
```

```
Show me a ChainOfThought example
```

## Common First Tasks

### Build a Question Answering System

```
Create a QA system that takes a question and context and returns an answer
```

### Create a Text Classifier

```
Build a classifier for email categories: work, personal, or spam
```

### Make a Summarizer

```
Generate a summarizer that takes long text and outputs a brief summary
```

## Tips for Beginners

!!! tip "Natural Language Works!"
    You don't need to know DSPy syntax. Just describe what you want in plain English:

    - "Create a sentiment analyzer"
    - "Build a question answering system"
    - "Make a text classifier for emails"

!!! tip "Use /status to Check"
    Not sure if your code was saved? Use `/status` to see what's in your session:
    ```
    /status
    ```

!!! tip "Save Often"
    After generating code you like, save it immediately:
    ```
    /save my_program.py
    ```

!!! tip "Validate Before Running"
    Always validate your code before running:
    ```
    /validate
    /run
    ```

## Troubleshooting

### CLI Won't Start

```bash
# Make sure it's installed
pip install dspy-code

# Try running with python -m
python -m dspy_code
```

### No Code Generated

1. Check if you described your task clearly
2. Try connecting a model: `/connect ollama llama3.1:8b`
3. Or use templates: `/examples`

### Can't Save Code

1. Check if code was generated: `/status`
2. Make sure you specify a filename: `/save myfile.py`
3. Check directory permissions

## Next Steps

Now that you've created your first program, learn more:

<div class="grid cards" markdown>

-   **📖 Understanding DSPy Code**

    Learn how DSPy Code works under the hood

    [Learn More →](understanding.md)

-   **🎨 Interactive Mode**

    Master all the slash commands

    [View Guide →](../guide/interactive-mode.md)

-   **📝 First Program Tutorial**

    Build a complete project step by step

    [Start Tutorial →](first-program.md)

-   **🚀 Generating Code**

    Learn all the ways to generate DSPy code

    [Read Guide →](../guide/generating-code.md)

</div>

---

**Ready to build something amazing?** Let's dive deeper!

[First Program Tutorial →](first-program.md){ .md-button .md-button--primary }
