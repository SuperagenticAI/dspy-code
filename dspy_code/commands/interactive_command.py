"""
Interactive REPL mode for DSPy Code.

This module provides a conversational interface where users can interact
with the CLI using natural language to generate DSPy components.
"""

import os
import re
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from ..core.config import ConfigManager
from ..core.exceptions import DSPyCLIError
from ..core.logging import get_logger
from ..models.code_generator import CodeGenerator
from ..models.model_manager import ModelManager
from ..models.task_collector import FieldDefinition, ReasoningPattern, TaskDefinition

# Import beautiful UI components
# from ..ui.welcome import show_welcome_screen  # Now using _show_welcome_screen in execute()
from ..ui.animations import (
    EnhancedThinkingAnimation,
)
from ..ui.prompts import (
    get_user_input,
    show_assistant_header,
    show_code_panel,
    show_error_message,
    show_info_message,
    show_next_steps,
    show_success_message,
    show_warning_message,
)
from .nl_command_router import NLCommandRouter

console = Console()
logger = get_logger(__name__)


class InteractiveSession:
    """Manages an interactive REPL session for DSPy Code."""

    def __init__(self, config_manager: ConfigManager, model_manager: ModelManager):
        self.config_manager = config_manager
        self.model_manager = model_manager
        self.code_generator = CodeGenerator(model_manager)
        self.conversation_history: list[dict[str, str]] = []
        self.current_context: dict[str, Any] = {}

        # Initialize LLM connector and reference loader
        from ..commands.slash_commands import SlashCommandHandler
        from ..models.dspy_reference_loader import DSPyReferenceLoader
        from ..models.llm_connector import LLMConnector
        from ..rag import CodebaseRAG

        self.llm_connector = LLMConnector(config_manager)
        self.reference_loader = DSPyReferenceLoader()

        # Initialize RAG system for codebase knowledge (lazy load only if index exists)
        # Indexing happens during /init command
        try:
            self.codebase_rag = CodebaseRAG(config_manager=config_manager)
            # Check if index exists
            if self.codebase_rag.enabled and self.codebase_rag.index is not None:
                logger.info("CodebaseRAG loaded from cache")
            else:
                logger.info("CodebaseRAG not initialized - run /init to build index")
        except Exception as e:
            logger.warning(f"Failed to load CodebaseRAG: {e}")
            self.codebase_rag = None

        self.slash_handler = SlashCommandHandler(
            self.llm_connector,
            self.reference_loader,
            self.conversation_history,
            self.current_context,
            config_manager,
        )

        # Set parent session reference for session management
        self.slash_handler.parent_session = self

        # Initialize natural language command router with LLM connector for hybrid routing
        self.nl_router = NLCommandRouter(llm_connector=self.llm_connector)

        # Auto-connect to default model if configured
        self._auto_connect_default_model()

    def start(self):
        """Start the interactive session."""
        # Welcome screen is now shown in execute() function before session starts

        # REQUIRE MODEL CONNECTION BEFORE PROCEEDING
        if not self._ensure_model_connected():
            console.print()
            console.print("[yellow]⚠️  Model connection is required to use DSPy Code.[/yellow]")
            console.print()
            console.print("[dim]Exiting...[/dim]")
            return

        # Start auto-save
        self.slash_handler.session_manager.start_auto_save(self)
        logger.info("Auto-save started (every 5 minutes)")

        # Check for recent auto-save to restore
        self._check_auto_save_restore()

        # Track if this is the first interaction
        first_interaction = True

        try:
            while True:
                try:
                    # Get user input with fancy text box
                    user_input = get_user_input(
                        show_examples=first_interaction,
                        conversation_count=len(self.conversation_history) // 2,
                    )
                    first_interaction = False

                    if not user_input.strip():
                        continue

                    # Check for slash commands first
                    if user_input.startswith("/"):
                        self.slash_handler.handle_command(user_input)
                        # Check if exit was requested
                        if self.slash_handler.should_exit:
                            break
                        # After /connect, verify connection is still active
                        if user_input.startswith("/connect"):
                            if not self.llm_connector.current_model:
                                console.print()
                                console.print(
                                    "[yellow]⚠️  Connection failed. Please connect to a model to continue.[/yellow]"
                                )
                                console.print()
                        continue

                    # Legacy support for non-slash commands (redirect to slash commands)
                    if user_input.lower() in ["exit", "quit", "bye", "q"]:
                        self.slash_handler.handle_command("/exit")
                        break

                    if user_input.lower() in ["help", "?"]:
                        self.slash_handler.handle_command("/help")
                        continue

                    if user_input.lower() in ["clear", "reset"]:
                        self.slash_handler.handle_command("/clear")
                        continue

                    if user_input.lower().startswith("save"):
                        # Convert to slash command
                        parts = user_input.split(maxsplit=1)
                        if len(parts) > 1:
                            self.slash_handler.handle_command(f"/save {parts[1]}")
                        else:
                            self.slash_handler.handle_command("/save")
                        continue

                    # Try to route natural language to slash commands (LLM makes final decision)
                    # BUT: Skip NL routing if it's clearly a code generation request
                    # (to avoid false positives with data generation)
                    context = {
                        "current_model": self.llm_connector.current_model
                        if self.llm_connector
                        else None,
                        "has_code": "last_generated" in self.current_context,
                        "has_data": "last_generated_data" in self.current_context,
                        "conversation_history": self.conversation_history[-5:]
                        if self.conversation_history
                        else [],  # Last 5 messages
                    }

                    # Quick check: if it looks like code generation (not data generation), skip NL routing
                    user_lower = user_input.lower()
                    import re

                    # Check for explicit data generation patterns (most specific first)
                    explicit_data_patterns = [
                        r"\bgenerate\s+\d+\s+examples?\b",
                        r"\bcreate\s+\d+\s+examples?\b",
                        r"\bmake\s+\d+\s+examples?\b",
                        r"\bgenerate\s+(?:training\s+)?(?:data|examples?|dataset)\b",
                        r"\bcreate\s+(?:training\s+)?(?:data|examples?|dataset|gold\s+examples?)\b",
                        r"\bmake\s+(?:training\s+)?(?:data|examples?|dataset)\b",
                        r"\bexamples?\s+for\s+\w+",
                        r"\btraining\s+(?:data|examples?)\b",
                        r"\bgold\s+examples?\b",
                        r"\bsynthetic\s+data\b",
                    ]

                    is_explicit_data_gen = any(
                        re.search(pattern, user_lower) for pattern in explicit_data_patterns
                    )

                    # Check if this is clearly a code generation request (skip NL routing)
                    code_generation_keywords = [
                        r"\b(build|create|write|make|generate|design)\s+(?:a\s+)?(?:dspy\s+)?(?:program|module|signature|class|code)",
                        r"\b(build|create|write|make|generate|design)\s+(?:a\s+)?(?:dspy\s+)?(?:program|module|signature|class|code)\s+for",
                        r"(?:program|module|signature|class)\s+(?:for|that|which)",
                    ]
                    is_code_generation = any(
                        re.search(pattern, user_lower) for pattern in code_generation_keywords
                    )

                    # Only try NL routing if it's NOT clearly code generation
                    # Code generation requests should go straight to _process_input
                    if is_code_generation:
                        logger.debug(
                            f"Detected code generation request, skipping NL routing: {user_input[:50]}..."
                        )
                        # Skip NL routing, go straight to code generation
                        if not self.llm_connector.current_model:
                            console.print()
                            show_warning_message("Model connection required for code generation.")
                            console.print()
                            console.print("[yellow]💡 Please connect to a model first:[/yellow]")
                            console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
                            console.print("  [cyan]/models[/cyan] - See all available models")
                            console.print()
                            continue
                        self._process_input(user_input)
                        continue

                    # For data generation, try NL routing
                    if is_explicit_data_gen:
                        nl_route = self.nl_router.route(user_input, context=context)
                        if nl_route:
                            command, args = nl_route
                            # Execute the routed slash command
                            full_command = f"{command} {' '.join(args)}" if args else command
                            logger.debug(f"Executing routed command: {full_command}")
                            self.slash_handler.handle_command(full_command)
                            if self.slash_handler.should_exit:
                                break
                            continue

                    # For other requests, try NL routing (might be commands like "connect", "save", etc.)
                    nl_route = self.nl_router.route(user_input, context=context)
                    if nl_route:
                        command, args = nl_route
                        # If it routed to /data but doesn't match explicit patterns, it's likely a false positive
                        if command == "/data" and not is_explicit_data_gen:
                            logger.debug(f"Ignoring false positive /data route for: {user_input}")
                            # Fall through to code generation / general LLM handling
                        # If it routed to /explain with no topic, treat as a natural-language question
                        # about the current code/session instead of forcing the slash command.
                        elif command == "/explain" and not args:
                            logger.debug(
                                "Routing generic 'explain' follow-up to LLM instead of /explain slash command"
                            )
                            # Fall through to general LLM handling below
                        else:
                            # Execute the routed slash command
                            full_command = f"{command} {' '.join(args)}" if args else command
                            logger.debug(f"Executing routed command: {full_command}")
                            try:
                                self.slash_handler.handle_command(full_command)
                                if self.slash_handler.should_exit:
                                    break
                                continue
                            except Exception as e:
                                # If command execution fails, it might be a code generation request
                                logger.debug(
                                    f"Command execution failed, treating as code generation: {e}"
                                )
                                # Fall through to general LLM handling

                    # If no slash command match, process as natural language for code generation
                    # But first check if model is connected
                    if not self.llm_connector.current_model:
                        console.print()
                        show_warning_message("Model connection required for code generation.")
                        console.print()
                        console.print("[yellow]💡 Please connect to a model first:[/yellow]")
                        console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
                        console.print("  [cyan]/models[/cyan] - See all available models")
                        console.print()
                        continue

                    self._process_input(user_input)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Use 'exit' to quit[/yellow]")
                    continue
                except EOFError:
                    console.print("\n[yellow]Goodbye! 👋[/yellow]")
                    break
                except Exception as e:
                    logger.error(f"Error in interactive session: {e}")
                    console.print(f"[red]Error:[/red] {e}")
        finally:
            # Stop auto-save on exit
            self.slash_handler.session_manager.stop_auto_save()
            logger.info("Auto-save stopped")

    def _auto_connect_default_model(self):
        """Auto-connect to the default model from config if available."""
        try:
            # Check if there's a default model configured
            default_model = self.config_manager.config.default_model
            if not default_model:
                logger.debug("No default model configured, skipping auto-connect")
                return

            # Determine model type from config
            model_type = None
            api_key = None

            # Check if it's in Ollama models list
            if default_model in self.config_manager.config.models.ollama_models:
                model_type = "ollama"

            # Check if it matches OpenAI model
            elif default_model == self.config_manager.config.models.openai_model:
                model_type = "openai"
                api_key = self.config_manager.config.models.openai_api_key or os.getenv(
                    "OPENAI_API_KEY"
                )

            # Check if it matches Anthropic model
            elif default_model == self.config_manager.config.models.anthropic_model:
                model_type = "anthropic"
                api_key = self.config_manager.config.models.anthropic_api_key or os.getenv(
                    "ANTHROPIC_API_KEY"
                )

            # Check if it matches Gemini model
            elif default_model == self.config_manager.config.models.gemini_model:
                model_type = "gemini"
                api_key = self.config_manager.config.models.gemini_api_key or os.getenv(
                    "GEMINI_API_KEY"
                )

            # If not found in any specific config, assume it's Ollama (most common for local models)
            else:
                logger.debug(f"Model '{default_model}' not found in config, assuming Ollama")
                model_type = "ollama"

            if model_type:
                logger.info(f"Auto-connecting to default model: {default_model} ({model_type})")
                self.llm_connector.connect_to_model(default_model, model_type, api_key)
                logger.info(f"Successfully connected to {default_model}")
            else:
                logger.warning(f"Could not determine model type for '{default_model}'")

        except Exception as e:
            logger.warning(f"Failed to auto-connect to default model: {e}")
            # Don't fail the session if auto-connect fails

    def _ensure_model_connected(self) -> bool:
        """
        Ensure a model is connected before proceeding.
        Prompts user to connect if not already connected.

        Returns:
            True if model is connected, False if user chose to exit
        """
        # Check if already connected
        if self.llm_connector.current_model:
            return True

        # Show connection requirement message
        console.print()
        console.print(
            "[bold yellow]🔌 Connect a model to start:[/bold yellow] [cyan]/model[/cyan] for interactive selection, or [cyan]/connect ollama gpt-oss:120b[/cyan], or [cyan]/models[/cyan] to see all options"
        )
        console.print()

        # Allow connection attempts in a loop
        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            attempts += 1

            # Get user input
            user_input = Prompt.ask(
                "[bold cyan]Enter command[/bold cyan]",
                default="/model" if attempts == 1 else "",
            ).strip()

            if not user_input:
                continue

            # Handle exit
            if user_input.lower() in ["exit", "quit", "q", "/exit"]:
                return False

            # Handle slash commands
            if user_input.startswith("/"):
                # Execute the command
                self.slash_handler.handle_command(user_input)

                # Check if connection was successful
                if self.llm_connector.current_model:
                    console.print()
                    show_success_message(f"Connected to {self.llm_connector.current_model}!")
                    console.print()
                    return True
                else:
                    # Check if it was a connect command that failed
                    if user_input.startswith("/connect"):
                        console.print()
                        console.print("[yellow]⚠️  Connection failed. Please try again.[/yellow]")
                        console.print()
                        if attempts < max_attempts:
                            console.print("[dim]You can also try:[/dim]")
                            console.print("  • [cyan]/models[/cyan] - See available models")
                            console.print("  • [cyan]/help[/cyan] - Get help with connection")
                            console.print()
                    continue

            # If not a slash command, treat as natural language and suggest /connect
            console.print()
            console.print("[yellow]Please use a slash command to connect.[/yellow]")
            console.print("  Try: [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print()

        # Max attempts reached
        console.print()
        console.print("[red]Maximum connection attempts reached.[/red]")
        console.print("[dim]Please ensure you have a model available and try again.[/dim]")
        return False

    def _check_auto_save_restore(self):
        """Check for recent auto-save and offer to restore."""
        try:
            sessions = self.slash_handler.session_manager.list_sessions()

            # Find most recent auto-save
            auto_saves = [s for s in sessions if s.name.startswith("autosave_")]
            if not auto_saves:
                return

            latest = auto_saves[0]  # Already sorted by timestamp

            # Check if it's recent (within last hour)
            from datetime import datetime, timedelta

            if datetime.now() - latest.timestamp < timedelta(hours=1):
                console.print()
                console.print(
                    f"[yellow]💾 Found recent auto-save from {latest.timestamp.strftime('%H:%M')}[/yellow]"
                )
                console.print(
                    f"[dim]   {latest.message_count} messages, {latest.file_count} files[/dim]"
                )
                console.print()

                from rich.prompt import Confirm

                if Confirm.ask("Restore previous session?", default=False):
                    self.slash_handler.handle_command(f"/session load {latest.name}")
                    console.print()
        except Exception as e:
            logger.debug(f"Auto-save restore check failed: {e}")

    def _show_welcome(self):
        """Show welcome message with quick start commands and RAG status."""
        from rich.table import Table

        # Check model status
        model_status = "✅ Connected" if self.llm_connector.current_model else "❌ Not connected"
        model_name = (
            self.llm_connector.current_model or self.config_manager.config.default_model or "None"
        )

        # Quick Start Commands Table
        quick_commands = Table.grid(padding=(0, 2))
        quick_commands.add_column(style="cyan bold")
        quick_commands.add_column(style="dim")

        quick_commands.add_row("/connect", "Connect to a model (e.g., /connect ollama llama3.1:8b)")
        quick_commands.add_row("/help", "Show all available commands")
        quick_commands.add_row("/explain", "Learn about DSPy concepts")
        quick_commands.add_row("/status", "Check current session status")
        quick_commands.add_row("/exit", "Exit the CLI")

        # Example Workflows
        workflows = Table.grid(padding=(0, 2))
        workflows.add_column(style="green bold")
        workflows.add_column(style="dim")

        workflows.add_row("💬 Natural Language", '"Create a sentiment analyzer"')
        workflows.add_row("📊 Generate Data", '"Generate 20 examples for QA"')
        workflows.add_row("🔧 Build Module", '"Build a RAG system with retrieval"')
        workflows.add_row("⚡ Optimize", '"Optimize my program with GEPA"')
        workflows.add_row("📈 Evaluate", '"Evaluate my program with accuracy"')

        # Main welcome panel
        welcome_content = """
[bold cyan]Welcome to DSPy Code![/bold cyan] 🚀

Your AI-powered DSPy development assistant. Build, optimize, and learn DSPy with natural language.

[bold yellow]📋 Quick Start Commands:[/bold yellow]
"""

        console.print(Panel(Markdown(welcome_content), border_style="cyan", title="DSPy Code"))
        console.print(quick_commands)
        console.print()

        console.print("[bold green]💡 Example Workflows:[/bold green]")
        console.print(workflows)
        console.print()

        # Status info
        status_text = f"[bold]Current Status:[/bold] {model_status}"
        if model_name != "None":
            status_text += f" ([cyan]{model_name}[/cyan])"
        console.print(status_text)

        # Show RAG and Fast Mode status with humor
        try:
            rag_config = self.config_manager.config.codebase_rag
            rag_enabled = rag_config.enabled if rag_config else False  # Default to disabled
            fast_mode = rag_config.fast_mode if rag_config else True  # Default to enabled

            # RAG status
            if self.codebase_rag and self.codebase_rag.enabled:
                if self.codebase_rag.index:
                    element_count = len(self.codebase_rag.index.elements)
                    rag_status = f"[cyan]RAG Mode:[/cyan] [green]ON[/green] ({element_count} elements indexed)"
                else:
                    rag_status = (
                        "[cyan]RAG Mode:[/cyan] [yellow]ON[/yellow] (no index - run /init to build)"
                    )
            else:
                rag_status = "[cyan]RAG Mode:[/cyan] [red]OFF[/red] (use /enable-rag to enable)"

            # Fast Mode status
            fast_status = (
                "[cyan]Fast Mode:[/cyan] [green]ON[/green]"
                if fast_mode
                else "[cyan]Fast Mode:[/cyan] [yellow]OFF[/yellow]"
            )

            console.print()
            console.print("[bold]Performance Settings:[/bold]")
            console.print(f"  {rag_status}")
            console.print(f"  {fast_status}")

            # Add message about quality vs speed
            if rag_enabled and not fast_mode:
                console.print()
                console.print("[dim]💡 RAG enabled - better code quality, slower responses[/dim]")
                console.print(
                    "[dim]   Use [cyan]/fast-mode on[/cyan] for faster responses or check [cyan]/status[/cyan] for details[/dim]"
                )
            elif not rag_enabled:
                console.print()
                console.print(
                    "[dim]💡 Fast mode ON, RAG disabled - quick responses, lower code quality[/dim]"
                )
                console.print(
                    "[dim]   Use [cyan]/enable-rag[/cyan] and [cyan]/fast-mode off[/cyan] for better quality (slower)[/dim]"
                )
            elif fast_mode:
                console.print()
                console.print(
                    "[dim]💡 Fast mode enabled - quick responses, slightly lower quality[/dim]"
                )
                console.print(
                    "[dim]   Use [cyan]/enable-rag[/cyan] and [cyan]/fast-mode off[/cyan] for better quality (slower)[/dim]"
                )
        except Exception as e:
            logger.debug(f"Error showing performance status: {e}")
            console.print("[dim]Performance: Status unknown[/dim]")

        if not self.llm_connector.current_model:
            console.print()
            console.print("[yellow]💡 Tip:[/yellow] Connect to a model to enable code generation:")
            console.print("   [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print("   [cyan]/connect openai gpt-4[/cyan]")
            console.print("   [cyan]/models[/cyan] - See all available models")

        console.print()
        console.print("[dim]Type your request or use [cyan]/help[/cyan] for more commands[/dim]")
        console.print()

    def _show_goodbye(self):
        """Show goodbye message with conversation summary."""
        console.print()

        # Show conversation summary
        if self.conversation_history:
            console.print(
                f"[dim]📊 Session Summary: {len(self.conversation_history) // 2} interactions[/dim]"
            )
            console.print()

        goodbye_text = Text()
        goodbye_text.append("👋 ", style="bold")
        goodbye_text.append("Thanks for using DSPy Code! ", style="bold cyan")
        goodbye_text.append("Happy coding!", style="dim")
        console.print(goodbye_text)
        console.print()

    def _show_help(self):
        """Show help message."""
        help_text = """
**Available Commands:**

- `help` or `?` - Show this help message
- `clear` or `reset` - Clear conversation history and start fresh
- `save <filename>` - Save the last generated code to a file
- `exit`, `quit`, `bye`, or `q` - Exit interactive mode

**Slash Commands:**

- `/connect <type> <model>` - Connect to a language model
- `/models` - List available models
- `/model` - Interactively select and connect to a model
- `/status` - Show connection status
- `/disconnect` - Disconnect from model
- `/reference [topic]` - View DSPy documentation
- `/help` - Show slash command help

**Natural Language Examples:**

**Creating Signatures:**
- "Create a signature for email classification"
- "I need input fields for text and output field for category"
- "Build a signature with question and answer fields"

**Creating Modules:**
- "Generate a module using chain of thought"
- "Create a predictor for sentiment analysis"
- "Build a ReAct module for question answering"

**Complete Programs:**
- "Create a complete email classifier"
- "Build a text summarization system"
- "Generate a question answering program"

**Generate Training Data:**
- "Generate 20 examples for sentiment analysis"
- "Create 50 gold examples for question answering"
- "Make training data for email classification"
- "Generate synthetic data for text summarization"

**Tips:**
- Be specific about your requirements
- Mention input and output fields if you know them
- Specify reasoning patterns (predict, chain of thought, react)
- Ask follow-up questions to refine the code
- Generate training data for GEPA optimization
"""
        console.print(Panel(Markdown(help_text), border_style="green", title="Help"))

    def _clear_context(self):
        """Clear conversation context."""
        self.conversation_history.clear()
        self.current_context.clear()
        console.print("[green]✓[/green] Context cleared. Starting fresh!")

    def _process_input(self, user_input: str):
        """Process user's natural language input."""
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": user_input})

        # Show enhanced thinking animation while analyzing
        with EnhancedThinkingAnimation(message_type="llm", update_interval=2.0):
            intent = self._analyze_intent(user_input)

        # Show assistant header
        show_assistant_header()

        if intent == "create_signature":
            self._handle_create_signature(user_input)
        elif intent == "create_module":
            self._handle_create_module(user_input)
        elif intent == "create_program":
            self._handle_create_program(user_input)
        elif intent == "generate_data":
            self._handle_generate_data(user_input)
        elif intent == "optimize":
            self._handle_optimize(user_input)
        elif intent == "evaluate" or intent == "eval":
            self._handle_evaluate(user_input)
        elif intent == "explain":
            self._handle_explain(user_input)
        else:
            self._handle_general_query(user_input)

    def _analyze_intent(self, user_input: str) -> str:
        """Analyze user intent from natural language input with enhanced detection."""
        user_input_lower = user_input.lower().strip()

        # Helper: detect if this looks like a natural-language question
        is_question = (
            "?" in user_input
            or user_input_lower.endswith("?")
            or user_input_lower.startswith(
                (
                    "how ",
                    "what ",
                    "why ",
                    "can ",
                    "could ",
                    "should ",
                    "would ",
                    "explain ",
                    "tell me ",
                    "describe ",
                )
            )
        )

        # PRIORITY 0: Check for code generation requests FIRST (before explanation)
        # These should NOT be treated as explanation requests
        code_generation_indicators = [
            r"\b(write|create|build|make|generate|design)\s+signature",
            r"\b(write|create|build|make|generate|design)\s+module",
            r"\b(write|create|build|make|generate|design)\s+program",
            r"\b(write|create|build|make|generate|design)\s+code",
            r"\b(write|create|build|make|generate|design)\s+class",
        ]
        for pattern in code_generation_indicators:
            if re.search(pattern, user_input_lower):
                # Check if it's signature creation
                if "signature" in user_input_lower:
                    logger.debug(
                        f"Intent: create_signature (matched code generation pattern: {pattern})"
                    )
                    return "create_signature"
                # Check if it's module/program creation
                elif any(
                    word in user_input_lower for word in ["module", "program", "class", "code"]
                ):
                    logger.debug(
                        f"Intent: create_module (matched code generation pattern: {pattern})"
                    )
                    return "create_module"

        # PRIORITY 1: Check for explanation requests (but NOT code generation)
        explanation_patterns = [
            user_input_lower.startswith(
                (
                    "explain",
                    "what is",
                    "how does",
                    "how can",
                    "tell me about",
                    "describe",
                    "what are",
                    "how are",
                    "why",
                )
            ),
            "what is" in user_input_lower and is_question,
            "how does" in user_input_lower and is_question,
            "how can" in user_input_lower and is_question,
            "tell me about" in user_input_lower,
            "explain" in user_input_lower and is_question,
        ]
        # Only treat as explanation if it's NOT a code generation request
        if any(explanation_patterns) and not any(
            re.search(pattern, user_input_lower) for pattern in code_generation_indicators
        ):
            logger.debug("Intent: explain (matched explanation patterns)")
            return "explain"

        # PRIORITY 2: Check for data generation (VERY SPECIFIC - require action verb + data keyword)

        # First check for explicit data generation patterns with numbers (most specific)
        data_with_number = re.search(
            r"\b(generate|create|make|produce)\s+(\d+)\s+(examples?|data|training\s+data|training\s+examples?|synthetic\s+data)",
            user_input_lower,
        )
        if data_with_number:
            logger.debug("Intent: generate_data (matched data generation with number)")
            return "generate_data"

        # Then check for explicit data generation phrases (require BOTH action verb AND data keyword)
        data_generation_patterns = [
            r"\bgenerate\s+(?:training\s+)?(?:data|examples?|dataset|synthetic\s+data)",
            r"\bcreate\s+(?:training\s+)?(?:data|examples?|dataset|synthetic\s+data|gold\s+examples?)",
            r"\bmake\s+(?:training\s+)?(?:data|examples?|dataset)",
            r"\bproduce\s+(?:training\s+)?(?:data|examples?|dataset)",
            r"\bgenerate\s+\d+\s+examples?",
            r"\bcreate\s+\d+\s+examples?",
            r"\bmake\s+\d+\s+examples?",
            r"\bexamples?\s+for\s+\w+",  # "examples for sentiment"
            r"\bdata\s+for\s+\w+",  # "data for classification"
            r"\btraining\s+(?:data|examples?)",  # "training data" or "training examples"
            r"\bgold\s+examples?",  # "gold examples"
            r"\bsynthetic\s+data",  # "synthetic data"
        ]

        # Check if any pattern matches (using word boundaries to avoid partial matches)
        for pattern in data_generation_patterns:
            if re.search(pattern, user_input_lower):
                logger.debug(f"Intent: generate_data (matched pattern: {pattern})")
                return "generate_data"

        # PRIORITY 3: Check for optimization
        optimize_keywords = ["optimize", "improve", "gepa", "better performance", "optimization"]
        if any(keyword in user_input_lower for keyword in optimize_keywords) and not is_question:
            logger.debug("Intent: optimize (matched optimization keywords)")
            return "optimize"

        # PRIORITY 5: Check for signature creation (explicit keywords - HIGH PRIORITY for code generation)
        # Patterns like "write signature", "create signature", "build signature", "make signature", "signature for"
        signature_patterns = [
            r"\b(write|create|build|make|generate|design)\s+signature",
            r"\bsignature\s+(?:for|with|that)",
            r"\bsignature\s+(?:has|contains|includes)",
            r"\binput\s+field",
            r"\boutput\s+field",
            r"\bcreate\s+signature",
            r"\bwrite\s+signature",
            r"\bbuild\s+signature",
        ]
        for pattern in signature_patterns:
            if re.search(pattern, user_input_lower):
                logger.debug(f"Intent: create_signature (matched pattern: {pattern})")
                return "create_signature"

        # PRIORITY 6: Check for complete program (explicit keywords)
        program_keywords = [
            "complete program",
            "full program",
            "entire program",
            "complete system",
            "full system",
            "complete application",
            "entire application",
        ]
        if any(keyword in user_input_lower for keyword in program_keywords):
            logger.debug("Intent: create_program (matched program keywords)")
            return "create_program"

        # PRIORITY 6: Check for module creation (explicit keywords)
        module_keywords = [
            "module",
            "predictor",
            "chain of thought",
            "cot",
            "react",
            "create module",
            "build module",
        ]
        if any(keyword in user_input_lower for keyword in module_keywords) and not is_question:
            logger.debug("Intent: create_module (matched module keywords)")
            return "create_module"

        # PRIORITY 7: Check for RAG/retrieval specific requests
        rag_keywords = ["rag", "retrieval", "retrieve", "document search", "knowledge base"]
        if any(keyword in user_input_lower for keyword in rag_keywords) and not is_question:
            logger.debug("Intent: create_module (matched RAG keywords)")
            return "create_module"

        # PRIORITY 8: Check for agent/tool specific requests
        agent_keywords = ["agent", "tools", "react", "actions", "tool use"]
        if any(keyword in user_input_lower for keyword in agent_keywords) and not is_question:
            logger.debug("Intent: create_module (matched agent keywords)")
            return "create_module"

        # PRIORITY 9: Task-oriented patterns (only if no other match)
        # Only match if it's clearly a task description, not a question
        if not is_question:
            task_patterns = [
                "classif",
                "analyz",
                "detect",
                "predict",
                "summar",  # Task verbs (exclude 'generat' to avoid confusion)
                "sentiment",
                "question",
                "answer",
                "email",
                "text",
                "document",  # Domain nouns
            ]
            if any(pattern in user_input_lower for pattern in task_patterns):
                logger.debug("Intent: create_module (detected task-oriented patterns)")
                return "create_module"

        # PRIORITY 10: Check for action verbs at start (only if not a question)
        if not is_question:
            action_verbs = ["create", "build", "make", "write", "develop", "need", "want"]
            if any(user_input_lower.startswith(verb) for verb in action_verbs):
                logger.debug("Intent: create_module (starts with action verb)")
                return "create_module"

        # Default to general for questions or unclear intent
        logger.debug("Intent: general (no specific patterns matched)")
        return "general"

    def _handle_create_signature(self, user_input: str):
        """Handle signature creation request."""
        console.print("I'll help you create a DSPy Signature! Let me extract the details...\n")

        # Check if model is connected - REQUIRED
        if not self.llm_connector.current_model:
            show_error_message("No model connected!")
            console.print()
            console.print(
                "[yellow]I need a language model to understand your request and generate code.[/yellow]"
            )
            console.print()
            console.print("[bold]Connect to a model:[/bold]")
            console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print("  [cyan]/connect openai gpt-4[/cyan]")
            console.print("  [cyan]/connect anthropic claude-3-sonnet[/cyan]")
            console.print()
            console.print("[dim]Or configure a default model in dspy_config.yaml[/dim]")
            return

        # Generate signature code using connected model
        with EnhancedThinkingAnimation(message_type="code", update_interval=1.5):
            signature_code = self._generate_signature_with_llm(user_input)

        if not signature_code or not signature_code.strip():
            logger.error(f"Signature generation returned empty result for: {user_input[:50]}...")
            show_error_message("Failed to generate signature. Please try being more specific.")
            console.print()
            show_info_message(
                'Example: "Create a signature for email classification with subject and body as inputs, category as output"'
            )
            return

        # Store in context
        self.current_context["last_generated"] = signature_code
        self.current_context["type"] = "signature"

        logger.debug(f"Successfully generated signature with {len(signature_code)} characters")

        # Display the code beautifully
        show_code_panel(signature_code, "Generated DSPy Signature", "python")

        show_success_message("Signature created successfully!")

        show_next_steps(
            [
                "Type [cyan]/save <filename>[/cyan] to save this code",
                "Type [cyan]/validate[/cyan] to check for errors",
                "Ask me to [green]create a module[/green] using this signature",
                "Request [yellow]modifications[/yellow] or improvements",
            ]
        )

    def _handle_create_module(self, user_input: str):
        """Handle module creation request."""
        console.print("I'll create a DSPy Module for you!\n")

        # Check if model is connected - REQUIRED
        if not self.llm_connector.current_model:
            show_error_message("No model connected!")
            console.print()
            console.print(
                "[yellow]I need a language model to understand your request and generate code.[/yellow]"
            )
            console.print()
            console.print("[bold]Connect to a model:[/bold]")
            console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print("  [cyan]/connect openai gpt-4[/cyan]")
            console.print("  [cyan]/connect anthropic claude-3-sonnet[/cyan]")
            console.print()
            console.print("[dim]Or configure a default model in dspy_config.yaml[/dim]")
            return

        # Generate module code using connected model
        with EnhancedThinkingAnimation(message_type="code", update_interval=1.5):
            module_code = self._generate_module_with_llm(user_input)

        if not module_code or not module_code.strip():
            logger.error(f"Module generation returned empty result for: {user_input[:50]}...")
            show_error_message("Failed to generate module.")
            console.print()

            # Provide actionable suggestions
            if not self.llm_connector.current_model:
                console.print("[yellow]💡 Suggestions:[/yellow]")
                console.print("  1. Connect to a model: [cyan]/connect ollama llama3.1:8b[/cyan]")
                console.print("  2. Check available models: [cyan]/models[/cyan]")
                console.print("  3. See connection status: [cyan]/status[/cyan]")
            else:
                console.print("[yellow]💡 Try being more specific:[/yellow]")
                console.print('  • "Build a module using chain of thought for sentiment analysis"')
                console.print('  • "Create a RAG system with document retrieval"')
                console.print('  • "Generate a ReAct agent for question answering"')
                console.print()
                console.print("  Or use slash commands:")
                console.print("  • [cyan]/explain module[/cyan] - Learn about modules")
                console.print("  • [cyan]/help[/cyan] - See all commands")
            console.print()
            return

        # Store in context
        self.current_context["last_generated"] = module_code
        self.current_context["type"] = "module"

        logger.debug(f"Successfully generated module with {len(module_code)} characters")
        logger.info("✓ Code stored in context - available for /save, /validate, /run")

        # Display the code beautifully
        show_code_panel(module_code, "Generated DSPy Module", "python")

        show_success_message("Module created successfully!")
        console.print("[dim]✓ Code ready - use [cyan]/save <filename>[/cyan] to save it[/dim]")
        console.print()

        # Show RAG tip if disabled
        self._show_rag_tip_if_needed()

        show_next_steps(
            [
                "Type [cyan]/save <filename>[/cyan] to save this code",
                "Type [cyan]/validate[/cyan] to check for errors",
                "Type [cyan]/run[/cyan] to test execution",
                "Type [cyan]/status[/cyan] to see what's in context",
                "Ask me to [green]create a complete program[/green]",
                "Request [yellow]optimizations[/yellow] or improvements",
            ]
        )

        # Suggest LM configuration that matches the connected model
        self._show_lm_configuration_hint()

    def _handle_create_program(self, user_input: str):
        """Handle complete program creation request."""
        console.print("I'll create a complete DSPy program for you!\n")

        # Check if model is connected - REQUIRED
        if not self.llm_connector.current_model:
            show_error_message("No model connected!")
            console.print()
            console.print(
                "[yellow]I need a language model to understand your request and generate code.[/yellow]"
            )
            console.print()
            console.print("[bold]Connect to a model:[/bold]")
            console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print("  [cyan]/connect openai gpt-4[/cyan]")
            console.print("  [cyan]/connect anthropic claude-3-sonnet[/cyan]")
            console.print()
            console.print("[dim]Or configure a default model in dspy_config.yaml[/dim]")
            return

        with EnhancedThinkingAnimation(message_type="code", update_interval=1.5):
            complete_code = self._generate_module_with_llm(user_input)  # Reuse module generation

        if not complete_code or not complete_code.strip():
            logger.error(f"Program generation returned empty result for: {user_input[:50]}...")
            show_error_message("Failed to generate program.")
            console.print()

            # Provide actionable suggestions
            if not self.llm_connector.current_model:
                console.print("[yellow]💡 Suggestions:[/yellow]")
                console.print("  1. Connect to a model: [cyan]/connect ollama llama3.1:8b[/cyan]")
                console.print("  2. Check available models: [cyan]/models[/cyan]")
            else:
                console.print("[yellow]💡 Try being more specific:[/yellow]")
                console.print('  • "Create a complete sentiment analysis program"')
                console.print('  • "Build a question answering system with RAG"')
                console.print('  • "Generate a text classification program"')
                console.print()
                console.print("  Or use: [cyan]/help[/cyan] for all commands")
            console.print()
            return

        # Store in context
        self.current_context["last_generated"] = complete_code
        self.current_context["type"] = "program"

        logger.debug(f"Successfully generated program with {len(complete_code)} characters")
        logger.info("✓ Code stored in context - available for /save, /validate, /run")

        # Display the code beautifully
        show_code_panel(complete_code, "Generated Complete DSPy Program", "python")

        show_success_message("Complete program created!")
        console.print("[dim]✓ Code ready - use [cyan]/save <filename>[/cyan] to save it[/dim]")
        console.print()

        # Show RAG tip if disabled
        self._show_rag_tip_if_needed()

        show_next_steps(
            [
                "Type [cyan]/save <filename>[/cyan] to save this code",
                "Type [cyan]/validate[/cyan] to check for errors",
                "Type [cyan]/run[/cyan] to test execution",
                "Type [cyan]/status[/cyan] to see what's in context",
                "Modify the task description or add examples",
                "Ask me to add [yellow]optimization[/yellow] or [yellow]evaluation[/yellow]",
            ]
        )

        # Suggest LM configuration that matches the connected model
        self._show_lm_configuration_hint()

    def _show_lm_configuration_hint(self) -> None:
        """Print a short hint showing how to configure dspy.LM for the connected model.

        This does not modify the generated code, but gives users a copy-paste snippet
        so they can easily align DSPy LM configuration with the model connected in DSPy Code.
        """
        if not self.llm_connector or not self.llm_connector.current_model:
            return

        model_name = self.llm_connector.current_model
        model_type = getattr(self.llm_connector, "model_type", None)

        if model_type == "ollama":
            console.print(
                "\n[dim]💡 To run this program with your connected Ollama model,"
                " configure DSPy like:[/dim]"
            )
            console.print(
                f'[cyan]lm = dspy.LM(model="ollama/{model_name}", api_base="http://localhost:11434")[/cyan]'
            )
            console.print("[cyan]dspy.configure(lm=lm)[/cyan]\n")
        elif model_type == "openai":
            console.print(
                "\n[dim]💡 To run this program with your connected OpenAI model,"
                " configure DSPy like:[/dim]"
            )
            console.print(
                f'[cyan]lm = dspy.LM(model="openai/{model_name}")[/cyan]\n[cyan]dspy.configure(lm=lm)[/cyan]\n'
            )
        elif model_type == "anthropic":
            console.print(
                "\n[dim]💡 To run this program with your connected Anthropic model,"
                " configure DSPy like:[/dim]"
            )
            console.print(
                f'[cyan]lm = dspy.LM(model="anthropic/{model_name}")[/cyan]\n[cyan]dspy.configure(lm=lm)[/cyan]\n'
            )
        elif model_type == "gemini":
            console.print(
                "\n[dim]💡 To run this program with your connected Gemini model,"
                " configure DSPy like:[/dim]"
            )
            console.print(
                f'[cyan]lm = dspy.LM(model="gemini/{model_name}")[/cyan]\n[cyan]dspy.configure(lm=lm)[/cyan]\n'
            )

    def _extract_data_generation_params(self, user_input: str) -> tuple[str, int]:
        """Extract task description and number of examples from user input.

        Returns:
            Tuple of (task_description, num_examples)
        """
        import re

        # Extract number of examples - look for patterns like "20 examples", "50", etc.
        num_match = re.search(
            r"(\d+)\s*(?:examples?|samples?|data points?|training examples?)",
            user_input,
            re.IGNORECASE,
        )
        if not num_match:
            # Try just a number
            num_match = re.search(r"\b(\d+)\b", user_input)

        num_examples = int(num_match.group(1)) if num_match else 20  # Default to 20
        num_examples = max(5, min(num_examples, 100))  # Limit to reasonable range

        # Extract task description - remove data generation keywords
        task_description = user_input
        # Remove number and "examples" keywords
        task_description = re.sub(
            r"\d+\s*(?:examples?|samples?|data points?|training examples?)",
            "",
            task_description,
            flags=re.IGNORECASE,
        )
        # Remove generation verbs
        task_description = re.sub(
            r"\b(generate|create|make|build)\s+", "", task_description, flags=re.IGNORECASE
        )
        # Remove data-related words
        task_description = re.sub(
            r"\b(data|examples?|samples?|training|gold|synthetic)\s+",
            "",
            task_description,
            flags=re.IGNORECASE,
        )
        # Remove "for" at the start
        task_description = re.sub(r"^\s*for\s+", "", task_description, flags=re.IGNORECASE)
        task_description = task_description.strip()

        # If empty, try to infer from common patterns
        if not task_description or len(task_description) < 3:
            task_types = {
                "sentiment": "sentiment analysis",
                "classification": "text classification",
                "question": "question answering",
                "qa": "question answering",
                "summarization": "text summarization",
                "translation": "translation",
                "email": "email classification",
                "ner": "named entity recognition",
            }

            for key, value in task_types.items():
                if key in user_input.lower():
                    task_description = value
                    break

        # If still empty, use a default
        if not task_description or len(task_description) < 3:
            task_description = "text classification"

        return task_description, num_examples

    def _handle_generate_data(self, user_input: str):
        """Handle data/example generation request."""
        console.print("I'll generate training data for you!\n")

        # Check if model is connected - REQUIRED
        if not self.llm_connector or not self.llm_connector.current_model:
            show_error_message("No model connected!")
            console.print()
            console.print("[yellow]I need a language model to generate training data.[/yellow]")
            console.print()
            console.print("[bold]Connect to a model:[/bold]")
            console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print("  [cyan]/connect openai gpt-4[/cyan]")
            console.print()
            return

        # Extract task and count from user input
        task_description, num_examples = self._extract_data_generation_params(user_input)

        if not task_description:
            console.print(
                "[yellow]I need more information about what kind of data to generate.[/yellow]"
            )
            console.print()
            console.print("Examples:")
            console.print('  "Generate 20 examples for sentiment analysis"')
            console.print('  "Create 50 gold examples for question answering"')
            console.print('  "Make training data for email classification"')
            return

        console.print(f"[cyan]Task:[/cyan] {task_description}")
        console.print(f"[cyan]Examples to generate:[/cyan] {num_examples}")
        console.print()

        with EnhancedThinkingAnimation(
            initial_message=f"🎲 Generating {num_examples} diverse examples...",
            message_type="code",
            update_interval=2.0,
        ):
            examples = self._generate_synthetic_examples(task_description, num_examples)

        if not examples:
            show_error_message("Failed to generate examples. Please try rephrasing your request.")
            return

        # Store in context
        self.current_context["last_generated_data"] = examples
        self.current_context["data_task"] = task_description

        # Display sample
        self._show_example_samples(examples, task_description)

        show_success_message(f"Generated {len(examples)} examples!")

        show_next_steps(
            [
                "Type [cyan]/save-data <filename>[/cyan] to save as JSONL",
                "Ask me to [green]generate more examples[/green]",
                "Use these for [yellow]GEPA optimization[/yellow]",
                "Request [cyan]different types of examples[/cyan]",
            ]
        )

    def _generate_synthetic_examples(
        self, task_description: str, num_examples: int
    ) -> list[dict[str, Any]]:
        """Generate synthetic training examples using LLM.

        Args:
            task_description: Description of the task
            num_examples: Number of examples to generate

        Returns:
            List of example dictionaries with 'input' and 'output' keys
        """
        if not self.llm_connector or not self.llm_connector.current_model:
            logger.warning("No LLM connected for data generation")
            return []

        try:
            # Build prompt for data generation
            prompt = (
                f"Generate {num_examples} diverse, realistic training examples "
                f"for: {task_description}\n\n"
                "Requirements:\n"
                "1. Create varied, realistic examples that cover different scenarios\n"
                "2. Include edge cases and challenging examples\n"
                "3. Make inputs natural and outputs accurate\n"
                "4. Ensure diversity in topics, length, and complexity\n"
                "5. Format as JSON array with 'input' and 'output' keys\n\n"
                "Example format:\n"
                '[{"input": "example input text", "output": "expected output"}]\n\n'
                f"Task: {task_description}\n"
                f"Number of examples: {num_examples}\n\n"
                "Generate ONLY the JSON array, no explanations:"
            )

            # Generate with LLM
            response = self.llm_connector.generate_response(
                prompt=prompt,
                system_prompt=(
                    "You are a data generation expert. "
                    "Generate high-quality, diverse training examples in JSON format."
                ),
                context={},
            )

            # Extract JSON from response
            examples = self._extract_json_from_response(response)

            if examples and isinstance(examples, list):
                logger.info(f"Generated {len(examples)} examples")
                return examples
            else:
                logger.warning("Failed to parse generated examples")
                return []

        except Exception as e:
            logger.error(f"Data generation failed: {e}")
            return []

    def _extract_json_from_response(self, response: str) -> list[dict[str, Any]] | None:
        """Extract JSON array from LLM response."""
        import json
        import re

        try:
            # Try to find JSON array in response
            json_match = re.search(r"\[[\s\S]*\]", response)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)

            # Try parsing entire response
            return json.loads(response)

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from response")
            return None

    def _show_example_samples(self, examples: list[dict[str, Any]], task_description: str = None):
        """Display a sample of generated examples."""
        from rich.table import Table

        console.print()
        console.print(f"[bold cyan]Generated Examples for: {task_description}[/bold cyan]")
        console.print()

        # Show first 5 examples in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Input", style="cyan", width=50)
        table.add_column("Output", style="green", width=30)

        for i, example in enumerate(examples[:5]):
            input_text = str(example.get("input", ""))
            output_text = str(example.get("output", ""))

            # Truncate if too long
            if len(input_text) > 100:
                input_text = input_text[:97] + "..."
            if len(output_text) > 50:
                output_text = output_text[:47] + "..."

            table.add_row(input_text, output_text)

        console.print(table)

        if len(examples) > 5:
            console.print()
            console.print(f"[dim]... and {len(examples) - 5} more examples[/dim]")

        console.print()

    def _handle_optimize(self, user_input: str):
        """Handle optimization request via natural language - routes to /optimize command."""
        # Extract arguments from natural language
        import re

        # Check for file/program reference
        file_match = re.search(
            r'(?:file |program |code |module )["\']?([\w./-]+\.py)["\']?', user_input, re.IGNORECASE
        )
        program_file = file_match.group(1) if file_match else None

        # Check for data file reference
        data_match = re.search(
            r'(?:data |examples |training |with )["\']?([\w./-]+\.(?:jsonl|json))["\']?',
            user_input,
            re.IGNORECASE,
        )
        data_file = data_match.group(1) if data_match else None

        # Check if we have code in context
        has_code = "last_generated" in self.current_context

        # If no file specified and we have code, use context
        if not program_file and has_code:
            # Save code temporarily if needed
            from pathlib import Path

            temp_file = Path("generated") / "temp_optimize.py"
            temp_file.parent.mkdir(exist_ok=True)
            temp_file.write_text(self.current_context["last_generated"])
            program_file = str(temp_file)
            console.print("[dim]Using generated code from context[/dim]")
            console.print()

        # Build command args
        args = []
        if program_file:
            args.append(program_file)
        if data_file:
            args.append(data_file)

        # Route to optimize command
        console.print("[bold cyan]🚀 Starting Optimization[/bold cyan]")
        console.print()
        self.slash_handler.handle_command(f"/optimize {' '.join(args)}")

    def _handle_evaluate(self, user_input: str):
        """Handle evaluation request via natural language - routes to /eval command."""
        # Extract arguments from natural language
        import re

        # Check for file/program reference
        file_match = re.search(
            r'(?:file |program |code |module )["\']?([\w./-]+\.py)["\']?', user_input, re.IGNORECASE
        )
        program_file = file_match.group(1) if file_match else None

        # Check for data file reference
        data_match = re.search(
            r'(?:data |examples |test |dataset |with )["\']?([\w./-]+\.(?:jsonl|json))["\']?',
            user_input,
            re.IGNORECASE,
        )
        data_file = data_match.group(1) if data_match else None

        # Check for metric specification
        metrics = ["accuracy", "f1", "precision", "recall", "rouge", "bleu", "exact_match"]
        specified_metric = None
        for metric in metrics:
            if metric in user_input.lower():
                specified_metric = metric
                break

        # Check if we have code in context
        has_code = "last_generated" in self.current_context

        # If no file specified and we have code, use context
        if not program_file and has_code:
            # Save code temporarily if needed
            from pathlib import Path

            temp_file = Path("generated") / "temp_eval.py"
            temp_file.parent.mkdir(exist_ok=True)
            temp_file.write_text(self.current_context["last_generated"])
            program_file = str(temp_file)
            console.print("[dim]Using generated code from context[/dim]")
            console.print()

        # Build command args
        args = []
        if program_file:
            args.append(program_file)
        if data_file:
            args.append(data_file)
        if specified_metric:
            args.append(f"metric={specified_metric}")

        # Route to eval command
        console.print("[bold cyan]📊 Running Evaluation[/bold cyan]")
        console.print()
        self.slash_handler.handle_command(f"/eval {' '.join(args)}")

    def _handle_explain(self, user_input: str):
        """Handle explanation request via natural language - routes to comprehensive explain system."""
        user_input_lower = user_input.lower().strip()

        # Parse the natural language query to extract the topic
        # This will route to the slash command handler's comprehensive explain system

        # Extract topic from natural language patterns
        topic = None
        category = None

        # Patterns for different question types
        explain_patterns = [
            # Direct questions
            (r"what (is|are) (.+?)(?:\?|$)", 2),
            (r"how (does|do) (.+?) (work|function)", 2),
            (r"explain (.+?)(?: to me| please|$)", 1),
            (r"tell me about (.+?)(?: please|$)", 1),
            (r"describe (.+?)(?: please|$)", 1),
            (r"what does (.+?) (do|mean)", 1),
            (r"(.+?) (explanation|info|information|details)", 1),
        ]

        import re

        for pattern, group_num in explain_patterns:
            match = re.search(pattern, user_input_lower, re.IGNORECASE)
            if match:
                topic = match.group(group_num).strip()
                break

        # If no pattern matched, try to extract topic directly
        if not topic:
            # Remove common question words
            topic = re.sub(
                r"^(what|how|tell|explain|describe|show|give|can you|could you|please)\s+",
                "",
                user_input_lower,
                flags=re.IGNORECASE,
            )
            topic = re.sub(
                r"\s+(is|are|does|do|work|mean|explain|info|information|details|please|\?)$",
                "",
                topic,
                flags=re.IGNORECASE,
            )
            topic = topic.strip()

        # IMPORTANT: If the request contains code generation keywords, it's NOT an explanation request
        # This prevents false positives like "write signature for X" being treated as "explain X"
        # But we need to be careful - questions about signatures/modules should still work
        code_gen_keywords = [
            "write",
            "create",
            "build",
            "make",
            "generate",
            "design",
            "code",
            "program",
        ]
        # Only filter if it's clearly a code generation request (has action verb + topic)
        # Questions like "how do signatures work" should NOT be filtered
        is_code_gen = any(keyword in user_input_lower for keyword in code_gen_keywords) and not any(
            question_word in user_input_lower
            for question_word in ["how", "what", "explain", "tell", "describe", "show me"]
        )
        if is_code_gen:
            # This should have been caught by intent detection, but if it got here, redirect to code generation
            logger.debug(
                "Explain handler detected code generation keywords, redirecting to code generation"
            )
            console.print(
                "[yellow]💡 This looks like a code generation request, not an explanation.[/yellow]"
            )
            console.print()
            # Fall through to general query handler which will generate code
            self._handle_general_query(user_input)
            return

        # Map natural language to known topics
        topic_mappings = {
            # Concepts - handle both singular and plural
            "signature": "signature",
            "signatures": "signature",
            "module": "module",
            "modules": "module",
            # Predictors
            "predict": "Predict",
            "predictor": "Predict",
            "chain of thought": "ChainOfThought",
            "chain-of-thought": "ChainOfThought",
            "cot": "ChainOfThought",
            "react": "ReAct",
            "re-act": "ReAct",
            "program of thought": "ProgramOfThought",
            "program-of-thought": "ProgramOfThought",
            "pot": "ProgramOfThought",
            "codeact": "CodeAct",
            "code act": "CodeAct",
            "code-act": "CodeAct",
            "multichain": "MultiChainComparison",
            "multi chain": "MultiChainComparison",
            "multi-chain": "MultiChainComparison",
            "bestofn": "BestOfN",
            "best of n": "BestOfN",
            "best-of-n": "BestOfN",
            "refine": "Refine",
            "knn": "KNN",
            "k-nn": "KNN",
            "k nearest neighbor": "KNN",
            "parallel": "Parallel",
            # Optimizers
            "gepa": "GEPA",
            "genetic": "GEPA",
            "genetic prompt": "GEPA",
            "mipro": "MIPROv2",
            "mipro v2": "MIPROv2",
            "mipro-v2": "MIPROv2",
            "optimizer": "optimization",
            "optimization": "optimization",
            "optimize": "optimization",
            # Adapters
            "json adapter": "JSONAdapter",
            "jsonadapter": "JSONAdapter",
            "json": "JSONAdapter",
            "xml adapter": "XMLAdapter",
            "xmladapter": "XMLAdapter",
            "xml": "XMLAdapter",
            "chat adapter": "ChatAdapter",
            "chatadapter": "ChatAdapter",
            "chat": "ChatAdapter",
            "two step adapter": "TwoStepAdapter",
            "twostepadapter": "TwoStepAdapter",
            "two-step adapter": "TwoStepAdapter",
            "two step": "TwoStepAdapter",
            "rag": "rag",
            "retrieval": "rag",
            "retrieval augmented generation": "rag",
            "evaluation": "evaluation",
            "eval": "evaluation",
            "metrics": "evaluation",
            "metric": "evaluation",
            "async": "async_streaming",
            "async/await": "async_streaming",
            "streaming": "async_streaming",
            "stream": "async_streaming",
            # General DSPy
            "dspy": "dspy",
            "dspy framework": "dspy",
            "dspy library": "dspy",
            "what is dspy": "dspy",
            "about dspy": "dspy",
        }

        # Check if topic matches a known mapping
        matched_topic = None
        for key, value in topic_mappings.items():
            if key in topic.lower():
                matched_topic = value
                break

        # If no mapping found, try direct match
        if not matched_topic:
            matched_topic = topic

        # Check for "all" or "list" requests
        if any(
            word in user_input_lower for word in ["all", "list", "show all", "what can you explain"]
        ):
            # Show all explainable topics
            self.slash_handler.cmd_explain([])
            return

        # Route to slash command handler's explain system
        # This uses the comprehensive knowledge base
        if matched_topic:
            # Convert to args format for cmd_explain
            args = [matched_topic]
            try:
                self.slash_handler.cmd_explain(args)
            except Exception as e:
                logger.debug(f"Explain error: {e}")
                # Fallback: show help
                console.print("[bold cyan]📖 Explanation Help[/bold cyan]")
                console.print()
                console.print(f"I found topic: [yellow]{matched_topic}[/yellow]")
                console.print()
                console.print(
                    "[dim]Try asking more specifically, or use:[/dim] [yellow]/explain[/yellow]"
                )
                console.print()
        else:
            # Show help if topic not recognized
            console.print("[bold cyan]📖 Explanation Help[/bold cyan]")
            console.print()
            console.print("I can explain many DSPy topics! Try asking:")
            console.print()
            console.print("[bold]Predictors:[/bold]")
            console.print('  • "What is ChainOfThought?"')
            console.print('  • "Explain ReAct predictor"')
            console.print('  • "Tell me about all predictors"')
            console.print()
            console.print("[bold]Optimizers:[/bold]")
            console.print('  • "What is GEPA?"')
            console.print('  • "How does optimization work?"')
            console.print('  • "Explain MIPROv2"')
            console.print()
            console.print("[bold]Adapters:[/bold]")
            console.print('  • "What is JSONAdapter?"')
            console.print('  • "Explain TwoStepAdapter"')
            console.print('  • "How does XMLAdapter work?"')
            console.print()
            console.print("[bold]Concepts:[/bold]")
            console.print('  • "What is a signature?"')
            console.print('  • "Explain RAG"')
            console.print('  • "How does evaluation work?"')
            console.print('  • "What is async/streaming?"')
            console.print()
            console.print("[bold]Retrievers:[/bold]")
            console.print('  • "What is ColBERTv2?"')
            console.print('  • "Explain custom retrievers"')
            console.print()
            console.print("[dim]Or use:[/dim] [yellow]/explain[/yellow] to see all topics")
            console.print()
            console.print()
            for name, info in predictor_info.items():
                console.print(f"  • [cyan]{name}[/cyan] - {info['description']}")
            console.print()
            console.print("[bold]Get details:[/bold]")
            console.print("  • Ask: 'What is ChainOfThought?' or 'Explain ReAct'")
            console.print("  • Or use: [yellow]/predictors[/yellow] to see comparison table")
            console.print("  • Or use: [yellow]/predictors <name>[/yellow] for specific details")
            return

    def _handle_general_query(self, user_input: str):
        """Handle general queries by using LLM with rich context (Claude Code style)."""
        # Always use LLM for responses - no static templates
        if not self.llm_connector.current_model:
            show_error_message("No model connected!")
            console.print()
            console.print("[yellow]I need a language model to help you.[/yellow]")
            console.print()
            console.print("[bold]Connect to a model:[/bold]")
            console.print("  [cyan]/connect ollama llama3.1:8b[/cyan]")
            console.print("  [cyan]/connect openai gpt-4[/cyan]")
            console.print("  [cyan]/models[/cyan] - See all available models")
            console.print()
            return

        # Use LLM to generate response with rich context
        console.print("Let me help you with that!\n")

        # Build comprehensive context for LLM
        reference = self.reference_loader.get_relevant_examples("general")
        context = self._build_context_with_rag(user_input, reference)

        # Build conversational prompt (Claude Code style)
        system_prompt = """You are an expert DSPy assistant, similar to Claude Code.
Your job is to help users with DSPy development by:
- Understanding their requests
- Providing code generation when appropriate
- Explaining concepts when asked
- Guiding them through best practices

You have access to:
- Real DSPy source code examples from the user's installed version
- Template examples (as reference/guidance)
- MCP context (if available)
- Conversation history
- DSPy reference documentation

Always provide helpful, accurate, and context-aware responses."""

        enhanced_prompt = f"""User request: {user_input}

=== CONTEXT AVAILABLE ===
DSPy Codebase Examples:
{context.get("codebase_examples", "None")[:2000]}

Template Examples (Reference):
{context.get("template_examples", "None")[:1500]}

MCP Context:
{context.get("mcp_context", "None")}

DSPy Reference:
{context.get("dspy_reference", "None")[:1000]}

Conversation History:
{context.get("conversation_history", "None")}

=== YOUR TASK ===
Analyze the user's request and provide the most helpful response:
- If they want code: Generate complete, executable DSPy code using real examples as reference
- If they have questions: Answer clearly using the context provided
- If unclear: Ask clarifying questions or provide helpful suggestions

Be conversational, helpful, and use the context to provide accurate information."""

        # Generate response via LLM
        with EnhancedThinkingAnimation(message_type="llm", update_interval=2.0):
            response = self.llm_connector.generate_response(
                prompt=enhanced_prompt, system_prompt=system_prompt, context=context
            )

        # Check if response contains code
        if "```python" in response or "import dspy" in response:
            # Extract and display code
            code = self._extract_code_from_response(response)
            if code and code.strip():
                self.current_context["last_generated"] = code
                self.current_context["type"] = "module"
                show_code_panel(code, "Generated DSPy Code", "python")
                show_success_message("Code generated!")

                # Show RAG tip if disabled
                self._show_rag_tip_if_needed()

                show_next_steps(
                    [
                        "Type [cyan]/save <filename>[/cyan] to save this code",
                        "Ask me to [yellow]modify[/yellow] or [yellow]improve[/yellow] it",
                    ]
                )
            else:
                # Display full response
                console.print(response)
        else:
            # Display conversational response
            console.print(response)
            console.print()

    def _extract_task_from_nl(self, user_input: str) -> TaskDefinition | None:
        """Extract task definition from natural language."""
        # This is a simplified extraction - in production, you'd use the LLM
        # For now, we'll create a basic task definition

        # Try to identify the task type
        task_description = user_input

        # Extract or infer fields
        input_fields = []
        output_fields = []

        # Simple keyword-based extraction
        if "email" in user_input.lower():
            input_fields.append(
                FieldDefinition(
                    name="email_text", type="str", description="The email content to analyze"
                )
            )
            if "classif" in user_input.lower() or "categor" in user_input.lower():
                output_fields.append(
                    FieldDefinition(name="category", type="str", description="The email category")
                )

        elif "text" in user_input.lower() or "document" in user_input.lower():
            input_fields.append(
                FieldDefinition(name="text", type="str", description="The input text")
            )

            if "summar" in user_input.lower():
                output_fields.append(
                    FieldDefinition(name="summary", type="str", description="The generated summary")
                )
            elif "sentiment" in user_input.lower():
                output_fields.append(
                    FieldDefinition(
                        name="sentiment",
                        type="str",
                        description="The sentiment (positive/negative/neutral)",
                    )
                )
            else:
                output_fields.append(
                    FieldDefinition(name="result", type="str", description="The output result")
                )

        elif "question" in user_input.lower():
            input_fields.append(
                FieldDefinition(name="question", type="str", description="The question to answer")
            )
            input_fields.append(
                FieldDefinition(name="context", type="str", description="The context or document")
            )
            output_fields.append(
                FieldDefinition(name="answer", type="str", description="The answer to the question")
            )

        # If we couldn't extract fields, return None
        if not input_fields or not output_fields:
            return None

        return TaskDefinition(
            description=task_description,
            input_fields=input_fields,
            output_fields=output_fields,
            complexity="simple",
        )

    def _extract_reasoning_pattern(self, user_input: str) -> ReasoningPattern:
        """Extract reasoning pattern from natural language."""
        user_input_lower = user_input.lower()

        if "chain of thought" in user_input_lower or "cot" in user_input_lower:
            return ReasoningPattern(type="chain_of_thought")
        elif "react" in user_input_lower:
            return ReasoningPattern(type="react")
        else:
            return ReasoningPattern(type="predict")

    def _build_context_with_rag(self, user_input: str, reference: str) -> dict[str, Any]:
        """Build comprehensive context dictionary with RAG-enhanced code examples.

        Similar to Claude Code/Gemini CLI - provides rich context from:
        - Real DSPy/GEPA source code (via RAG)
        - Template examples (as reference/guidance)
        - MCP context (if available)
        - Conversation history

        Args:
            user_input: User's request
            reference: DSPy reference documentation

        Returns:
            Context dictionary for LLM with comprehensive code examples
        """
        context = {
            "dspy_reference": reference,
            "conversation_history": "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in self.conversation_history[-4:]]
            ),
        }

        # Check if RAG is enabled and not in fast mode
        rag_enabled = self.codebase_rag and self.codebase_rag.enabled and not self._is_fast_mode()

        # Add comprehensive RAG context from DSPy and GEPA source code
        if rag_enabled:
            try:
                # Get config values for performance tuning
                rag_config = self.config_manager.config.codebase_rag
                max_tokens = rag_config.max_context_tokens if rag_config else 4000
                top_k = rag_config.search_top_k if rag_config else 8

                # Get main context
                rag_context = self.codebase_rag.build_context(
                    user_input, max_tokens=max_tokens, top_k=top_k
                )
                if rag_context:
                    context["codebase_examples"] = rag_context
                    logger.debug("Added comprehensive RAG context from DSPy/GEPA source code")

                # Skip pattern-specific searches if configured
                if not (rag_config and rag_config.skip_pattern_searches):
                    # Also get specific examples for common patterns
                    specific_queries = []
                    user_lower = user_input.lower()

                    # Enhanced pattern matching for better context engineering
                    if any(
                        word in user_lower
                        for word in ["retrieve", "rag", "retrieval", "search", "document"]
                    ):
                        specific_queries.append("dspy.Retrieve retrieval RAG")
                    if any(word in user_lower for word in ["react", "agent", "tool", "action"]):
                        specific_queries.append("dspy.ReAct agent tools")
                    if any(
                        word in user_lower
                        for word in ["gepa", "optimize", "optimization", "genetic"]
                    ):
                        specific_queries.append("GEPA Genetic Pareto optimization")
                    if any(word in user_lower for word in ["chain", "thought", "reasoning", "cot"]):
                        specific_queries.append("dspy.ChainOfThought reasoning")
                    if any(
                        word in user_lower for word in ["signature", "input", "output", "field"]
                    ):
                        specific_queries.append("dspy.Signature InputField OutputField")
                    if any(
                        word in user_lower for word in ["mcp", "model context protocol", "server"]
                    ):
                        specific_queries.append("MCP Model Context Protocol client")
                    if any(
                        word in user_lower
                        for word in ["async", "streaming", "streamify", "asyncify"]
                    ):
                        specific_queries.append("dspy async streaming asyncify streamify")
                    if any(word in user_lower for word in ["adapter", "json", "xml", "chat"]):
                        specific_queries.append("dspy adapters JSONAdapter XMLAdapter ChatAdapter")

                    # Get additional context for specific patterns
                    additional_context = []
                    for query in specific_queries[:5]:  # Top 5 specific queries for better coverage
                        specific_context = self.codebase_rag.build_context(
                            query, max_tokens=2000, top_k=5
                        )
                        if specific_context:
                            additional_context.append(
                                f"\n# Additional Context: {query}\n{specific_context}"
                            )

                    if additional_context:
                        context["additional_examples"] = "\n".join(additional_context)
                        logger.debug(f"Added {len(additional_context)} additional context sections")
                else:
                    logger.debug(
                        "Skipping pattern-specific searches (skip_pattern_searches enabled)"
                    )

            except Exception as e:
                logger.warning(f"Failed to get RAG context: {e}")
        else:
            if self.codebase_rag and not self.codebase_rag.enabled:
                logger.debug("RAG disabled in config")
            elif self._is_fast_mode():
                logger.debug("Fast mode enabled - skipping RAG context")

        # Add template examples as reference (not direct responses)
        try:
            template_context = self._build_template_context(user_input)
            if template_context:
                context["template_examples"] = template_context
                logger.debug("Added template examples as reference")
        except Exception as e:
            logger.warning(f"Failed to get template context: {e}")

        # Add MCP context if available
        try:
            mcp_context = self._build_mcp_context(user_input)
            if mcp_context:
                context["mcp_context"] = mcp_context
                logger.debug("Added MCP context")
        except Exception as e:
            logger.warning(f"Failed to get MCP context: {e}")

        return context

    def _is_fast_mode(self) -> bool:
        """Check if fast mode is enabled."""
        try:
            rag_config = self.config_manager.config.codebase_rag
            return rag_config.fast_mode if rag_config else True  # Default to enabled
        except:
            return True  # Default to enabled

    def _show_rag_tip_if_needed(self):
        """Show tip to enable RAG if it's disabled."""
        # Only show once per session
        if hasattr(self, "_rag_tip_shown"):
            return

        try:
            rag_config = self.config_manager.config.codebase_rag
            rag_enabled = rag_config.enabled if rag_config else False
            fast_mode = rag_config.fast_mode if rag_config else True

            # Only show if RAG is disabled
            if rag_enabled:
                return

            console.print()
            console.print(
                "[yellow]💡 Tip:[/yellow] Want better code quality? "
                "[cyan]/enable-rag[/cyan] and [cyan]/fast-mode off[/cyan] "
                "(slower but more accurate)"
            )
            console.print("[dim]   Current: Fast mode ON, RAG OFF - quick responses[/dim]")
            console.print("[dim]   Better: RAG ON, Fast mode OFF - slower but higher quality[/dim]")
            console.print()

            self._rag_tip_shown = True
        except Exception:
            pass

    def _show_performance_tip_if_needed(self, generation_time: float):
        """Show performance tip after slow response."""
        # Only show once per session
        if hasattr(self, "_performance_tip_shown"):
            return

        # Only show if RAG enabled and fast mode disabled
        if not (self.codebase_rag and self.codebase_rag.enabled):
            return

        if self._is_fast_mode():
            return

        console.print()
        console.print(
            f"[dim]⏱️  That took {generation_time:.1f}s. "
            f"Want faster? Try [cyan]/fast-mode on[/cyan] "
            f"(0.5-1s responses, slightly lower quality)[/dim]"
        )
        console.print("[dim]   Or check [cyan]/status[/cyan] for all performance settings[/dim]")
        console.print()

        self._performance_tip_shown = True

    def _build_template_context(self, user_input: str) -> str:
        """Build template context as reference for LLM.

        Uses pattern matching to find relevant templates and includes them
        as reference examples (not direct responses).

        Args:
            user_input: User's request

        Returns:
            Formatted template examples as reference
        """
        try:
            from ..templates.adapters import AdapterTemplates
            from ..templates.async_streaming import AsyncStreamingTemplates
            from ..templates.complete_programs import CompleteProgramTemplates
            from ..templates.industry_templates import IndustryTemplates

            user_lower = user_input.lower()
            template_parts = []

            # Search for relevant templates using pattern matching
            complete_templates = CompleteProgramTemplates()
            industry_templates = IndustryTemplates()

            # Find matching templates
            matching_templates = []

            # Check complete program templates
            for template in complete_templates.list_all():
                if any(kw in user_lower for kw in template.keywords):
                    matching_templates.append(("complete", template.name, template.description))

            # Check industry templates
            for template in industry_templates.list_all():
                if any(kw in user_lower for kw in template.keywords):
                    matching_templates.append(("industry", template.name, template.description))

            # Add relevant template code as reference (limit to top 2 most relevant)
            if matching_templates:
                template_parts.append(
                    "# Relevant Template Examples (for reference only - use as guidance):\n"
                )
                for template_type, template_name, description in matching_templates[:2]:
                    try:
                        if template_type == "complete":
                            template_code = complete_templates.get_template_code(template_name)
                        else:
                            template_code = industry_templates.get_template_code(template_name)

                        if template_code:
                            template_parts.append(f"\n## Template: {description}\n")
                            template_parts.append("```python")
                            # Include first 100 lines of template as reference
                            template_lines = template_code.split("\n")[:100]
                            template_parts.append("\n".join(template_lines))
                            template_parts.append("```\n")
                            template_parts.append(
                                "# Use this template as a reference for structure and patterns\n"
                            )
                    except Exception as e:
                        logger.debug(f"Failed to load template {template_name}: {e}")

            # Add adapter templates if relevant
            if any(word in user_lower for word in ["adapter", "json", "xml", "chat"]):
                adapters = AdapterTemplates()
                adapter_types = []
                if "json" in user_lower:
                    adapter_types.append(("json", adapters._generate_json()))
                elif "xml" in user_lower:
                    adapter_types.append(("xml", adapters._generate_xml()))
                elif "chat" in user_lower:
                    adapter_types.append(("chat", adapters._generate_chat()))

                if adapter_types:
                    template_parts.append("\n# Adapter Template Examples (for reference):\n")
                    for adapter_name, adapter_code in adapter_types[:1]:  # Limit to 1
                        template_parts.append(f"## {adapter_name.upper()}Adapter Example:\n")
                        template_parts.append("```python")
                        template_lines = adapter_code.split("\n")[:80]
                        template_parts.append("\n".join(template_lines))
                        template_parts.append("```\n")

            # Add async/streaming templates if relevant
            if any(
                word in user_lower
                for word in ["async", "streaming", "stream", "asyncify", "streamify"]
            ):
                async_templates = AsyncStreamingTemplates()
                if "async" in user_lower or "asyncify" in user_lower:
                    async_code = async_templates._generate_asyncify()
                    template_parts.append("\n# Async Template Example (for reference):\n")
                    template_parts.append("```python")
                    template_lines = async_code.split("\n")[:80]
                    template_parts.append("\n".join(template_lines))
                    template_parts.append("```\n")
                elif "stream" in user_lower or "streamify" in user_lower:
                    stream_code = async_templates._generate_streamify()
                    template_parts.append("\n# Streaming Template Example (for reference):\n")
                    template_parts.append("```python")
                    template_lines = stream_code.split("\n")[:80]
                    template_parts.append("\n".join(template_lines))
                    template_parts.append("```\n")

            return "\n".join(template_parts) if template_parts else ""

        except Exception as e:
            logger.warning(f"Failed to build template context: {e}")
            return ""

    def _build_mcp_context(self, user_input: str) -> str:
        """Build MCP context if MCP servers are available.

        Args:
            user_input: User's request

        Returns:
            MCP context information
        """
        try:
            if not self.slash_handler or not self.slash_handler.mcp_manager:
                return ""

            mcp_manager = self.slash_handler.mcp_manager
            user_lower = user_input.lower()

            # Check if user is asking about MCP or if MCP servers are available
            if "mcp" in user_lower or "model context protocol" in user_lower:
                mcp_parts = []
                mcp_parts.append("# MCP (Model Context Protocol) Context:\n")

                # Get available servers
                if mcp_manager.server_configs:
                    mcp_parts.append(
                        f"Available MCP servers: {', '.join(mcp_manager.server_configs.keys())}\n"
                    )
                    mcp_parts.append("MCP allows connecting to external tools and services.\n")
                    mcp_parts.append(
                        "Use MCP servers to extend DSPy programs with external capabilities.\n"
                    )
                else:
                    mcp_parts.append(
                        "No MCP servers configured. MCP can extend DSPy with external tools.\n"
                    )

                return "\n".join(mcp_parts)

            return ""

        except Exception as e:
            logger.debug(f"Failed to build MCP context: {e}")
            return ""

    def _generate_signature_with_llm(self, user_input: str) -> str:
        """Generate signature code using connected LLM."""

        # If model is connected, use it
        if self.llm_connector.current_model:
            try:
                # Load DSPy reference for signatures
                reference = self.reference_loader.get_relevant_examples("create_signature")

                # Build comprehensive system prompt with DSPy context
                system_prompt = """You are an expert DSPy code generator, similar to Claude Code or Gemini CLI.
Your job is to generate high-quality, production-ready DSPy Signatures based on the user's request.

You have access to:
- Real DSPy source code examples from the user's installed version
- DSPy reference documentation
- Conversation history
- Best practices from the DSPy codebase

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Output ONLY valid, executable Python code - NO markdown, NO explanations, NO pseudo code
2. Generate COMPLETE, RUNNABLE code - not templates, not examples, not placeholders
3. Use the EXACT DSPy syntax from the user's installed version (check codebase examples)
4. Include descriptive field descriptions that explain what each field represents
5. Use meaningful, task-specific class and field names (not generic "input"/"output")
6. Add a comprehensive docstring explaining the signature's purpose
7. Always start with: import dspy
8. Follow patterns from the provided codebase examples
9. DO NOT generate pseudo code, placeholders, or incomplete code
10. Generate REAL, WORKING code that can be used immediately

SIGNATURE PATTERNS (use codebase examples as reference):
- Simple signatures: InputField(s) → OutputField(s)
- Multi-input signatures: Multiple InputFields → Single or multiple OutputFields
- Complex signatures: Nested structures, optional fields

Generate COMPLETE, EXECUTABLE code that matches the user's ACTUAL task, using field names that make sense for their use case."""

                # Build comprehensive context with RAG (DSPy + GEPA source code)
                # This is CRITICAL - provides real DSPy examples from user's installed version
                context = self._build_context_with_rag(user_input, reference)

                # Build enhanced user prompt with rich DSPy context (Claude Code style)
                enhanced_prompt = f"""Generate a COMPLETE, EXECUTABLE DSPy Signature based on this request:

{user_input}

CRITICAL INSTRUCTIONS (Claude Code Style):
- You are an expert DSPy code generator with access to comprehensive context
- Use REAL DSPy source code examples as your PRIMARY reference (from user's installed version)
- Template examples are provided as REFERENCE/GUIDANCE only - adapt them, don't copy them
- Generate REAL, WORKING code tailored to the user's specific request - NOT generic templates
- The codebase examples below are from actual DSPy source code - follow their style exactly

=== REAL DSPy SOURCE CODE EXAMPLES (Primary Reference) ===
{context.get("codebase_examples", "No codebase examples available - use standard DSPy patterns")}

=== ADDITIONAL PATTERN-SPECIFIC EXAMPLES ===
{context.get("additional_examples", "")}

=== TEMPLATE EXAMPLES (Reference Only - Adapt, Don't Copy) ===
{context.get("template_examples", "")}

=== DSPy REFERENCE DOCUMENTATION ===
{context.get("dspy_reference", "")}

=== CONVERSATION HISTORY ===
{context.get("conversation_history", "")}

REQUIREMENTS:
1. Analyze the user's request carefully - understand their SPECIFIC needs
2. Use codebase examples as PRIMARY reference for syntax and patterns
3. Use template examples as GUIDANCE for structure (adapt to user's needs)
4. Generate COMPLETE, RUNNABLE code tailored to the user's task
5. Include ALL necessary imports
6. Make it production-ready and executable
7. Match the user's specific task (not generic templates)
8. Use meaningful class and field names that match the task

OUTPUT FORMAT:
- Output ONLY valid Python code
- NO markdown, NO explanations, NO pseudo code
- Complete, executable code that can run immediately

Generate code that ACTUALLY solves the user's specific problem using real DSPy patterns!"""

                # Generate with LLM (track time for performance tips)
                import time

                start_time = time.time()

                response = self.llm_connector.generate_response(
                    prompt=enhanced_prompt, system_prompt=system_prompt, context=context
                )

                generation_time = time.time() - start_time

                # Show performance tip if slow
                if generation_time > 3.0:
                    self._show_performance_tip_if_needed(generation_time)

                # Extract code from response
                code = self._extract_code_from_response(response)

                # If code extraction failed, try the raw response
                if not code or not code.strip():
                    code = response

                # Validate that we got actual code
                if code and code.strip():
                    if "import" in code and ("class" in code or "def" in code):
                        logger.debug(
                            f"Successfully generated signature with {len(code)} characters"
                        )
                        return code
                    else:
                        # Try to extract from markdown if present
                        import re

                        code_blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", code, re.DOTALL)
                        if code_blocks:
                            return code_blocks[0].strip()

                logger.warning("Signature generation returned empty or invalid code")
                return None

            except Exception as e:
                logger.error(f"LLM generation failed: {e}", exc_info=True)
                return None

        # No model connected
        return None

    def _generate_module_with_llm(self, user_input: str) -> str:
        """Generate module code using connected LLM with DSPy context.

        ALWAYS uses LLM - no template fallback. Requires model connection.
        """

        # REQUIRED: Model must be connected - no template fallback
        if not self.llm_connector.current_model:
            logger.warning("No model connected - cannot generate code without LLM")
            return None

        # ALWAYS use LLM with DSPy context
        if self.llm_connector.current_model:
            try:
                # Load DSPy reference for modules
                reference = self.reference_loader.get_relevant_examples("create_module")

                # Build comprehensive system prompt like Claude Code/Gemini CLI
                system_prompt = """You are an expert DSPy code generator, similar to Claude Code or Gemini CLI.
Your job is to generate high-quality, production-ready DSPy Modules based on the user's request.

You have access to:
- Real DSPy source code from the user's installed version (via codebase examples)
- Real GEPA optimization code examples
- DSPy reference documentation
- Conversation history
- Best practices from the actual DSPy and GEPA codebases

CRITICAL RULES - YOU MUST FOLLOW THESE EXACTLY:
1. Output ONLY valid, executable Python code - NO markdown, NO explanations, NO pseudo code, NO comments like "# TODO" or "# FIXME"
2. Generate COMPLETE, RUNNABLE code that can be executed immediately - not templates, not examples, not pseudo code
3. Use the EXACT DSPy syntax from the user's installed version (check codebase examples)
4. Understand the user's ACTUAL intent - analyze their request carefully
5. Include proper imports and complete, production-ready code
6. Follow patterns from the provided codebase examples (they're from real DSPy/GEPA source)
7. Use meaningful class and method names that match the user's task
8. DO NOT generate pseudo code, placeholders, or incomplete code
9. DO NOT use comments like "# Your code here" or "# Implement this"
10. Generate REAL, WORKING code that can be copied and run immediately

DSPy PATTERNS (use codebase examples as primary reference):

**Retrieval/RAG Systems**:
```python
import dspy

class RAGSignature(dspy.Signature):
    question = dspy.InputField()
    context = dspy.InputField()
    answer = dspy.OutputField()

class RAGModule(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(RAGSignature)

    def forward(self, question):
        context = self.retrieve(question).passages
        answer = self.generate_answer(question=question, context=context)
        return answer
```

**ReAct Agents with Tools**:
```python
import dspy

class AgentSignature(dspy.Signature):
    task = dspy.InputField()
    result = dspy.OutputField()

class AgentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.react = dspy.ReAct(AgentSignature, tools=[search_tool, calculator_tool])

    def forward(self, task):
        result = self.react(task=task)
        return result
```

**Chain of Thought**:
```python
import dspy

class TaskSignature(dspy.Signature):
    input_text = dspy.InputField()
    output = dspy.OutputField()

class TaskModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(TaskSignature)

    def forward(self, input_text):
        result = self.predictor(input_text=input_text)
        return result.output
```

ANALYZE THE USER'S REQUEST CAREFULLY:
- If they mention "retrieval", "RAG", "documents", "search" → Use dspy.Retrieve (check codebase examples)
- If they mention "agent", "tools", "actions" → Use dspy.ReAct with actual tools (check codebase examples)
- If they mention "reasoning", "thinking", "steps" → Use dspy.ChainOfThought (check codebase examples)
- If they mention "program", "code", "math" → Use dspy.ProgramOfThought (check codebase examples)
- If they mention "optimize", "gepa", "genetic" → Reference GEPA examples from codebase
- Match field names to their actual task (not generic "text" and "result")
- Use the codebase examples as your PRIMARY reference - they're from real DSPy/GEPA source code

IMPORTANT:
- The codebase examples provided are from the user's ACTUAL installed DSPy and GEPA versions
- Use those examples as your guide for syntax, patterns, and best practices
- Generate code that matches the patterns in the codebase examples
- Make it production-ready, following the style and structure from the examples

ABSOLUTELY FORBIDDEN:
- NO pseudo code (e.g., "# Function to do X" without implementation)
- NO placeholders (e.g., "# TODO: implement this")
- NO incomplete code (e.g., "def forward(self, x): pass")
- NO explanations mixed with code
- NO markdown formatting in code output

REQUIRED:
- Complete, executable Python code
- All functions and methods fully implemented
- Proper error handling where appropriate
- Code that can be run immediately without modification

Generate REAL, COMPLETE, EXECUTABLE code that ACTUALLY does what the user asked for, using real patterns from DSPy and GEPA source code!"""

                # Build comprehensive context with RAG (DSPy + GEPA source code)
                context = self._build_context_with_rag(user_input, reference)

                # Build enhanced user prompt with rich DSPy context (Claude Code style)
                enhanced_prompt = f"""Generate a COMPLETE, EXECUTABLE DSPy program based on this request:

{user_input}

CRITICAL INSTRUCTIONS (Claude Code Style):
- You are an expert DSPy code generator with access to comprehensive context
- Use REAL DSPy source code examples as your PRIMARY reference (from user's installed version)
- Template examples are provided as REFERENCE/GUIDANCE only - adapt them, don't copy them
- Generate REAL, WORKING code tailored to the user's specific request - NOT generic templates
- The codebase examples below are from actual DSPy/GEPA/MCP source code - follow their style exactly

=== REAL DSPy SOURCE CODE EXAMPLES (Primary Reference) ===
{context.get("codebase_examples", "No codebase examples available - use standard DSPy patterns")}

=== ADDITIONAL PATTERN-SPECIFIC EXAMPLES ===
{context.get("additional_examples", "")}

=== TEMPLATE EXAMPLES (Reference Only - Adapt, Don't Copy) ===
{context.get("template_examples", "")}

=== MCP CONTEXT (If Relevant) ===
{context.get("mcp_context", "")}

=== DSPy REFERENCE DOCUMENTATION ===
{context.get("dspy_reference", "")}

=== CONVERSATION HISTORY ===
{context.get("conversation_history", "")}

REQUIREMENTS:
1. Analyze the user's request carefully - understand their SPECIFIC needs
2. Use codebase examples as PRIMARY reference for syntax and patterns
3. Use template examples as GUIDANCE for structure (adapt to user's needs)
4. Generate COMPLETE, RUNNABLE code tailored to the user's task
5. Include ALL necessary imports and implementations
6. Make it production-ready and executable
7. Match the user's specific task (not generic templates)
8. Use meaningful class and method names that match the task

OUTPUT FORMAT:
- Output ONLY valid Python code
- NO markdown, NO explanations, NO pseudo code
- Complete, executable code that can run immediately

Generate code that ACTUALLY solves the user's specific problem using real DSPy patterns!"""

                # Generate with LLM (track time for performance tips)
                import time

                start_time = time.time()

                response = self.llm_connector.generate_response(
                    prompt=enhanced_prompt, system_prompt=system_prompt, context=context
                )

                generation_time = time.time() - start_time

                # Show performance tip if slow
                if generation_time > 3.0:
                    self._show_performance_tip_if_needed(generation_time)

                # Extract code from response
                code = self._extract_code_from_response(response)

                # If code extraction failed, try the raw response
                if not code or not code.strip():
                    code = response

                # Validate that we got actual code, not pseudo code or explanations
                if code and code.strip():
                    import re

                    # Only check for truly incomplete code - be lenient
                    # Check if forward method has ONLY 'pass' (definitely incomplete)
                    forward_pass_pattern = r"def forward\([^)]+\):\s*\n\s+pass\s*(?:\n|$)"
                    has_incomplete_forward = bool(
                        re.search(forward_pass_pattern, code, re.MULTILINE)
                    )

                    # Check for NotImplementedError (definitely incomplete)
                    has_not_implemented = "raise NotImplementedError" in code

                    # Check for obvious placeholders
                    has_placeholder = any(
                        ph in code
                        for ph in [
                            "# Your code here",
                            "# Placeholder for",
                            "# TODO: implement",
                            "# FIXME: implement",
                        ]
                    )

                    # Only retry if we have truly incomplete code
                    if has_incomplete_forward or has_not_implemented or has_placeholder:
                        logger.warning("Detected incomplete code - retrying with stronger prompt")
                        # Build a more focused retry prompt
                        retry_prompt = f"""Generate a COMPLETE, EXECUTABLE DSPy program for email classification.

The previous attempt had incomplete code. Generate FULL, WORKING code:

1. Signature class with email fields (subject, body) and category output
2. Module class with fully implemented forward() method (NO 'pass', NO placeholders)
3. Complete implementation that can run immediately

{context.get("codebase_examples", "")}

Generate ONLY the complete Python code - no explanations, no markdown:"""

                        try:
                            retry_response = self.llm_connector.generate_response(
                                prompt=retry_prompt, system_prompt=system_prompt, context=context
                            )
                            code = self._extract_code_from_response(retry_response)
                            if not code or not code.strip():
                                code = retry_response

                            # Check retry result - if still incomplete, accept it anyway (better than nothing)
                            if code and code.strip():
                                # Final check: does it have basic structure?
                                has_import = "import dspy" in code or "from dspy" in code
                                has_class = "class" in code
                                has_forward = "def forward" in code

                                if has_import and has_class:
                                    logger.debug(
                                        f"Generated {len(code)} characters of code (after retry)"
                                    )
                                    return code
                        except Exception as e:
                            logger.warning(f"Retry failed: {e}, using original code")
                            # Fall through to accept original code

                    # Check if it looks like actual code (has imports, classes, etc.)
                    if "import" in code and ("class" in code or "def" in code):
                        # Basic validation: has structure
                        has_import = "import dspy" in code or "from dspy" in code
                        has_class = "class" in code

                        if has_import and has_class:
                            logger.debug(f"Successfully generated {len(code)} characters of code")
                            return code
                        else:
                            logger.warning(
                                f"Code missing basic structure: import={has_import}, class={has_class}"
                            )
                    else:
                        logger.warning(f"LLM response doesn't look like code: {code[:200]}...")
                        # Try to extract code from markdown blocks if present
                        code_blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", code, re.DOTALL)
                        if code_blocks:
                            extracted = code_blocks[0].strip()
                            # Basic validation
                            if "import" in extracted and (
                                "class" in extracted or "def" in extracted
                            ):
                                return extracted

                logger.warning("LLM generation returned empty or invalid code")
                return None

            except Exception as e:
                logger.error(f"LLM generation failed: {e}", exc_info=True)
                return None

        # No model connected - don't fall back to templates, require model
        logger.warning("No model connected - cannot generate code")
        return None

    def _generate_basic_module_template(self, user_input: str) -> str:
        """Generate a basic module template when all else fails."""

        # Extract task name from input
        user_lower = user_input.lower()

        # CRITICAL: Check for ReAct FIRST before determining task type
        # This ensures ReAct agents always get tools
        predictor, predictor_comment = self._select_predictor(user_lower)

        # Determine task type
        if "sentiment" in user_lower:
            task_name = "SentimentAnalysis"
            input_field = "text"
            output_field = "sentiment"
            desc = "Analyze sentiment of text"
            example_input = "I love this product!"
            example_output = "positive"
        elif "classif" in user_lower or "categor" in user_lower:
            task_name = "TextClassification"
            input_field = "text"
            output_field = "category"
            desc = "Classify text into categories"
            example_input = "The stock market rose today"
            example_output = "business"
        elif "question" in user_lower or "answer" in user_lower:
            task_name = "QuestionAnswering"
            input_field = "question"
            output_field = "answer"
            desc = "Answer questions"
            example_input = "What is the capital of France?"
            example_output = "Paris"
        elif "summar" in user_lower:
            task_name = "TextSummarization"
            input_field = "text"
            output_field = "summary"
            desc = "Summarize text"
            example_input = "Long article text..."
            example_output = "Brief summary"
        elif "research" in user_lower:
            task_name = "Research"
            input_field = "query"
            output_field = "findings"
            desc = "Research and find information"
            example_input = "What are the latest developments in AI?"
            example_output = "Recent AI developments include..."
        else:
            task_name = "TextProcessing"
            input_field = "text"
            output_field = "result"
            desc = "Process text"
            example_input = "Sample input"
            example_output = "Processed output"

        # CRITICAL: If ReAct is selected, ALWAYS generate with tools!
        if predictor == "dspy.ReAct":
            return self._generate_react_program(
                task_name,
                input_field,
                output_field,
                desc,
                example_input,
                example_output,
                predictor_comment,
            )

        return f'''import dspy

class {task_name}Signature(dspy.Signature):
    """{desc}."""

    {input_field} = dspy.InputField(desc="The input {input_field}")
    {output_field} = dspy.OutputField(desc="The {output_field}")

class {task_name}Module(dspy.Module):
    """{desc} module.

    {predictor_comment}
    """

    def __init__(self):
        super().__init__()
        self.predictor = {predictor}({task_name}Signature)

    def forward(self, {input_field}):
        """Process the input and return the {output_field}."""
        result = self.predictor({input_field}={input_field})
        return result.{output_field}'''

    def _generate_complete_program(self, user_input: str) -> str:
        """Generate a complete, runnable DSPy program."""

        user_lower = user_input.lower()

        # Determine task details
        if "sentiment" in user_lower:
            task_name = "SentimentAnalysis"
            input_field = "text"
            output_field = "sentiment"
            desc = "Analyze the sentiment of text"
            example_input = "I love this product! It's amazing."
            example_output = "positive"
        elif "classif" in user_lower or "categor" in user_lower:
            task_name = "TextClassification"
            input_field = "text"
            output_field = "category"
            desc = "Classify text into categories"
            example_input = "The stock market rose 5% today."
            example_output = "business"
        elif "question" in user_lower or "answer" in user_lower or "qa" in user_lower:
            task_name = "QuestionAnswering"
            input_field = "question"
            output_field = "answer"
            desc = "Answer questions based on context"
            example_input = "What is the capital of France?"
            example_output = "Paris"
        elif "summar" in user_lower:
            task_name = "TextSummarization"
            input_field = "text"
            output_field = "summary"
            desc = "Summarize long text into concise form"
            example_input = "Long article text here..."
            example_output = "Brief summary of the article."
        elif "translat" in user_lower:
            task_name = "Translation"
            input_field = "text"
            output_field = "translation"
            desc = "Translate text to another language"
            example_input = "Hello, how are you?"
            example_output = "Bonjour, comment allez-vous?"
        else:
            task_name = "TextProcessing"
            input_field = "text"
            output_field = "result"
            desc = "Process text and generate output"
            example_input = "Sample input text"
            example_output = "Processed output"

        # Select predictor (default to ChainOfThought if not specified)
        predictor, predictor_comment = self._select_predictor(user_lower)

        # CRITICAL: Check if ReAct FIRST - needs special handling with tools
        if predictor == "dspy.ReAct":
            return self._generate_react_program(
                task_name,
                input_field,
                output_field,
                desc,
                example_input,
                example_output,
                predictor_comment,
            )

        # If no specific predictor mentioned, use ChainOfThought as default
        if predictor == "dspy.Predict" and not any(
            kw in user_lower for kw in ["predict", "simple", "fast", "direct"]
        ):
            predictor = "dspy.ChainOfThought"
            predictor_comment = (
                "Uses ChainOfThought: Provides step-by-step reasoning (default for better quality)."
            )

        # Generate complete program with all components
        return f'''"""
{task_name} - Complete DSPy Program

This program demonstrates how to use DSPy for {desc.lower()}.
Generated by DSPy Code.
"""

import dspy

# ============================================================================
# 1. SIGNATURE - Defines the task interface
# ============================================================================

class {task_name}Signature(dspy.Signature):
    """{desc}."""

    {input_field} = dspy.InputField(desc="The input {input_field}")
    {output_field} = dspy.OutputField(desc="The {output_field}")


# ============================================================================
# 2. MODULE - Implements the task logic
# ============================================================================

class {task_name}Module(dspy.Module):
    """{desc} module.

    {predictor_comment}
    """

    def __init__(self):
        super().__init__()
        self.predictor = {predictor}({task_name}Signature)

    def forward(self, {input_field}):
        """Process the input and return the {output_field}."""
        result = self.predictor({input_field}={input_field})
        return result.{output_field}


# ============================================================================
# 3. CONFIGURATION - Set up the language model
# ============================================================================

{self._get_enhanced_config_section()}


# ============================================================================
# 4. MAIN PROGRAM - Run the task
# ============================================================================

def main():
    """Main program execution."""

    # Configure DSPy
    print("Setting up DSPy...")
    configure_dspy()
    print()

    # Create the module
    print("Creating {task_name} module...")
    module = {task_name}Module()
    print("✓ Module created")
    print()

    # Example usage
    print("Running example...")
    print("-" * 60)

    example_{input_field} = "{example_input}"
    print(f"Input: {{example_{input_field}}}")
    print()

    # Run the module
    result = module({input_field}=example_{input_field})

    print(f"Output: {{result}}")
    print("-" * 60)
    print()

    # Interactive mode
    print("Try your own inputs (Ctrl+C to exit):")
    try:
        while True:
            user_{input_field} = input("\\n{input_field.capitalize()}: ").strip()
            if not user_{input_field}:
                continue

            result = module({input_field}=user_{input_field})
            print(f"{output_field.capitalize()}: {{result}}")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 5. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE THIS PROGRAM:

1. Add Evaluation:
   - Create test examples with expected outputs
   - Use dspy.Evaluate to measure accuracy

2. Optimize with GEPA:
   - Collect training examples
   - Run: optimizer = dspy.GEPA(metric=your_metric)
   - optimized = optimizer.compile(module, trainset=examples)

3. Add More Features:
   - Handle edge cases
   - Add input validation
   - Implement error handling
   - Add logging

4. Deploy:
   - Save the optimized module: dspy.save(module, 'model.json')
   - Load in production: module = dspy.load('model.json')
"""


if __name__ == "__main__":
    main()
'''

    def _get_enhanced_config_section(self) -> str:
        """Get enhanced configuration section with all LM options."""
        return '''def configure_dspy():
    """Configure DSPy with a language model."""

    # ========================================================================
    # OPTION 1: Ollama (Local, Free, Recommended for Getting Started)
    # ========================================================================
    # Requires: Ollama installed and running (ollama serve)
    # Install: https://ollama.ai/download
    # Models: ollama pull gpt-oss:20b

    # DSPy 3.0+ uses the unified LM interface
    lm = dspy.LM(model='ollama/gpt-oss:20b')

    # ========================================================================
    # OPTION 2: OpenAI (Cloud-based, Requires API Key)
    # ========================================================================
    # Get API key: https://platform.openai.com/api-keys
    # Set environment variable: export OPENAI_API_KEY=sk-...

    # lm = dspy.LM(model='openai/gpt-5.1')

    # Other OpenAI models:
    # lm = dspy.LM(model='openai/gpt-4o')
    # lm = dspy.LM(model='openai/gpt-4o-mini')
    # lm = dspy.LM(model='openai/o1')  # Reasoning model
    # lm = dspy.LM(model='openai/o3-mini')  # Latest reasoning model

    # ========================================================================
    # OPTION 3: Anthropic Claude (Cloud-based, Requires API Key)
    # ========================================================================
    # Get API key: https://console.anthropic.com/
    # Set environment variable: export ANTHROPIC_API_KEY=sk-ant-...

    # lm = dspy.LM(model='anthropic/claude-4.5-sonnet')

    # Other Claude models:
    # lm = dspy.LM(model='anthropic/claude-4.5-opus')
    # lm = dspy.LM(model='anthropic/claude-3-5-sonnet-20241022')

    # ========================================================================
    # OPTION 4: Google Gemini (Cloud-based, Requires API Key)
    # ========================================================================
    # Get API key: https://makersuite.google.com/app/apikey
    # Set environment variable: export GOOGLE_API_KEY=AIza...

    # lm = dspy.LM(model='gemini/gemini-pro-2.5')

    # Other Gemini models:
    # lm = dspy.LM(model='gemini/gemini-2.0-flash-exp')
    # lm = dspy.LM(model='gemini/gemini-1.5-pro')

    # ========================================================================
    # OPTION 5: Azure OpenAI (Enterprise, Requires Deployment)
    # ========================================================================
    # Requires: Azure OpenAI resource and deployment
    # Set environment variables: AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION

    # lm = dspy.LM(
    #     model='azure/your-deployment-name',
    #     api_base='https://your-resource.openai.azure.com/',
    #     api_version='2024-02-15-preview'
    # )

    # ========================================================================
    # Configure DSPy with selected model (DSPy 3.0+)
    # ========================================================================
    dspy.configure(lm=lm)
    print(f"✓ Configured DSPy with {lm.model}")
    print(f"  Provider: LM")

    return lm'''

    def _generate_react_program(
        self,
        task_name: str,
        input_field: str,
        output_field: str,
        desc: str,
        example_input: str,
        example_output: str,
        predictor_comment: str,
    ) -> str:
        """Generate a complete ReAct program with example tools."""

        return f'''"""
{task_name}Agent - Complete DSPy ReAct Program with Tools

This program demonstrates how to use DSPy ReAct for {desc.lower()} with tools.
Generated by DSPy Code.
"""

import dspy
from dspy import Tool

# ============================================================================
# 1. DEFINE TOOLS - Functions the agent can use
# ============================================================================

def search_tool(query: str) -> str:
    """
    Search for information on the web.

    Args:
        query: The search query

    Returns:
        Search results as a string
    """
    # In a real implementation, this would call a search API
    # For demo purposes, we return a mock response
    return f"Search results for '{{query}}': [Mock search results would appear here]"


def calculator_tool(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation
    """
    try:
        # Safe evaluation of mathematical expressions
        result = eval(expression, {{"__builtins__": {{}}}}, {{}})
        return f"Result: {{result}}"
    except Exception as e:
        return f"Error: {{str(e)}}"


def get_current_info(topic: str) -> str:
    """
    Get current information about a topic.

    Args:
        topic: The topic to get information about

    Returns:
        Current information about the topic
    """
    # In a real implementation, this would fetch real-time data
    return f"Current information about '{{topic}}': [Mock current data would appear here]"


# ============================================================================
# 2. SIGNATURE - Defines the task interface
# ============================================================================

class {task_name}Signature(dspy.Signature):
    """{desc}."""

    {input_field} = dspy.InputField(desc="The input {input_field}")
    {output_field} = dspy.OutputField(desc="The {output_field}")


# ============================================================================
# 3. MODULE - Implements the ReAct agent with tools
# ============================================================================

class {task_name}Agent(dspy.Module):
    """{desc} agent.

    {predictor_comment}

    This agent can use the following tools:
    - search_tool: Search for information
    - calculator_tool: Perform calculations
    - get_current_info: Get current information about topics
    """

    def __init__(self):
        super().__init__()

        # Define available tools
        self.tools = [
            Tool(
                func=search_tool,
                name="search",
                desc="Search for information on the web"
            ),
            Tool(
                func=calculator_tool,
                name="calculator",
                desc="Evaluate mathematical expressions"
            ),
            Tool(
                func=get_current_info,
                name="get_info",
                desc="Get current information about a topic"
            )
        ]

        # Create ReAct predictor with tools
        self.predictor = dspy.ReAct({task_name}Signature, tools=self.tools)

    def forward(self, {input_field}):
        """Process the input using ReAct reasoning and tools."""
        result = self.predictor({input_field}={input_field})
        return result.{output_field}


# ============================================================================
# 4. CONFIGURATION - Set up the language model
# ============================================================================

{self._get_enhanced_config_section()}


# ============================================================================
# 5. MAIN PROGRAM - Run the agent
# ============================================================================

def main():
    """Main program execution."""

    # Configure DSPy
    print("Setting up DSPy...")
    configure_dspy()
    print()

    # Create the agent
    print("Creating {task_name} agent with tools...")
    agent = {task_name}Agent()
    print("✓ Agent created with tools: search, calculator, get_info")
    print()

    # Example usage
    print("Running example...")
    print("-" * 60)

    example_{input_field} = "{example_input}"
    print(f"Input: {{example_{input_field}}}")
    print()

    # Run the agent (it will use tools as needed)
    result = agent({input_field}=example_{input_field})

    print(f"Output: {{result}}")
    print("-" * 60)
    print()

    # Interactive mode
    print("Try your own inputs (Ctrl+C to exit):")
    print("The agent will automatically use tools when needed.")
    print()

    try:
        while True:
            user_{input_field} = input("\\n{input_field.capitalize()}: ").strip()
            if not user_{input_field}:
                continue

            result = agent({input_field}=user_{input_field})
            print(f"{output_field.capitalize()}: {{result}}")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 6. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE THIS AGENT:

1. Add More Tools:
   - API integrations (weather, news, databases)
   - File operations (read, write, search files)
   - Custom domain-specific tools

2. Improve Tool Implementations:
   - Replace mock responses with real API calls
   - Add error handling and retries
   - Add rate limiting and caching

3. Add Evaluation:
   - Create test cases with expected tool usage
   - Measure accuracy of tool selection
   - Evaluate final output quality

4. Optimize with GEPA:
   - Collect examples of good tool usage
   - Optimize prompts for better tool selection
   - Fine-tune reasoning patterns

5. Deploy:
   - Save the optimized agent: dspy.save(agent, 'agent.json')
   - Load in production: agent = dspy.load('agent.json')
   - Add monitoring and logging
"""


if __name__ == "__main__":
    main()
'''

    def _select_predictor(self, user_input_lower: str) -> tuple[str, str]:
        """
        Select appropriate predictor based on user input.

        Returns:
            Tuple of (predictor_code, comment_explaining_choice)
        """

        # ProgramOfThought - for mathematical/computational tasks
        if any(
            kw in user_input_lower
            for kw in ["program of thought", "pot", "math", "calculat", "comput"]
        ):
            return (
                "dspy.ProgramOfThought",
                "Uses ProgramOfThought: Generates and executes Python code for computational tasks.",
            )

        # CodeAct - for code generation and programming tasks
        if any(
            kw in user_input_lower
            for kw in ["code act", "codeact", "code generat", "programming", "write code"]
        ):
            return ("dspy.CodeAct", "Uses CodeAct: Generates code-based solutions and actions.")

        # MultiChainComparison - for high-accuracy tasks
        if any(
            kw in user_input_lower
            for kw in [
                "multi chain",
                "multichain",
                "comparison",
                "multiple reasoning",
                "high accuracy",
            ]
        ):
            return (
                "dspy.MultiChainComparison",
                "Uses MultiChainComparison: Generates multiple reasoning chains and selects the best one.",
            )

        # BestOfN - for quality-focused tasks
        if any(
            kw in user_input_lower
            for kw in ["best of", "bestof", "multiple attempts", "best output"]
        ):
            return (
                "dspy.BestOfN",
                "Uses BestOfN: Generates multiple outputs and selects the best one based on a metric.",
            )

        # Refine - for iterative improvement
        if any(kw in user_input_lower for kw in ["refine", "iterative", "improve", "polish"]):
            return (
                "dspy.Refine",
                "Uses Refine: Iteratively refines the output for better quality.",
            )

        # KNN - for example-based learning
        if any(
            kw in user_input_lower
            for kw in ["knn", "k-nn", "nearest neighbor", "example", "similar"]
        ):
            return (
                "dspy.KNN",
                "Uses KNN: Retrieves similar examples and uses them for prediction.",
            )

        # Parallel - for ensemble/multiple perspectives
        if any(kw in user_input_lower for kw in ["parallel", "ensemble", "multiple", "combine"]):
            return (
                "dspy.Parallel",
                "Uses Parallel: Runs multiple predictors in parallel for ensemble predictions.",
            )

        # ReAct - for tool-using agents (check this BEFORE other patterns)
        # Keywords: react, agent, tool, action, search, web, api, external
        if any(
            kw in user_input_lower
            for kw in [
                "react",
                "agent",
                "tool",
                "action",
                "search",
                "web search",
                "api",
                "external",
            ]
        ):
            return ("dspy.ReAct", "Uses ReAct: Combines reasoning and acting with external tools.")

        # ChainOfThought - for reasoning tasks
        if any(
            kw in user_input_lower
            for kw in ["chain of thought", "cot", "reasoning", "think", "explain"]
        ):
            return (
                "dspy.ChainOfThought",
                "Uses ChainOfThought: Generates step-by-step reasoning before the final answer.",
            )

        # ChainOfThought - default for better quality
        # (Changed from Predict to provide better results by default)
        return (
            "dspy.ChainOfThought",
            "Uses ChainOfThought: Provides step-by-step reasoning for better quality (default).",
        )

    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response."""
        import re

        # Look for code blocks
        code_pattern = r"```python\n(.*?)\n```"
        matches = re.findall(code_pattern, response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # Look for code without markers
        if "import dspy" in response and "class" in response:
            # Try to extract just the code part
            lines = response.split("\n")
            code_lines = []
            in_code = False

            for line in lines:
                if "import dspy" in line:
                    in_code = True
                if in_code:
                    code_lines.append(line)

            if code_lines:
                return "\n".join(code_lines).strip()

        return response.strip()

    def _generate_signature_code(self, task_def: TaskDefinition) -> str:
        """Generate signature code from task definition."""
        return self.code_generator._generate_signature(task_def)

    def _generate_module_code(self, task_def: TaskDefinition, pattern: ReasoningPattern) -> str:
        """Generate module code from task definition and pattern."""
        signature_code = self.code_generator._generate_signature(task_def)
        module_code = self.code_generator._generate_module(task_def, pattern)

        return f"import dspy\n\n{signature_code}\n\n{module_code}"

    def _assemble_complete_program(self, generated) -> str:
        """Assemble complete program from generated components."""
        return f"""{chr(10).join(generated.imports)}

