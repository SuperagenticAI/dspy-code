# Quick Start

Get started with DSPy Code in 5 minutes! This guide will walk you through creating your first DSPy program.

## Step 1: Start the CLI

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

## Step 2: Initialize Your Project

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

## Step 3: Generate Your First Program

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

## Step 4: Save Your Code

Save the generated code to a file:

```
/save sentiment.py
```

The file will be saved to your `generated/` directory.

!!! success "Saved!"
    ```
    ✓ Code saved to: generated/sentiment.py
    ```

## Step 5: Validate Your Code

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

## Step 6: Run Your Program

Test your program:

```
/run
```

DSPy Code will execute your code in a safe sandbox and show you the results.

## That's It!

You just:

1. ✅ Started DSPy Code
2. ✅ Initialized a project
3. ✅ Generated a DSPy program
4. ✅ Saved it to a file
5. ✅ Validated the code
6. ✅ Ran it successfully

## What's Next?

### Connect a Model (Optional but Recommended)

For better code generation, connect to an LLM:

```
/connect ollama llama3.1:8b
```

Or use OpenAI:

```
/connect openai gpt-4
```

!!! info "Why Connect a Model?"
    Without a model, DSPy Code uses templates. With a model, it can understand your specific requirements and generate more customized code!

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
