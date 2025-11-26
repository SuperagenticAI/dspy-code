"""
Enhanced animations and loading indicators for DSPy Code.
Inspired by Claude Code's engaging animation system.
"""

import os
import random
import threading
import time

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.text import Text

# Allow users to disable emoji-heavy UI if their terminal/font doesn't support it well.
SIMPLE_UI = os.getenv("DSPY_CODE_SIMPLE_UI", "").lower() in {"1", "true", "yes", "on"}

console = Console()


def create_safe_spinner(spinner_name: str, text: str = "", style: str = "cyan") -> Spinner:
    """
    Safely create a Rich Spinner with fallback to 'dots' if spinner name is invalid.

    This ensures compatibility across different Rich versions and PyPI installations.

    Args:
        spinner_name: Name of the spinner to create
        text: Text to display with the spinner
        style: Style for the spinner

    Returns:
        A valid Spinner instance (always succeeds, falls back to 'dots' if needed)
    """
    try:
        return Spinner(spinner_name, text=text, style=style)
    except (ValueError, KeyError):
        # Invalid spinner name - fallback to safe default
        return Spinner("dots", text=text, style=style)


# Enhanced thinking messages with stages (emoji-rich or simple, depending on SIMPLE_UI)
if SIMPLE_UI:
    THINKING_MESSAGES_STAGE_1 = [
        "Analyzing your request...",
        "Understanding what you need...",
        "Processing your input...",
        "Identifying the task...",
        "Examining the requirements...",
    ]

    THINKING_MESSAGES_STAGE_2 = [
        "Generating code structure...",
        "Crafting your DSPy components...",
        "Building the solution...",
        "Creating the code...",
        "Assembling the pieces...",
        "Weaving everything together...",
    ]

    THINKING_MESSAGES_STAGE_3 = [
        "Adding the finishing touches...",
        "Polishing the code...",
        "Optimizing the structure...",
        "Adding best practices...",
        "Finalizing your program...",
        "Almost there...",
    ]

    # Engaging messages for LLM processing
    LLM_PROCESSING_MESSAGES = [
        "Thinking about your request...",
        "Processing with the language model...",
        "The AI is working on your request...",
        "Generating an answer...",
        "Crafting the solution...",
    ]

    # Code generation specific messages
    CODE_GENERATION_MESSAGES = [
        "Writing your signature...",
        "Building your module...",
        "Engineering the structure...",
        "Adding best practices...",
        "Polishing the code...",
    ]
else:
    # Emoji-rich messages (default)
    THINKING_MESSAGES_STAGE_1 = [
        "🧠 Analyzing your request...",
        "🔍 Understanding what you need...",
        "📝 Processing your input...",
        "🎯 Identifying the task...",
        "🔬 Examining the requirements...",
    ]

    THINKING_MESSAGES_STAGE_2 = [
        "⚡ Generating code structure...",
        "🎨 Crafting your DSPy components...",
        "🔧 Building the solution...",
        "✨ Creating the code...",
        "🏗️  Assembling the pieces...",
        "🌟 Weaving everything together...",
    ]

    THINKING_MESSAGES_STAGE_3 = [
        "🎭 Adding the finishing touches...",
        "💫 Polishing the code...",
        "🌈 Optimizing the structure...",
        "🎪 Adding best practices...",
        "🔮 Finalizing your program...",
        "✨ Almost there...",
    ]

    # Engaging messages for LLM processing
    LLM_PROCESSING_MESSAGES = [
        "🤔 Thinking deeply about this...",
        "💭 Processing with the language model...",
        "🧠 The AI is working on your request...",
        "⚡ Generating intelligent response...",
        "🎯 Crafting the perfect solution...",
        "🌟 Creating something amazing...",
        "🔮 Consulting the knowledge base...",
        "📚 Drawing from DSPy expertise...",
        "🎨 Painting your solution...",
        "🚀 Accelerating through the problem...",
        "💡 Having a brilliant idea...",
        "🎪 Performing computational magic...",
        "🔬 Analyzing patterns and structures...",
        "🎭 Orchestrating the components...",
        "🌈 Synthesizing the answer...",
        "✨ Channeling DSPy wisdom...",
        "🎯 Zeroing in on the solution...",
        "🌟 Weaving code and concepts...",
        "💫 Assembling the perfect response...",
        "🔧 Engineering excellence...",
    ]

    # Code generation specific messages
    CODE_GENERATION_MESSAGES = [
        "📝 Writing your signature...",
        "🏗️  Building your module...",
        "⚙️  Engineering the structure...",
        "🎨 Adding best practices...",
        "✨ Polishing the code...",
        "🔧 Optimizing the implementation...",
        "🌟 Adding documentation...",
        "💫 Finalizing details...",
    ]