{generated.signature_code}

{generated.module_code}

{generated.program_code}
"""

    def _save_generated_code(self, command: str):
        """Save the last generated code to a file."""
        if "last_generated" not in self.current_context:
            console.print("[yellow]No code to save yet. Generate something first![/yellow]")
            return

        # Extract filename from command
        parts = command.split(maxsplit=1)
        if len(parts) < 2:
            console.print("[yellow]Usage: save <filename>[/yellow]")
            return

        filename = parts[1].strip()
        if not filename.endswith(".py"):
            filename += ".py"

        # Determine output directory
        output_dir = Path(self.config_manager.config.output_directory)
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / filename

        # Write the file
        output_file.write_text(self.current_context["last_generated"])

        console.print(f"[green]✓[/green] Code saved to: {output_file}")


def _show_welcome_screen(console, context, config_manager):
    """Show simple welcome screen with ASCII art."""
    from rich.align import Align
    from rich.box import DOUBLE
    from rich.panel import Panel
    from rich.text import Text

    from ..core.version_checker import display_version_info
    from ..ui.welcome import DSPY_ASCII_ART, create_gradient_text

    console.print()

    # Display DSPy version info with warnings if needed
    display_version_info(console, show_warning=True)
    console.print()

    # Create beautiful gradient colors for the ASCII art (purple → pink → orange)
    # Using exact RGB colors matching the SVG gradient
    gradient_colors = [
        (217, 70, 239),  # #d946ef - Deep purple - "DSPY" starts here
        (217, 70, 239),  # #d946ef - Purple
        (192, 38, 211),  # #c026d3 - Purple
        (168, 85, 247),  # #a855f7 - Bright purple
        (168, 85, 247),  # #a855f7 - Purple transitioning to pink
        (236, 72, 153),  # #ec4899 - Pink
        (236, 72, 153),  # #ec4899 - Bright pink - middle section
        (244, 63, 94),  # #f43f5e - Pink
        (244, 63, 94),  # #f43f5e - Pink transitioning to orange
        (251, 146, 60),  # #fb923c - Orange - "CODE" section
        (251, 146, 60),  # #fb923c - Bright orange
        (251, 146, 60),  # #fb923c - Orange end
    ]

    # Show ASCII art with gradient in a panel
    ascii_text = create_gradient_text(DSPY_ASCII_ART, gradient_colors)
    ascii_panel = Panel(
        Align.center(ascii_text), border_style="bright_magenta", box=DOUBLE, padding=(1, 4)
    )
    console.print(ascii_panel)

    # Simple welcome message with purple-pink-orange gradient
    welcome_text = Text()
    welcome_text.append("✨ ", style="bright_magenta")
    welcome_text.append("Welcome to ", style="white")
    welcome_text.append("D", style="magenta")
    welcome_text.append("S", style="bright_magenta")
    welcome_text.append("P", style="red")
    welcome_text.append("y", style="bright_red")
    welcome_text.append(" ", style="white")
    welcome_text.append("C", style="yellow")
    welcome_text.append("o", style="bright_yellow")
    welcome_text.append("d", style="yellow")
    welcome_text.append("e", style="bright_red")
    welcome_text.append(" ✨", style="bright_magenta")

    console.print(Align.center(welcome_text))
    console.print()

    # Model info
    model_name = "Not configured"
    if config_manager:
        try:
            config = config_manager.get_config()
            if config and "model" in config:
                model_name = config.get("model", {}).get("name", "Not configured")
        except Exception:
            pass

    model_info = Text()
    model_info.append("🤖 Model: ", style="dim")
    model_info.append(
        model_name, style="bold green" if model_name != "Not configured" else "bold yellow"
    )
    console.print(Align.center(model_info))
    console.print()

    # Show RAG and Fast Mode status
    try:
        if config_manager:
            rag_config = config_manager.config.codebase_rag
            rag_enabled = rag_config.enabled if rag_config else False  # Default to disabled
            fast_mode = rag_config.fast_mode if rag_config else True  # Default to enabled

            # Performance status using Rich Text properly
            perf_text = Text()
            perf_text.append("⚡ Performance: ", style="dim")
            perf_text.append("RAG ", style="dim")
            if rag_enabled:
                perf_text.append("ON", style="bold green")
            else:
                perf_text.append("OFF", style="bold red")
            perf_text.append(" | Fast Mode ", style="dim")
            if fast_mode:
                perf_text.append("ON", style="bold green")
            else:
                perf_text.append("OFF", style="bold yellow")
            console.print(Align.center(perf_text))
            console.print()

            # Show tip based on current settings
            if not rag_enabled:
                tip_text = Text()
                tip_text.append("💡 ", style="yellow")
                tip_text.append("Quick responses | ", style="dim")
                tip_text.append("Enable RAG for better quality: ", style="dim")
                tip_text.append("/enable-rag", style="cyan")
                tip_text.append(" + ", style="dim")
                tip_text.append("/fast-mode off", style="cyan")
                console.print(Align.center(tip_text))
                console.print()
    except Exception:
        pass

    # Minimal help
    console.print("[dim]Type /help for commands or describe what you want to build[/dim]")
    console.print()


def execute(verbose: bool = False, debug: bool = False):
    """
    Execute the interactive REPL mode.

    Args:
        verbose: Enable verbose output
        debug: Enable debug mode
    """
    logger.info("Starting interactive mode")

    # Initialize config manager
    config_manager = ConfigManager()

    # Try to load project context
    from ..project import ProjectContextManager

    context_manager = ProjectContextManager()
    context = context_manager.load_context(".")

    # Show enhanced welcome screen
    _show_welcome_screen(console, context, config_manager)

    try:
        # Initialize model manager
        model_manager = ModelManager(config_manager)

        # Start interactive session
        session = InteractiveSession(config_manager, model_manager)
        session.start()

    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
    except Exception as e:
        logger.error(f"Failed to start interactive mode: {e}")
        raise DSPyCLIError(f"Failed to start interactive mode: {e}")
