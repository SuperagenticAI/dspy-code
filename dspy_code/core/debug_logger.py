"""
Debug logger for enhanced debugging and performance tracking.
"""

import logging
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from collections.abc import Generator
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TimingStats:
    """Statistics for a timed operation."""

    count: int = 0
    total_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0

    def add(self, elapsed: float) -> None:
        """Add a timing measurement."""
        self.count += 1
        self.total_time += elapsed
        self.min_time = min(self.min_time, elapsed)
        self.max_time = max(self.max_time, elapsed)

    @property
    def avg_time(self) -> float:
        """Average time per operation."""
        return self.total_time / self.count if self.count > 0 else 0.0


@dataclass
class DebugLoggerConfig:
    """Configuration for debug logger."""

    enabled: bool = False
    log_llm_calls: bool = True
    log_mcp_messages: bool = True
    log_validation: bool = True
    log_timings: bool = True
    include_stack_traces: bool = True


class DebugLogger:
    """
    Enhanced logger for debugging and performance tracking.

    Provides timing measurements, LLM call logging, MCP message logging,
    and validation step logging when debug mode is enabled.
    """

    _instance: "DebugLogger | None" = None

    def __init__(self, config: DebugLoggerConfig | None = None):
        """
        Initialize the debug logger.

        Args:
            config: Debug logger configuration
        """
        self.config = config or DebugLoggerConfig()
        self._timings: dict[str, TimingStats] = defaultdict(TimingStats)
        self._llm_calls: list[dict[str, Any]] = []
        self._mcp_messages: list[dict[str, Any]] = []

    @classmethod
    def get_instance(cls) -> "DebugLogger":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def configure(cls, config: DebugLoggerConfig) -> "DebugLogger":
        """Configure the singleton instance."""
        cls._instance = cls(config)
        return cls._instance

    def enable(self) -> None:
        """Enable debug logging."""
        self.config.enabled = True

    def disable(self) -> None:
        """Disable debug logging."""
        self.config.enabled = False

    @contextmanager
    def timed_operation(self, name: str) -> Generator[None, None, None]:
        """
        Context manager for timing operations.

        Args:
            name: Name of the operation being timed

        Yields:
            None
        """
        if not self.config.enabled or not self.config.log_timings:
            yield
            return

        start = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            self._timings[name].add(elapsed)
            logger.debug(f"[TIMING] {name}: {elapsed:.3f}s")

    def log_llm_call(
        self,
        model: str,
        prompt_tokens: int,
        response_tokens: int,
        elapsed: float,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        """
        Log an LLM API call.

        Args:
            model: Model name
            prompt_tokens: Number of prompt tokens
            response_tokens: Number of response tokens
            elapsed: Time taken in seconds
            success: Whether the call succeeded
            error: Error message if failed
        """
        if not self.config.enabled or not self.config.log_llm_calls:
            return

        call_info = {
            "model": model,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "elapsed": elapsed,
            "success": success,
            "error": error,
            "timestamp": time.time(),
        }
        self._llm_calls.append(call_info)

        status = "✓" if success else "✗"
        logger.debug(
            f"[LLM {status}] model={model}, prompt={prompt_tokens}, "
            f"response={response_tokens}, time={elapsed:.3f}s"
        )

    def log_mcp_message(
        self,
        direction: str,
        server: str,
        message_type: str,
        content: Any = None,
    ) -> None:
        """
        Log an MCP message exchange.

        Args:
            direction: "send" or "recv"
            server: Server name
            message_type: Type of message
            content: Message content (optional)
        """
        if not self.config.enabled or not self.config.log_mcp_messages:
            return

        message_info = {
            "direction": direction,
            "server": server,
            "type": message_type,
            "content": str(content)[:200] if content else None,
            "timestamp": time.time(),
        }
        self._mcp_messages.append(message_info)

        arrow = "→" if direction == "send" else "←"
        logger.debug(f"[MCP {arrow}] server={server}, type={message_type}")

    def log_validation_step(
        self,
        step: str,
        result: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """
        Log a validation step.

        Args:
            step: Name of validation step
            result: Result of validation
            details: Additional details
        """
        if not self.config.enabled or not self.config.log_validation:
            return

        logger.debug(f"[VALIDATION] {step}: {result}")
        if details:
            for key, value in details.items():
                logger.debug(f"  {key}: {value}")

    def log_error(self, error: Exception, context: str = "") -> None:
        """
        Log an error with optional stack trace.

        Args:
            error: The exception
            context: Additional context
        """
        if not self.config.enabled:
            return

        msg = f"[ERROR] {context}: {type(error).__name__}: {error}"
        if self.config.include_stack_traces:
            logger.exception(msg)
        else:
            logger.error(msg)

    def get_timing_stats(self) -> dict[str, dict[str, float]]:
        """Get all timing statistics."""
        return {
            name: {
                "count": stats.count,
                "total": stats.total_time,
                "avg": stats.avg_time,
                "min": stats.min_time if stats.count > 0 else 0,
                "max": stats.max_time,
            }
            for name, stats in self._timings.items()
        }

    def get_llm_stats(self) -> dict[str, Any]:
        """Get LLM call statistics."""
        if not self._llm_calls:
            return {"total_calls": 0}

        total_prompt = sum(c["prompt_tokens"] for c in self._llm_calls)
        total_response = sum(c["response_tokens"] for c in self._llm_calls)
        total_time = sum(c["elapsed"] for c in self._llm_calls)
        success_count = sum(1 for c in self._llm_calls if c["success"])

        return {
            "total_calls": len(self._llm_calls),
            "successful_calls": success_count,
            "total_prompt_tokens": total_prompt,
            "total_response_tokens": total_response,
            "total_time": total_time,
        }

    def clear(self) -> None:
        """Clear all logged data."""
        self._timings.clear()
        self._llm_calls.clear()
        self._mcp_messages.clear()
