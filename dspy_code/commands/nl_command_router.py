"""
Natural Language Command Router for DSPy Code.

Maps natural language queries to slash commands using a hybrid approach:
1. Fast pattern matching (first attempt)
2. LLM reasoning (fallback for complex/unmatched queries)

Enables users to use natural language for all CLI functionality.
"""

import json
import re
from typing import Any

from ..core.logging import get_logger

logger = get_logger(__name__)


class NLCommandRouter:
    """Routes natural language queries to appropriate slash commands."""

    def __init__(self, llm_connector=None):
        """
        Initialize the NL command router.

        Args:
            llm_connector: Optional LLMConnector for LLM-based reasoning fallback
        """
        # Command mappings: natural language patterns -> (command, args_extractor)
        self.command_mappings = self._build_command_mappings()
        self.llm_connector = llm_connector

    def _build_command_mappings(self) -> dict[str, dict[str, Any]]:
        """Build comprehensive command mappings."""
        return {
            # Connection commands
            "connect": {
                "patterns": [
                    r"connect (?:to )?(?:a |an )?(?:model |llm |language model )?",
                    r"use (?:model |llm |language model )",
                    r"switch (?:to )?(?:model |llm )",
                    r"set (?:up |)model",
                    r"configure model",
                    r"link (?:to )?model",
                ],
                "command": "/connect",
                "extract_args": self._extract_connect_args,
            },
            "disconnect": {
                "patterns": [
                    r"disconnect (?:from )?(?:model |llm )?",
                    r"unlink (?:from )?model",
                    r"stop using (?:model |llm )",
                    r"close (?:model |llm )?connection",
                ],
                "command": "/disconnect",
                "extract_args": lambda x, m: [],
            },
            "models": {
                "patterns": [
                    r"list (?:available |all )?(?:models |llms |language models )",
                    r"show (?:available |all )?(?:models |llms )",
                    r"what (?:models |llms ) (?:are |do you )?(?:available |support )",
                    r"available (?:models |llms )",
                ],
                "command": "/models",
                "extract_args": lambda x, m: [],
            },
            "status": {
                "patterns": [
                    r"status",
                    r"what (?:is |'s )?(?:the )?(?:current )?(?:status |state )",
                    r"show (?:me )?(?:the )?(?:current )?(?:status |state )",
                    r"where (?:am |are )?i",
                    r"what (?:am |are )?i (?:doing |working on )",
                    r"current (?:status |state )",
                ],
                "command": "/status",
                "extract_args": lambda x, m: [],
            },
            # File operations
            "save": {
                "patterns": [
                    r"save (?:the )?(?:code |program |module |file )?(?:as |to )?",
                    r"save (?:this |it |current )",
                    r"write (?:to |)file",
                    r"store (?:the )?(?:code |program )",
                    r"export (?:code |program )",
                ],
                "command": "/save",
                "extract_args": self._extract_save_args,
            },
            "save_data": {
                "patterns": [
                    r"save (?:the )?(?:data |examples |training data |dataset )",
                    r"save (?:my )?(?:generated )?(?:data |examples )",
                    r"export (?:data |examples |training data )",
                    r"store (?:the )?(?:data |examples )",
                ],
                "command": "/save-data",
                "extract_args": self._extract_save_data_args,
            },
            # Validation and execution
            "validate": {
                "patterns": [
                    r"validate (?:the )?(?:code |program |module )?",
                    r"check (?:the )?(?:code |program |for errors )",
                    r"verify (?:the )?(?:code |program )",
                    r"test (?:the )?(?:code |program |syntax )",
                    r"is (?:the )?(?:code |program ) (?:valid |correct )",
                    r"does (?:the )?(?:code |program ) (?:work |have errors )",
                ],
                "command": "/validate",
                "extract_args": lambda x, m: [],
            },
            "run": {
                "patterns": [
                    r"run (?:the )?(?:code |program |module |script )?",
                    r"execute (?:the )?(?:code |program )",
                    r"test (?:the )?(?:code |program |execution )",
                    r"start (?:the )?(?:program |code )",
                    r"launch (?:the )?(?:program )",
                ],
                "command": "/run",
                "extract_args": self._extract_run_args,
            },
            "test": {
                "patterns": [
                    r"test (?:the )?(?:code |program |module )",
                    r"run tests",
                    r"execute tests",
                ],
                "command": "/test",
                "extract_args": self._extract_test_args,
            },
            # Project management
            "init": {
                "patterns": [
                    r"initialize (?:project |workspace |directory )",
                    r"init (?:project |workspace )",
                    r"setup (?:project |workspace |directory )",
                    r"create (?:new )?(?:project |workspace )",
                    r"start (?:new )?(?:project |workspace )",
                    r"new project",
                ],
                "command": "/init",
                "extract_args": self._extract_init_args,
            },
            "project": {
                "patterns": [
                    r"project (?:info |information |details |status )",
                    r"show (?:me )?(?:the )?(?:project |workspace )",
                    r"what (?:is |'s )?(?:the )?(?:project |workspace )",
                ],
                "command": "/project",
                "extract_args": lambda x, m: [],
            },
            # Optimization
            "optimize": {
                "patterns": [
                    r"optimize (?:the )?(?:code |program |module )?",
                    r"improve (?:the )?(?:code |program |performance )",
                    r"use (?:gepa |optimization )",
                    r"run (?:gepa |optimization )",
                    r"make (?:it |the code |the program ) (?:better |faster |more efficient )",
                ],
                "command": "/optimize",
                "extract_args": self._extract_optimize_args,
            },
            "optimize_start": {
                "patterns": [
                    r"start (?:gepa |optimization )",
                    r"begin (?:gepa |optimization )",
                ],
                "command": "/optimize-start",
                "extract_args": self._extract_optimize_start_args,
            },
            "optimize_status": {
                "patterns": [
                    r"(?:gepa |optimization ) (?:status |progress )",
                    r"how (?:is |'s )?(?:gepa |optimization ) (?:going |progressing )",
                    r"check (?:gepa |optimization ) (?:status |progress )",
                ],
                "command": "/optimize-status",
                "extract_args": lambda x, m: [],
            },
            "optimize_cancel": {
                "patterns": [
                    r"cancel (?:gepa |optimization )",
                    r"stop (?:gepa |optimization )",
                    r"abort (?:gepa |optimization )",
                ],
                "command": "/optimize-cancel",
                "extract_args": lambda x, m: [],
            },
            # Evaluation
            "eval": {
                "patterns": [
                    r"evaluate (?:the )?(?:code |program |model )",
                    r"run (?:evaluation |eval )",
                    r"test (?:performance |accuracy |metrics )",
                    r"measure (?:performance |accuracy )",
                    r"calculate (?:metrics |scores )",
                ],
                "command": "/eval",
                "extract_args": self._extract_eval_args,
            },
            # Data generation - HIGH PRIORITY (check before other patterns)
            # Use word boundaries to avoid false matches
            "data": {
                "patterns": [
                    r"\bgenerate\s+\d+\s+examples?\b",  # "generate 20 examples"
                    r"\bcreate\s+\d+\s+examples?\b",  # "create 20 examples"
                    r"\bmake\s+\d+\s+examples?\b",  # "make 20 examples"
                    r"\bgenerate\s+\d+\s+data\b",  # "generate 20 data"
                    r"\bcreate\s+\d+\s+data\b",  # "create 20 data"
                    r"\bgenerate\s+(?:training\s+)?examples?\b",  # "generate examples" or "generate training examples"
                    r"\bcreate\s+(?:training\s+)?examples?\b",  # "create examples" or "create training examples"
                    r"\bmake\s+(?:training\s+)?examples?\b",  # "make examples" or "make training examples"
                    r"\bgenerate\s+training\s+data\b",  # "generate training data"
                    r"\bcreate\s+training\s+data\b",  # "create training data"
                    r"\bgenerate\s+dataset\b",  # "generate dataset"
                    r"\bcreate\s+dataset\b",  # "create dataset"
                    r"\bexamples?\s+for\s+\w+",  # "examples for X" (requires task after "for")
                    r"\btraining\s+examples?\b",  # "training examples"
                    r"\bgold\s+examples?\b",  # "gold examples"
                    r"\bsynthetic\s+data\b",  # "synthetic data"
                ],
                "command": "/data",
                "extract_args": self._extract_data_args,
            },
            "help": {
                "patterns": [
                    r"help",
                    r"what (?:can |do ) (?:you |i ) (?:do |help )",
                    r"show (?:me )?(?:help |commands |options )",
                    r"list (?:commands |options )",
                    r"what (?:commands |options ) (?:are |do you have )",
                ],
                "command": "/help",
                "extract_args": lambda x, m: [],
            },
            "intro": {
                "patterns": [
                    r"intro(?:duction )?",
                    r"guide",
                    r"tutorial",
                    r"getting started",
                    r"how (?:to |do i ) (?:start |begin |use )",
                ],
                "command": "/intro",
                "extract_args": lambda x, m: [],
            },
            # History and context
            "history": {
                "patterns": [
                    r"history",
                    r"show (?:me )?(?:the )?(?:conversation |chat |message )?history",
                    r"what (?:did |have ) (?:we |i ) (?:talked |discussed ) (?:about )",
                    r"previous (?:messages |conversation )",
                ],
                "command": "/history",
                "extract_args": self._extract_history_args,
            },
            "clear": {
                "patterns": [
                    r"clear (?:context |history |conversation |memory )",
                    r"reset (?:context |history |conversation )",
                    r"forget (?:everything |all |context )",
                    r"start (?:over |fresh |new )",
                    r"new (?:conversation |session )",
                ],
                "command": "/clear",
                "extract_args": lambda x, m: [],
            },
            # Sessions
            "sessions": {
                "patterns": [
                    r"list (?:sessions |saved sessions )",
                    r"show (?:me )?(?:all )?(?:sessions |saved sessions )",
                    r"what (?:sessions |saved sessions ) (?:do |are ) (?:i |you ) (?:have |saved )",
                ],
                "command": "/sessions",
                "extract_args": lambda x, m: [],
            },
            "session": {
                "patterns": [
                    r"save (?:session |conversation )",
                    r"load (?:session |conversation )",
                    r"restore (?:session |conversation )",
                    r"open (?:session |conversation )",
                ],
                "command": "/session",
                "extract_args": self._extract_session_args,
            },
            # Export/Import
            "export": {
                "patterns": [
                    r"export (?:package |project |code )",
                    r"package (?:the )?(?:project |code )",
                    r"create (?:package |archive )",
                ],
                "command": "/export",
                "extract_args": self._extract_export_args,
            },
            "import": {
                "patterns": [
                    r"import (?:package |project )",
                    r"load (?:package |project )",
                    r"open (?:package |project )",
                ],
                "command": "/import",
                "extract_args": self._extract_import_args,
            },
            # RAG and indexing
            "refresh_index": {
                "patterns": [
                    r"refresh (?:index |knowledge base |codebase )",
                    r"rebuild (?:index |knowledge base )",
                    r"update (?:index |knowledge base )",
                    r"reindex",
                ],
                "command": "/refresh-index",
                "extract_args": lambda x, m: [],
            },
            "index_status": {
                "patterns": [
                    r"index (?:status |state )",
                    r"knowledge base (?:status |state )",
                    r"codebase (?:index |status )",
                ],
                "command": "/index-status",
                "extract_args": lambda x, m: [],
            },
            # Feature listings
            "predictors": {
                "patterns": [
                    r"list (?:predictors |predictor types )",
                    r"show (?:me )?(?:predictors |predictor types )",
                    r"what (?:predictors |predictor types ) (?:are |do you have )",
                    r"available (?:predictors |predictor types )",
                ],
                "command": "/predictors",
                "extract_args": self._extract_predictors_args,
            },
            "adapters": {
                "patterns": [
                    r"list (?:adapters |adapter types )",
                    r"show (?:me )?(?:adapters |adapter types )",
                    r"what (?:adapters |adapter types )",
                ],
                "command": "/adapters",
                "extract_args": self._extract_adapters_args,
            },
            "retrievers": {
                "patterns": [
                    r"list (?:retrievers |retriever types )",
                    r"show (?:me )?(?:retrievers |retriever types )",
                    r"what (?:retrievers |retriever types )",
                ],
                "command": "/retrievers",
                "extract_args": self._extract_retrievers_args,
            },
            "examples": {
                "patterns": [
                    r"show (?:me )?(?:examples |templates |samples )",
                    r"list (?:examples |templates )",
                    r"what (?:examples |templates ) (?:do |are ) (?:you |available )",
                    r"^(?:show|list|view|see) (?:code )?examples",  # Only at start, with action verb
                    r"^(?:show|list|view|see) templates",  # Only at start, with action verb
                ],
                "command": "/examples",
                "extract_args": self._extract_examples_args,
            },
            # MCP commands
            "mcp_connect": {
                "patterns": [
                    r"connect (?:to )?(?:mcp |mcp server )",
                    r"link (?:to )?(?:mcp |mcp server )",
                    r"use (?:mcp |mcp server )",
                ],
                "command": "/mcp-connect",
                "extract_args": self._extract_mcp_connect_args,
            },
            "mcp_disconnect": {
                "patterns": [
                    r"disconnect (?:from )?(?:mcp |mcp server )",
                    r"unlink (?:from )?(?:mcp |mcp server )",
                ],
                "command": "/mcp-disconnect",
                "extract_args": self._extract_mcp_disconnect_args,
            },
            "mcp_servers": {
                "patterns": [
                    r"list (?:mcp |mcp )?servers",
                    r"show (?:me )?(?:mcp |mcp )?servers",
                    r"what (?:mcp |mcp )?servers",
                ],
                "command": "/mcp-servers",
                "extract_args": lambda x, m: [],
            },
            "mcp_tools": {
                "patterns": [
                    r"list (?:mcp )?tools",
                    r"show (?:me )?(?:mcp )?tools",
                    r"what (?:mcp )?tools",
                    r"available (?:mcp )?tools",
                ],
                "command": "/mcp-tools",
                "extract_args": self._extract_mcp_tools_args,
            },
            "mcp_call": {
                "patterns": [
                    r"call (?:mcp )?tool",
                    r"use (?:mcp )?tool",
                    r"invoke (?:mcp )?tool",
                    r"run (?:mcp )?tool",
                ],
                "command": "/mcp-call",
                "extract_args": self._extract_mcp_call_args,
            },
            "mcp_resources": {
                "patterns": [
                    r"list (?:mcp )?resources",
                    r"show (?:me )?(?:mcp )?resources",
                    r"what (?:mcp )?resources",
                ],
                "command": "/mcp-resources",
                "extract_args": self._extract_mcp_resources_args,
            },
            "mcp_read": {
                "patterns": [
                    r"read (?:mcp )?resource",
                    r"get (?:mcp )?resource",
                    r"load (?:mcp )?resource",
                ],
                "command": "/mcp-read",
                "extract_args": self._extract_mcp_read_args,
            },
            "mcp_prompts": {
                "patterns": [
                    r"list (?:mcp )?prompts",
                    r"show (?:me )?(?:mcp )?prompts",
                ],
                "command": "/mcp-prompts",
                "extract_args": self._extract_mcp_prompts_args,
            },
            "mcp_prompt": {
                "patterns": [
                    r"get (?:mcp )?prompt",
                    r"show (?:me )?(?:mcp )?prompt",
                ],
                "command": "/mcp-prompt",
                "extract_args": self._extract_mcp_prompt_args,
            },
            # Demo
            "demo": {
                "patterns": [
                    r"demo",
                    r"show (?:me )?(?:a )?demo",
                    r"demonstration",
                    r"example (?:usage |workflow )",
                ],
                "command": "/demo",
                "extract_args": self._extract_demo_args,
            },
        }

    def route(
        self, user_input: str, context: dict[str, Any] | None = None
    ) -> tuple[str, list[str]] | None:
        """
        Route natural language input to a slash command using LLM reasoning.

        NOTE: For now we only use this router to handle *explicit* routing
        requests (e.g. \"run /init\" or \"call /connect\"), and we do not
        automatically convert generic natural language like \"explain X\"
        into slash commands. If this router can't confidently decide, it
        returns None and the main interactive loop treats the input as a
        normal LLM request instead of failing with a command usage error.

        Strategy:
        1. Try pattern matching to gather context (fast, deterministic hints)
        2. Always use LLM reasoning with pattern matching results as context
        3. LLM makes the final decision based on all available context

        Args:
            user_input: User's natural language input
            context: Optional context (conversation history, current state, etc.)

        Returns:
            Tuple of (command, args) or None if no match
        """
        if not self.llm_connector or not self.llm_connector.current_model:
            logger.debug(
                f"No LLM available for NL routing, treating as normal LLM input: '{user_input}'"
            )
            # Don't auto-route to commands if no LLM; let interactive loop
            # handle this as a regular natural language request.
            return None

        user_input_lower = user_input.lower().strip()

        # Check if user explicitly references a slash command (e.g., "/save", "/mcp-read")
        # We need to distinguish between actual commands (like "/save") and file paths (like "/tmp/city")
        # Slash commands typically appear as "/command" at word boundaries or standalone
        slash_command_pattern = r'\b/(?:save|run|validate|connect|mcp-|init|help|status|clear|exit|optimize|eval|explain|model|models|data|examples|adapters|retrievers|demo|session)'
        has_slash_command = re.search(slash_command_pattern, user_input_lower) is not None

        # Also check for natural language command patterns (without "/")
        # This allows commands like "list mcp servers" to be routed
        has_nl_command_pattern = False
        for cmd_name, cmd_info in self.command_mappings.items():
            for pattern in cmd_info.get("patterns", []):
                if re.search(pattern, user_input_lower, re.IGNORECASE):
                    has_nl_command_pattern = True
                    break
            if has_nl_command_pattern:
                break

        # Route if either:
        # 1. User explicitly references a slash command (and it's not a file path)
        # 2. User's input matches a natural language command pattern
        if not has_slash_command and not has_nl_command_pattern:
            logger.debug(
                f"No command pattern match in NL input, treating as normal LLM input: '{user_input}'"
            )
            return None

        # If the user mentions a command (either slash or natural language),
        # allow the LLM router to decide whether to dispatch it.
        if has_slash_command:
            logger.debug(f"Using LLM reasoning for explicit slash command reference: '{user_input}'")
        else:
            logger.debug(f"Using LLM reasoning for natural language command pattern: '{user_input}'")
        return self._route_with_llm(user_input, context, pattern_matches=None)

    def _route_with_llm(
        self,
        user_input: str,
        context: dict[str, Any] | None = None,
        pattern_matches: list[dict[str, Any]] | None = None,
    ) -> tuple[str, list[str]] | None:
        """
        Use LLM reasoning to route natural language to slash commands.

        Args:
            user_input: User's natural language input
            context: Optional context information (conversation history, current state, etc.)
            pattern_matches: Optional list of pattern matching results to provide as hints

        Returns:
            Tuple of (command, args) or None if LLM can't determine
        """
        if not self.llm_connector or not self.llm_connector.current_model:
            logger.debug("LLM not available for routing")
            return None

        try:
            # Build list of available commands for LLM
            available_commands = []
            for cmd_name, cmd_info in self.command_mappings.items():
                available_commands.append(
                    {
                        "command": cmd_info["command"],
                        "description": self._get_command_description(cmd_name),
                        "examples": self._get_command_examples(cmd_name),
                    }
                )

            # Build comprehensive context information
            context_info = ""
            if context:
                if "current_model" in context:
                    context_info += f"Currently connected model: {context['current_model']}\n"
                if "has_code" in context:
                    context_info += f"User has generated code: {context['has_code']}\n"
                if "has_data" in context:
                    context_info += f"User has generated data: {context['has_data']}\n"
                if "conversation_history" in context:
                    # Include recent conversation context
                    history = context.get("conversation_history", [])
                    if history:
                        recent = history[-3:] if len(history) > 3 else history
                        context_info += "\nRecent conversation context:\n"
                        for msg in recent:
                            role = msg.get("role", "unknown")
                            content = msg.get("content", "")[:200]  # Truncate long messages
                            context_info += f"  {role}: {content}\n"

            # Add pattern matching hints if available
            pattern_hints = ""
            if pattern_matches:
                pattern_hints = (
                    "\n\nPattern Matching Hints (for reference, but you make the final decision):\n"
                )
                for match in pattern_matches[:3]:  # Top 3 matches
                    pattern_hints += f"  - {match['command']} (confidence: {match['confidence']}, args hint: {match.get('args_hint', [])})\n"
                pattern_hints += "\n"

            # Build comprehensive prompt for LLM
            prompt = f"""You are an intelligent command router for DSPy Code CLI. Your job is to understand the user's intent and route them to the correct command with the right arguments.

User's request: "{user_input}"

Current Context:
{context_info if context_info else "No additional context available."}
{pattern_hints}

Available Commands (with descriptions):
{json.dumps(available_commands, indent=2)}

Your Task:
1. Analyze the user's request carefully, considering all context provided
2. Determine which command best matches the user's intent (even if it's not in the pattern hints)
3. Extract all relevant arguments (model names, filenames, numbers, task descriptions, etc.)
4. Consider the conversation history and current state when making your decision
5. Return ONLY a JSON object with this exact format:
{{
  "command": "/command-name",
  "args": ["arg1", "arg2", ...],
  "reasoning": "brief explanation of why you chose this command"
}}

Important Guidelines:
- If the user wants to generate training data/examples, use /data command
- If the user wants to optimize code/programs, use /optimize command
- If the user wants to evaluate/test code, use /eval command
- If the user wants to create code/modules/programs, return null (this triggers code generation)
- If the user asks a question or wants explanation, use /explain command
- Extract arguments accurately (e.g., "20 examples" → args: ["task description", "20"])
- Consider the full context, not just pattern hints

Examples:
- "generate 20 examples for tweet classification" → {{"command": "/data", "args": ["tweet classification", "20"], "reasoning": "User wants to generate training data"}}
- "optimize my program with gepa" → {{"command": "/optimize", "args": [], "reasoning": "User wants to optimize code"}}
- "evaluate the program with accuracy metric" → {{"command": "/eval", "args": ["metric=accuracy"], "reasoning": "User wants to evaluate code"}}
- "test performance of my_module.py" → {{"command": "/eval", "args": ["my_module.py"], "reasoning": "User wants to evaluate a specific file"}}
- "connect to ollama llama3.1:8b" → {{"command": "/connect", "args": ["ollama", "llama3.1:8b"], "reasoning": "User wants to connect to a model"}}
- "save this as test.py" → {{"command": "/save", "args": ["test.py"], "reasoning": "User wants to save generated code"}}
- "what is ChainOfThought?" → {{"command": "/explain", "args": ["ChainOfThought"], "reasoning": "User wants an explanation"}}
- "create a sentiment analyzer" → {{"command": null, "args": [], "reasoning": "User wants code generation, not a command"}}

Return ONLY the JSON, no explanations:"""

            # Call LLM
            response = self.llm_connector.generate_response(
                prompt=prompt,
                system_prompt="You are a precise command router. Always return valid JSON only.",
                context={},
            )

            # Extract JSON from response
            result = self._extract_json_from_llm_response(response)

            if result and result.get("command"):
                command = result["command"]
                args = result.get("args", [])
                reasoning = result.get("reasoning", "No reasoning provided")
                logger.debug(f"NL routing (LLM): '{user_input}' -> {command} {args}")
                logger.debug(f"LLM reasoning: {reasoning}")
                return (command, args if isinstance(args, list) else [])

            # LLM determined this is not a command (likely code generation)
            logger.debug(f"LLM determined '{user_input}' is not a command (likely code generation)")
            return None

        except Exception as e:
            logger.warning(f"LLM routing failed: {e}")
            # Fallback to pattern matching if LLM fails
            if pattern_matches:
                best_match = pattern_matches[0]
                logger.debug(f"Falling back to pattern match: {best_match['command']}")
                return (best_match["command"], best_match.get("args_hint", []))
            return None

    def _route_with_pattern_only(self, user_input: str) -> tuple[str, list[str]] | None:
        """
        Fallback routing using only pattern matching (when LLM is not available).

        Args:
            user_input: User's natural language input

        Returns:
            Tuple of (command, args) or None if no match
        """
        user_input_lower = user_input.lower().strip()

        # Check data generation first (highest priority)
        if "data" in self.command_mappings:
            cmd_info = self.command_mappings["data"]
            for pattern in cmd_info["patterns"]:
                match = re.search(pattern, user_input_lower, re.IGNORECASE)
                if match:
                    args = cmd_info["extract_args"](user_input, match)
                    logger.debug(
                        f"Pattern routing (fallback): '{user_input}' -> {cmd_info['command']} {args}"
                    )
                    return (cmd_info["command"], args)

        # Check all other commands
        for cmd_name, cmd_info in self.command_mappings.items():
            if cmd_name == "data":
                continue
            for pattern in cmd_info["patterns"]:
                match = re.search(pattern, user_input_lower, re.IGNORECASE)
                if match:
                    args = cmd_info["extract_args"](user_input, match)
                    logger.debug(
                        f"Pattern routing (fallback): '{user_input}' -> {cmd_info['command']} {args}"
                    )
                    return (cmd_info["command"], args)

        return None

    def _extract_json_from_llm_response(self, response: str) -> dict[str, Any] | None:
        """Extract JSON from LLM response."""
        if not response or not response.strip():
            return None

        try:
            # Try to find JSON object in response (handles markdown code blocks)
            # Remove markdown code blocks if present
            cleaned_response = re.sub(r"```(?:json)?\s*\n?", "", response, flags=re.IGNORECASE)
            cleaned_response = cleaned_response.strip()

            # Try to find JSON object in response
            json_match = re.search(r"\{[\s\S]*\}", cleaned_response)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)

            # Try parsing entire response as JSON
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Response was: {response[:200]}...")
            return None
        except Exception as e:
            logger.debug(f"Unexpected error parsing LLM response: {e}")
            return None

    def _get_command_description(self, cmd_name: str) -> str:
        """Get human-readable description of a command."""
        descriptions = {
            "connect": "Connect to a language model (Ollama, OpenAI, Anthropic, Gemini)",
            "disconnect": "Disconnect from current model",
            "models": "List available models",
            "status": "Show current status (model, code, data)",
            "save": "Save generated code to a file",
            "save_data": "Save generated training data to a file",
            "validate": "Validate code for errors and best practices",
            "run": "Execute/run the generated code",
            "test": "Run tests on the code",
            "init": "Initialize a new DSPy project",
            "project": "Show project information",
            "optimize": "Optimize code using GEPA",
            "eval": "Evaluate code performance with metrics",
            "data": "Generate training data/examples",
            "explain": "Explain DSPy concepts, predictors, optimizers",
            "help": "Show help and available commands",
            "intro": "Show introduction and getting started guide",
            "history": "Show conversation history",
            "clear": "Clear context and start fresh",
            "sessions": "List saved sessions",
            "session": "Save or load a session",
            "export": "Export project as a package",
            "import": "Import a project package",
            "refresh_index": "Refresh codebase knowledge index",
            "index_status": "Show index status",
            "predictors": "List all DSPy predictors",
            "adapters": "List all DSPy adapters",
            "retrievers": "List all DSPy retrievers",
            "examples": "Show code examples and templates",
            "mcp_connect": "Connect to an MCP server",
            "mcp_disconnect": "Disconnect from MCP server",
            "mcp_servers": "List available MCP servers",
            "mcp_tools": "List MCP tools",
            "mcp_call": "Call an MCP tool",
            "mcp_resources": "List MCP resources",
            "mcp_read": "Read an MCP resource",
            "mcp_prompts": "List MCP prompts",
            "mcp_prompt": "Get an MCP prompt",
            "demo": "Show a demo",
        }
        return descriptions.get(cmd_name, "Execute a command")

    def _get_command_examples(self, cmd_name: str) -> list[str]:
        """Get example natural language phrases for a command."""
        examples = {
            "connect": ["connect to ollama llama3.1:8b", "use model gpt-4", "switch to claude"],
            "save": ["save as test.py", "save the code", "write to file"],
            "validate": ["validate the code", "check for errors", "verify the program"],
            "run": ["run the code", "execute the program", "test execution"],
            "status": ["what's the status", "show me the status", "where am I"],
            "optimize": ["optimize the code", "improve with gepa", "run optimization"],
            "data": ["generate 20 examples", "create training data", "make examples"],
            "explain": ["what is ChainOfThought", "explain GEPA", "tell me about predictors"],
        }
        return examples.get(cmd_name, [])

    # Argument extraction methods
    def _extract_connect_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract model connection arguments."""
        user_input_lower = user_input.lower()
        args = []

        # Extract provider
        if "ollama" in user_input_lower:
            args.append("ollama")
        elif "openai" in user_input_lower or "gpt" in user_input_lower:
            args.append("openai")
        elif "anthropic" in user_input_lower or "claude" in user_input_lower:
            args.append("anthropic")
        elif "gemini" in user_input_lower or "google" in user_input_lower:
            args.append("gemini")

        # Extract model name
        model_patterns = [
            r"llama[0-9.]+(?::[0-9]+[bB])?",
            r"gpt-[0-9.]+",
            r"claude-[0-9.]+",
            r"gemini-[0-9.]+",
        ]

        for pattern in model_patterns:
            match = re.search(pattern, user_input_lower)
            if match:
                model_name = match.group(0)
                if args:  # If provider found
                    args.append(model_name)
                # Try to infer provider from model name
                elif "llama" in model_name:
                    args = ["ollama", model_name]
                elif "gpt" in model_name:
                    args = ["openai", model_name]
                elif "claude" in model_name:
                    args = ["anthropic", model_name]
                elif "gemini" in model_name:
                    args = ["gemini", model_name]
                break

        return args

    def _extract_save_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract save file arguments."""
        # Look for filename
        filename_match = re.search(
            r'(?:as |to |file |filename )["\']?([\w./-]+\.py)["\']?', user_input, re.IGNORECASE
        )
        if filename_match:
            return [filename_match.group(1)]

        # Look for filename without extension
        filename_match = re.search(
            r'(?:as |to |file |filename )["\']?([\w./-]+)["\']?', user_input, re.IGNORECASE
        )
        if filename_match:
            filename = filename_match.group(1)
            if not filename.endswith(".py"):
                filename += ".py"
            return [filename]

        return []

    def _extract_save_data_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract save data arguments."""
        # Look for filename
        filename_match = re.search(
            r'(?:as |to |file )["\']?([\w./-]+\.jsonl?)["\']?', user_input, re.IGNORECASE
        )
        if filename_match:
            return [filename_match.group(1)]

        filename_match = re.search(
            r'(?:as |to |file )["\']?([\w./-]+)["\']?', user_input, re.IGNORECASE
        )
        if filename_match:
            filename = filename_match.group(1)
            if not filename.endswith(".jsonl"):
                filename += ".jsonl"
            return [filename]

        return []

    def _extract_run_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract run command arguments."""
        # Look for timeout
        timeout_match = re.search(r"timeout[=: ](\d+)", user_input, re.IGNORECASE)
        if timeout_match:
            return [f"timeout={timeout_match.group(1)}"]
        return []

    def _extract_test_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract test arguments."""
        return []

    def _extract_init_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract init arguments."""
        args = []

        # Check for flags
        if "fresh" in user_input.lower() or "new" in user_input.lower():
            args.append("--fresh")
        if "verbose" in user_input.lower():
            args.append("--verbose")

        # Check for path
        path_match = re.search(
            r'(?:in |at |path |directory )["\']?([\w./-]+)["\']?', user_input, re.IGNORECASE
        )
        if path_match:
            args.extend(["--path", path_match.group(1)])

        return args

    def _extract_optimize_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract optimize arguments."""
        args = []

        # Look for file/program reference
        file_match = re.search(
            r'(?:file |program |code |module )["\']?([\w./-]+\.py)["\']?', user_input, re.IGNORECASE
        )
        if file_match:
            args.append(file_match.group(1))

        # Look for data file reference
        data_match = re.search(
            r'(?:data |examples |training |with )["\']?([\w./-]+\.(?:jsonl|json))["\']?',
            user_input,
            re.IGNORECASE,
        )
        if data_match:
            args.append(data_match.group(1))

        return args

    def _extract_optimize_start_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract optimize-start arguments."""
        return []

    def _extract_eval_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract eval arguments."""
        args = []

        # Look for file/program reference
        file_match = re.search(
            r'(?:file |program |code |module )["\']?([\w./-]+\.py)["\']?', user_input, re.IGNORECASE
        )
        if file_match:
            args.append(file_match.group(1))

        # Look for data file reference
        data_match = re.search(
            r'(?:data |examples |test |dataset |with )["\']?([\w./-]+\.(?:jsonl|json))["\']?',
            user_input,
            re.IGNORECASE,
        )
        if data_match:
            args.append(data_match.group(1))

        # Look for metrics
        metrics = [
            "accuracy",
            "f1",
            "precision",
            "recall",
            "rouge",
            "bleu",
            "exact_match",
            "semantic_similarity",
        ]
        for metric in metrics:
            if metric in user_input.lower():
                args.append(f"metric={metric}")
                break

        return args

    def _extract_data_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract data generation arguments."""
        # Example: "generate 20 examples for tweet classification in jsonl format"
        # Example: "create 50 training examples for sentiment analysis"

        # Extract number of examples (look for patterns like "20 examples", "50", etc.)
        num_match = re.search(
            r"(\d+)\s*(?:examples?|samples?|data points?|training examples?)",
            user_input,
            re.IGNORECASE,
        )
        if not num_match:
            # Try just a number at the start
            num_match = re.search(r"^(?:generate|create|make)\s+(\d+)", user_input, re.IGNORECASE)

        num_examples = num_match.group(1) if num_match else "20"  # Default to 20
        num_examples = max(5, min(int(num_examples), 100))  # Limit to reasonable range

        # Extract task description - remove data generation keywords and numbers
        task_desc = user_input

        # Remove generation verbs
        task_desc = re.sub(
            r"^(?:generate|create|make|produce)\s+", "", task_desc, flags=re.IGNORECASE
        )

        # Remove number and "examples"/"data" keywords
        task_desc = re.sub(
            r"\d+\s*(?:examples?|samples?|data points?|training examples?|data)",
            "",
            task_desc,
            flags=re.IGNORECASE,
        )

        # Remove format specifications
        task_desc = re.sub(
            r"\s*(?:in|as|with)\s+(?:jsonl?|json|csv|txt)\s+format",
            "",
            task_desc,
            flags=re.IGNORECASE,
        )

        # Remove common prepositions and articles at start
        task_desc = re.sub(
            r"^(?:for |about |on |regarding |a |an |the )", "", task_desc, flags=re.IGNORECASE
        ).strip()

        # Remove trailing "in jsonl format" or similar
        task_desc = re.sub(
            r"\s+(?:in|as|with)\s+.*format$", "", task_desc, flags=re.IGNORECASE
        ).strip()

        # If task description is empty or too short, try to extract from context
        if not task_desc or len(task_desc) < 3:
            # Look for task-specific keywords
            task_types = {
                "tweet": "tweet classification",
                "sentiment": "sentiment analysis",
                "classification": "text classification",
                "question": "question answering",
                "qa": "question answering",
                "summarization": "text summarization",
                "translation": "translation",
                "email": "email classification",
                "ner": "named entity recognition",
                "rag": "retrieval augmented generation",
            }
            for key, value in task_types.items():
                if key in user_input.lower():
                    task_desc = value
                    break

        # If still empty, use a default
        if not task_desc or len(task_desc) < 3:
            task_desc = "text classification"

        # Return: [task_description, num_examples]
        return [task_desc, str(num_examples)]

    def _extract_explain_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract explain arguments."""
        # Remove question words and extract topic
        topic = user_input.lower()
        topic = re.sub(r"^(explain|what|how|tell|describe|show)\s+", "", topic)
        topic = re.sub(r"\?$", "", topic).strip()

        if topic:
            return [topic]
        return []

    def _extract_history_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract history arguments."""
        if "all" in user_input.lower():
            return ["all"]
        return []

    def _extract_session_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract session arguments."""
        args = []

        if "save" in user_input.lower():
            args.append("save")
            # Extract session name
            name_match = re.search(
                r'(?:as |named |called )["\']?([\w-]+)["\']?', user_input, re.IGNORECASE
            )
            if name_match:
                args.append(name_match.group(1))
        elif (
            "load" in user_input.lower()
            or "restore" in user_input.lower()
            or "open" in user_input.lower()
        ):
            args.append("load")
            # Extract session name
            name_match = re.search(
                r'(?:session |named |called )["\']?([\w-]+)["\']?', user_input, re.IGNORECASE
            )
            if name_match:
                args.append(name_match.group(1))

        return args

    def _extract_export_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract export arguments."""
        args = []

        # Look for output path
        path_match = re.search(
            r'(?:to |as |path )["\']?([\w./-]+)["\']?', user_input, re.IGNORECASE
        )
        if path_match:
            args.append(path_match.group(1))

        return args

    def _extract_import_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract import arguments."""
        args = []

        # Look for file path
        path_match = re.search(
            r'(?:from |file |path )["\']?([\w./-]+)["\']?', user_input, re.IGNORECASE
        )
        if path_match:
            args.append(path_match.group(1))

        return args

    def _extract_predictors_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract predictors arguments."""
        # Check for specific predictor name
        predictors = [
            "predict",
            "chainofthought",
            "react",
            "programofthought",
            "codeact",
            "multichain",
            "bestofn",
            "refine",
            "knn",
            "parallel",
        ]
        for pred in predictors:
            if pred in user_input.lower():
                return [pred]
        return []

    def _extract_adapters_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract adapters arguments."""
        adapters = ["json", "xml", "chat", "twostep"]
        for adapter in adapters:
            if adapter in user_input.lower():
                return [adapter]
        return []

    def _extract_retrievers_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract retrievers arguments."""
        retrievers = ["colbert", "custom", "embeddings"]
        for ret in retrievers:
            if ret in user_input.lower():
                return [ret]
        return []

    def _extract_examples_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract examples arguments."""
        # Check for example type
        example_types = ["rag", "sentiment", "qa", "classification", "optimization"]
        for ex_type in example_types:
            if ex_type in user_input.lower():
                return [ex_type]
        return []

    def _extract_mcp_connect_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP connect arguments."""
        # Look for server name
        name_match = re.search(
            r'(?:server |named |called )["\']?([\w-]+)["\']?', user_input, re.IGNORECASE
        )
        if name_match:
            return [name_match.group(1)]
        return []

    def _extract_mcp_disconnect_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP disconnect arguments."""
        return []

    def _extract_mcp_tools_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP tools arguments."""
        return []

    def _extract_mcp_call_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP call arguments."""
        args = []

        # Look for tool name
        tool_match = re.search(
            r'(?:tool |named |called )["\']?([\w-]+)["\']?', user_input, re.IGNORECASE
        )
        if tool_match:
            args.append(tool_match.group(1))

        return args

    def _extract_mcp_resources_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP resources arguments."""
        return []

    def _extract_mcp_read_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP read arguments."""
        args = []

        # Look for resource URI
        uri_match = re.search(
            r'(?:resource |uri |url )["\']?([\w:/.-]+)["\']?', user_input, re.IGNORECASE
        )
        if uri_match:
            args.append(uri_match.group(1))

        return args

    def _extract_mcp_prompts_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP prompts arguments."""
        return []

    def _extract_mcp_prompt_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract MCP prompt arguments."""
        args = []

        # Look for prompt name
        prompt_match = re.search(
            r'(?:prompt |named |called )["\']?([\w-]+)["\']?', user_input, re.IGNORECASE
        )
        if prompt_match:
            args.append(prompt_match.group(1))

        return args

    def _extract_demo_args(self, user_input: str, match: re.Match) -> list[str]:
        """Extract demo arguments."""
        # Check for demo type
        demo_types = ["basic", "rag", "optimization", "mcp"]
        for demo_type in demo_types:
            if demo_type in user_input.lower():
                return [demo_type]
        return []
