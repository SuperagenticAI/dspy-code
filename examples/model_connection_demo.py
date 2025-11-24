"""
Demo of Model Connection System.

Shows how to connect to models and use them for intelligent code generation.
"""

from rich.console import Console
from rich.panel import Panel

console = Console()


def show_demo():
    """Show model connection demo."""

    console.print("\n[bold magenta]DSPy Code Model Connection Demo[/bold magenta]\n")

    # Demo 1: Slash Commands
    console.print("[bold cyan]1. Slash Commands[/bold cyan]\n")

    commands = [
        ("/connect ollama llama2", "Connect to local Ollama model"),
        ("/connect openai gpt-4", "Connect to OpenAI GPT-4"),
        ("/models", "List all available models"),
        ("/models ollama", "List only Ollama models"),
        ("/status", "Check connection status"),
        ("/reference signature", "View DSPy signature examples"),
        ("/disconnect", "Disconnect from current model"),
        ("/help", "Show all commands"),
    ]

    for cmd, desc in commands:
        console.print(f"  [yellow]{cmd:30}[/yellow] - {desc}")

    console.print()

    # Demo 2: Connection Flow
    console.print("[bold cyan]2. Connection Flow Example[/bold cyan]\n")

    flow = """
[bold]Step 1: Start Ollama[/bold]
$ ollama serve

[bold]Step 2: Pull a model[/bold]
$ ollama pull llama2

[bold]Step 3: Start DSPy Code[/bold]
$ dspy-cli

[bold]Step 4: Connect to model[/bold]
You: /connect ollama llama2
✓ Connected to llama2!

[bold]Step 5: Make a request[/bold]
You: Create a signature for email classification

[dim]CLI Process:[/dim]
1. Loads DSPy signature reference docs
2. Sends to llama2 with context
3. Generates accurate DSPy code
4. Validates and displays

[bold green]Result: Perfect DSPy signature code![/bold green]
"""

    panel = Panel(flow, border_style="cyan", padding=(1, 2))
    console.print(panel)
    console.print()

    # Demo 3: Supported Models
    console.print("[bold cyan]3. Supported Models[/bold cyan]\n")

    models = {
        "Local (Ollama)": [
            "llama2 - General purpose, free",
            "mistral - Fast and capable",
            "codellama - Best for code generation",
            "mixtral - Advanced reasoning",
        ],
        "Cloud (OpenAI)": [
            "gpt-4 - Most capable",
            "gpt-4-turbo - Fast and capable",
            "gpt-3.5-turbo - Fast and cheap",
        ],
        "Cloud (Anthropic)": [
            "claude-3-opus - Most capable",
            "claude-3-sonnet - Balanced",
            "claude-3-haiku - Fast and cheap",
        ],
        "Cloud (Google)": ["gemini-pro - General purpose", "gemini-pro-vision - With images"],
    }

    for category, model_list in models.items():
        console.print(f"[bold]{category}:[/bold]")
        for model in model_list:
            console.print(f"  • {model}")
        console.print()

    # Demo 4: Benefits
    console.print("[bold cyan]4. Why Connect a Model?[/bold cyan]\n")

    benefits = """
[bold green]With Model Connection:[/bold green]
✓ Understands complex natural language requests
✓ Generates accurate, context-aware DSPy code
✓ Uses actual DSPy patterns from reference docs
✓ Adapts to your specific requirements
✓ Provides explanations and suggestions
✓ Learns from conversation history

[bold yellow]Without Model Connection:[/bold yellow]
✗ Limited to basic templates
✗ Generic code generation
✗ No understanding of nuances
✗ No adaptation to context
"""

    console.print(benefits)
    console.print()

    # Demo 5: Quick Start
    console.print("[bold cyan]5. Quick Start[/bold cyan]\n")

    quickstart = """
[bold]Option 1: Free with Ollama[/bold]
$ ollama pull llama2
$ dspy-cli
/connect ollama llama2

[bold]Option 2: Cloud with OpenAI[/bold]
$ export OPENAI_API_KEY=sk-your-key
$ dspy-cli
/connect openai gpt-4

[bold]Then start creating:[/bold]
You: Create a signature for sentiment analysis
You: Build a module using chain of thought
You: Generate a complete email classifier
"""

    panel = Panel(quickstart, border_style="green", padding=(1, 2))
    console.print(panel)
    console.print()

    # Demo 6: Documentation
    console.print("[bold cyan]6. Learn More[/bold cyan]\n")

    console.print("📚 [bold]Documentation:[/bold]")
    console.print("  • docs/MODEL_CONNECTION_GUIDE.md - Complete setup guide")
    console.print("  • MODEL_INTEGRATION_SUMMARY.md - Technical overview")
    console.print("  • /help in CLI - Interactive help")
    console.print()

    console.print("🚀 [bold]Try it now:[/bold]")
    console.print("  $ dspy-cli")
    console.print("  /connect ollama llama2")
    console.print('  "Create a signature for text classification"')
    console.print()


if __name__ == "__main__":
    show_demo()
