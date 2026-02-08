"""
Stream manager for handling streaming LLM responses.
"""

import asyncio
import logging
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass
from typing import Any

from rich.console import Console

logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    """Configuration for streaming behavior."""

    enabled: bool = True
    buffer_size: int = 1  # Number of tokens to buffer before display
    show_progress: bool = True


class StreamManager:
    """
    Manager for streaming LLM responses.

    Handles token-by-token display, cancellation, and graceful
    handling of interrupted streams.
    """

    def __init__(self, console: Console | None = None, config: StreamConfig | None = None):
        """
        Initialize the stream manager.

        Args:
            console: Rich console for output. Creates new one if not provided.
            config: Streaming configuration.
        """
        self.console = console or Console()
        self.config = config or StreamConfig()
        self._cancelled = False
        self._buffer: list[str] = []

    async def stream_response(
        self,
        stream: AsyncIterator[str],
        on_token: Callable[[str], None] | None = None,
    ) -> str:
        """
        Stream tokens to console and collect full response.

        Args:
            stream: Async iterator yielding tokens
            on_token: Optional callback for each token

        Returns:
            Complete response string
        """
        self._cancelled = False
        full_response: list[str] = []

        try:
            async for token in stream:
                if self._cancelled:
                    logger.info("Stream cancelled by user")
                    break

                full_response.append(token)
                self._buffer.append(token)

                # Flush buffer when it reaches buffer_size
                if len(self._buffer) >= self.config.buffer_size:
                    self._flush_buffer(on_token)

        except asyncio.CancelledError:
            logger.info("Stream cancelled via asyncio")
        except Exception as e:
            logger.warning(f"Stream interrupted: {e}")

        # Flush any remaining buffer
        self._flush_buffer(on_token)

        return "".join(full_response)

    def stream_response_sync(
        self,
        tokens: list[str],
        on_token: Callable[[str], None] | None = None,
    ) -> str:
        """
        Process tokens synchronously (for non-streaming fallback).

        Args:
            tokens: List of tokens to process
            on_token: Optional callback for each token

        Returns:
            Complete response string
        """
        self._cancelled = False
        full_response: list[str] = []

        for token in tokens:
            if self._cancelled:
                break

            full_response.append(token)

            if on_token:
                on_token(token)
            else:
                self.console.print(token, end="")

        # Print newline at end
        if not on_token:
            self.console.print()

        return "".join(full_response)

    def _flush_buffer(self, on_token: Callable[[str], None] | None) -> None:
        """Flush the token buffer to output."""
        if not self._buffer:
            return

        combined = "".join(self._buffer)
        self._buffer.clear()

        if on_token:
            on_token(combined)
        else:
            self.console.print(combined, end="")

    def cancel(self) -> None:
        """Cancel ongoing stream."""
        self._cancelled = True
        logger.debug("Stream cancellation requested")

    @property
    def is_cancelled(self) -> bool:
        """Check if stream has been cancelled."""
        return self._cancelled

    def reset(self) -> None:
        """Reset the stream manager state."""
        self._cancelled = False
        self._buffer.clear()


def supports_streaming(model_name: str) -> bool:
    """
    Check if a model supports streaming.

    Args:
        model_name: Name of the model

    Returns:
        True if model supports streaming
    """
    # Most modern LLM APIs support streaming
    streaming_providers = [
        "openai",
        "anthropic",
        "gemini",
        "ollama",
        "gpt",
        "claude",
    ]

    model_lower = model_name.lower()
    return any(provider in model_lower for provider in streaming_providers)


class StreamingFallback:
    """
    Fallback handler for non-streaming responses.

    Simulates streaming by yielding the response in chunks.
    """

    def __init__(self, chunk_size: int = 10):
        """
        Initialize fallback handler.

        Args:
            chunk_size: Number of characters per chunk
        """
        self.chunk_size = chunk_size

    async def simulate_stream(self, response: str) -> AsyncIterator[str]:
        """
        Simulate streaming by yielding response in chunks.

        Args:
            response: Complete response to chunk

        Yields:
            Response chunks
        """
        for i in range(0, len(response), self.chunk_size):
            chunk = response[i : i + self.chunk_size]
            yield chunk
            # Small delay to simulate streaming
            await asyncio.sleep(0.01)
