"""
Demo of the beautiful DSPy Code UI/UX.

This script demonstrates the enhanced UI components.
"""

import time

from dspy_cli.ui.animations import ThinkingAnimation, get_random_thinking_message
from dspy_cli.ui.prompts import (
    show_assistant_header,
    show_code_panel,
    show_error_message,
    show_info_message,
    show_next_steps,
    show_success_message,
    show_warning_message,
)

# Import UI components
from dspy_cli.ui.welcome import show_welcome_screen
from rich.console import Console

console = Console()


def demo_welcome_screen():
    """Demo the welcome screen."""
    print("\n" + "=" * 70)
    print("DEMO 1: Welcome Screen")
    print("=" * 70 + "\n")

    show_welcome_screen("gpt-4")

    input("\nPress Enter to continue to next demo...")


def demo_animations():
    """Demo the thinking animations."""
    console.clear()
    print("\n" + "=" * 70)
    print("DEMO 2: Thinking Animations")
    print("=" * 70 + "\n")

    console.print("[bold]Demonstrating various thinking messages:[/bold]\n")

    for i in range(5):
        message = get_random_thinking_message()
        with ThinkingAnimation(message):
            time.sleep(1.5)
        console.print(f"  ✓ Completed: {message}\n")

    input("\nPress Enter to continue to next demo...")


def demo_messages():
    """Demo different message types."""
    console.clear()
    print("\n" + "=" * 70)
    print("DEMO 3: Message Types")
    print("=" * 70 + "\n")

    console.print("[bold]Different message styles:[/bold]\n")

    show_success_message("Operation completed successfully!")
    console.print()

    show_info_message("Here's some helpful information")
    console.print()

    show_warning_message("Please be careful with this action")
    console.print()

    show_error_message("Something went wrong")
    console.print()

    input("\nPress Enter to continue to next demo...")


def demo_code_display():
    """Demo code display."""
    console.clear()
    print("\n" + "=" * 70)
    print("DEMO 4: Code Display")
    print("=" * 70 + "\n")

    sample_code = '''import dspy

class SentimentAnalysis(dspy.Signature):
    """Analyze the sentiment of text."""

    text = dspy.InputField(desc="The text to analyze")
    sentiment = dspy.OutputField(desc="positive, negative, or neutral")
    confidence = dspy.OutputField(desc="Confidence score 0-1")


class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentAnalysis)

    def forward(self, text):
        return self.predictor(text=text)
'''

    show_assistant_header()

    with ThinkingAnimation("✨ Crafting your DSPy module..."):
        time.sleep(2)

    show_code_panel(sample_code, "Generated DSPy Module (Chain of Thought)", "python")

    show_success_message("Module created successfully!")

    show_next_steps(
        [
            "Type [cyan]save sentiment_analyzer.py[/cyan] to save this code",
            "Ask me to [green]add more features[/green]",
            "Request [yellow]optimizations[/yellow]",
        ]
    )

    input("\nPress Enter to continue to next demo...")


def demo_complete_interaction():
    """Demo a complete interaction flow."""
    console.clear()
    print("\n" + "=" * 70)
    print("DEMO 5: Complete Interaction Flow")
    print("=" * 70 + "\n")

    console.print("[bold cyan]Simulating a complete user interaction:[/bold cyan]\n")

    # User request
    console.print("[bold]You:[/bold] Create a signature for email classification\n")

    # Processing
    with ThinkingAnimation("🔍 Analyzing your requirements..."):
        time.sleep(1.5)

    show_assistant_header()
    console.print("I'll help you create a DSPy Signature! Let me extract the details...\n")

    with ThinkingAnimation("✨ Crafting your DSPy signature..."):
        time.sleep(1.5)

    # Show result
    sample_signature = '''import dspy

class EmailClassification(dspy.Signature):
    """Classify emails by priority."""

    subject = dspy.InputField(desc="Email subject line")
    body = dspy.InputField(desc="Email body content")
    priority = dspy.OutputField(desc="urgent, normal, or low")
'''

    show_code_panel(sample_signature, "Generated DSPy Signature", "python")

    show_success_message("Signature created successfully!")

    show_next_steps(
        [
            "Type [cyan]save email_signature.py[/cyan] to save",
            "Ask me to [green]create a module[/green] using this",
            "Request [yellow]modifications[/yellow]",
        ]
    )

    console.print("\n[dim]This is what the actual CLI interaction looks like![/dim]\n")


def main():
    """Run all demos."""
    console.print("\n[bold magenta]DSPy Code UI/UX Demo[/bold magenta]")
    console.print("[dim]Showcasing the beautiful, Claude-like interface[/dim]\n")

    demos = [
        ("Welcome Screen", demo_welcome_screen),
        ("Thinking Animations", demo_animations),
        ("Message Types", demo_messages),
        ("Code Display", demo_code_display),
        ("Complete Interaction", demo_complete_interaction),
    ]

    for i, (name, demo_func) in enumerate(demos, 1):
        try:
            demo_func()
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Demo interrupted. Exiting...[/yellow]\n")
            break

    console.clear()
    console.print("\n[bold green]✨ Demo Complete! ✨[/bold green]\n")
    console.print("The DSPy Code now features:")
    console.print("  ✓ Beautiful ASCII art welcome screen")
    console.print("  ✓ Animated thinking indicators")
    console.print("  ✓ Styled message types")
    console.print("  ✓ Syntax-highlighted code panels")
    console.print("  ✓ Helpful next steps suggestions")
    console.print()
    console.print("[bold cyan]Try it yourself:[/bold cyan]")
    console.print("  $ dspy-cli")
    console.print()


if __name__ == "__main__":
    main()