def get_random_thinking_message(stage: int = 1) -> str:
    """Get a random thinking message for a specific stage."""
    if stage == 1:
        return random.choice(THINKING_MESSAGES_STAGE_1)
    elif stage == 2:
        return random.choice(THINKING_MESSAGES_STAGE_2)
    elif stage == 3:
        return random.choice(THINKING_MESSAGES_STAGE_3)
    else:
        return random.choice(THINKING_MESSAGES_STAGE_2)


def get_random_llm_message() -> str:
    """Get a random message for LLM processing."""
    return random.choice(LLM_PROCESSING_MESSAGES)


def get_random_code_message() -> str:
    """Get a random message for code generation."""
    return random.choice(CODE_GENERATION_MESSAGES)


class EnhancedThinkingAnimation:
    """
    Enhanced context manager for showing engaging thinking animations.
    Features progressive messages and multiple spinner types.

    Usage:
        with EnhancedThinkingAnimation():
            # Do work here
            pass
    """

    def __init__(
        self,
        initial_message: str | None = None,
        message_type: str = "llm",  # "llm", "code", "general"
        update_interval: float = 2.0,
        show_progress: bool = True,
    ):
        self.message_type = message_type
        self.update_interval = update_interval
        self.show_progress = show_progress
        self.current_stage = 1
        self.start_time = None
        self.message_count = 0

        # Select initial message based on type
        if initial_message:
            self.current_message = initial_message
        elif message_type == "llm":
            self.current_message = get_random_llm_message()
        elif message_type == "code":
            self.current_message = get_random_code_message()
        else:
            self.current_message = get_random_thinking_message(1)

        # Use spinner types that render well across terminals; allow a simpler set if SIMPLE_UI is on.
        if SIMPLE_UI:
            spinner_types = [
                "dots",
                "line",
                "bouncingBar",
            ]
        else:
            spinner_types = [
                "dots",
                "dots2",
                "dots3",
                "dots4",
                "dots5",
                "dots6",
                "dots7",
                "dots8",
                "dots9",
                "dots10",
                "dots11",
                "dots12",
                "line",
                "line2",
                "pipe",
                "simpleDots",
                "simpleDotsScrolling",
                "star",
                "star2",
                "flip",
                "hamburger",
                "growVertical",
                "growHorizontal",
                "bounce",
                "boxBounce",
                "boxBounce2",
                "triangle",
                "arc",
                "circle",
                "squareCorners",
                "circleQuarters",
                "circleHalves",
                "squish",
                "toggle",
                "toggle2",
                "toggle3",
                "toggle4",
                "toggle5",
                "toggle6",
                "toggle7",
                "toggle8",
                "toggle9",
                "toggle10",
                "toggle11",
                "toggle12",
                "toggle13",
                "arrow",
                "arrow2",
                "arrow3",
                "bouncingBar",
                "bouncingBall",
                "smiley",
                "hearts",
                "clock",
            ]

        self.spinner_type = random.choice(spinner_types)
        # Use safe spinner creation (handles PyPI package compatibility)
        # This will always succeed, falling back to "dots" if spinner_type is invalid
        self.spinner = create_safe_spinner(
            self.spinner_type, text=self.current_message, style="cyan"
        )
        self.live = None
        self.update_thread = None
        self.running = False

    def _get_next_message(self) -> str:
        """Get the next message based on current stage and message type."""
        self.message_count += 1

        # Progress through stages
        if self.message_count <= 3:
            self.current_stage = 1
        elif self.message_count <= 6:
            self.current_stage = 2
        else:
            self.current_stage = 3

        if self.message_type == "llm":
            return get_random_llm_message()
        elif self.message_type == "code":
            return get_random_code_message()
        else:
            return get_random_thinking_message(self.current_stage)

    def _update_message(self):
        """Update message in a separate thread."""
        while self.running:
            time.sleep(self.update_interval)
            if self.running and self.live:
                new_message = self._get_next_message()
                self.current_message = new_message
                self.spinner.text = new_message
                if self.live:
                    try:
                        self.live.update(self.spinner)
                    except Exception:
                        pass

    def __enter__(self):
        self.start_time = time.time()
        self.running = True
        self.live = Live(
            self.spinner, console=console, refresh_per_second=20, transient=False, screen=False
        )
        self.live.__enter__()

        # Start message update thread
        if self.update_interval > 0:
            self.update_thread = threading.Thread(target=self._update_message, daemon=True)
            self.update_thread.start()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False

        # Wait a bit for thread to finish current update
        if self.update_thread and self.update_thread.is_alive():
            time.sleep(0.1)

        if self.live:
            self.live.__exit__(exc_type, exc_val, exc_tb)

        # Show completion message with engaging text
        elapsed = time.time() - self.start_time if self.start_time else 0
        if elapsed > 0.5:  # Only show if it took meaningful time
            if elapsed < 2.0:
                completion_msg = f"✨ Done! ({elapsed:.1f}s)"
            elif elapsed < 5.0:
                completion_msg = f"✓ Completed in {elapsed:.1f}s"
            else:
                completion_msg = f"🎉 Finished! That took {elapsed:.1f}s"
            console.print(f"[green]{completion_msg}[/green]")

    def update(self, message: str):
        """Update the animation message immediately."""
        self.current_message = message
        if self.live:
            self.spinner.text = message
            self.live.update(self.spinner)

    def set_stage(self, stage: int, message: str | None = None):
        """Set the current stage and optionally update message."""
        self.current_stage = stage
        if message:
            self.update(message)
        else:
            new_message = get_random_thinking_message(stage)
            self.update(new_message)


class ProgressiveThinkingAnimation:
    """
    Progressive animation that shows multiple stages with engaging visuals.
    Similar to Claude Code's multi-stage progress indicators.
    """

    def __init__(self, stages: list[str] | None = None, message_type: str = "llm"):
        if stages is None:
            if message_type == "llm":
                self.stages = [
                    "🔍 Understanding your request...",
                    "🧠 Processing with AI...",
                    "✨ Generating response...",
                    "🎨 Polishing the output...",
                ]
            elif message_type == "code":
                self.stages = [
                    "📝 Analyzing requirements...",
                    "🏗️  Building structure...",
                    "⚙️  Implementing logic...",
                    "✨ Adding best practices...",
                ]
            else:
                self.stages = [
                    "🔍 Analyzing...",
                    "⚡ Processing...",
                    "✨ Finalizing...",
                ]
        else:
            self.stages = stages

        self.current_stage = 0
        self.live = None
        self.running = False

    def _create_display(self) -> Panel:
        """Create the display panel with current stage."""
        stage_text = Text()

        # Show completed stages
        for i, stage in enumerate(self.stages):
            if i < self.current_stage:
                stage_text.append("✓ ", style="green bold")
                stage_text.append(stage, style="green dim")
            elif i == self.current_stage:
                stage_text.append("⟳ ", style="cyan bold")
                stage_text.append(stage, style="cyan")
            else:
                stage_text.append("○ ", style="dim")
                stage_text.append(stage, style="dim")

            if i < len(self.stages) - 1:
                stage_text.append("\n")

        return Panel(
            Align.left(stage_text),
            border_style="cyan",
            title="[bold cyan]Processing[/bold cyan]",
            padding=(1, 2),
        )

    def __enter__(self):
        self.running = True
        self.live = Live(
            self._create_display(), console=console, refresh_per_second=10, transient=False
        )
        self.live.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        if self.live:
            # Complete all stages
            self.current_stage = len(self.stages)
            self.live.update(self._create_display())
            time.sleep(0.3)
            self.live.__exit__(exc_type, exc_val, exc_tb)

    def next_stage(self):
        """Move to the next stage."""
        if self.current_stage < len(self.stages) - 1:
            self.current_stage += 1
            if self.live:
                self.live.update(self._create_display())


# Backward compatibility
class ThinkingAnimation(EnhancedThinkingAnimation):
    """Backward compatible wrapper for ThinkingAnimation."""


# Backward compatibility: get_random_thinking_message() without stage parameter
# Use get_random_thinking_message(stage=1) instead


def show_progress_animation(message: str, duration: float = 1.0):
    """Show a brief progress animation."""
    with EnhancedThinkingAnimation(initial_message=message, message_type="general"):
        time.sleep(duration)
