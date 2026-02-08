"""
Tests for streaming support.
"""

import asyncio
import pytest

from dspy_code.models.streaming import (
    StreamConfig,
    StreamManager,
    StreamingFallback,
    supports_streaming,
)


class TestStreamManager:
    """Tests for StreamManager."""

    @pytest.mark.asyncio
    async def test_stream_collects_all_tokens(self):
        """Test that streaming collects all tokens."""
        manager = StreamManager()

        async def token_generator():
            for token in ["Hello", " ", "World", "!"]:
                yield token

        result = await manager.stream_response(token_generator())
        assert result == "Hello World!"

    @pytest.mark.asyncio
    async def test_stream_calls_on_token_callback(self):
        """Test that on_token callback is called."""
        manager = StreamManager()
        received_tokens = []

        def on_token(token):
            received_tokens.append(token)

        async def token_generator():
            for token in ["A", "B", "C"]:
                yield token

        await manager.stream_response(token_generator(), on_token=on_token)
        assert "".join(received_tokens) == "ABC"

    @pytest.mark.asyncio
    async def test_stream_cancellation(self):
        """Test that stream can be cancelled."""
        manager = StreamManager()
        received_tokens = []

        async def slow_generator():
            for i in range(10):
                yield str(i)
                if i == 2:
                    manager.cancel()
                await asyncio.sleep(0.01)

        result = await manager.stream_response(slow_generator())

        # Should have stopped after cancellation
        assert len(result) <= 4  # "0", "1", "2", maybe "3"
        assert manager.is_cancelled

    @pytest.mark.asyncio
    async def test_stream_handles_errors_gracefully(self):
        """Test that stream handles errors gracefully."""
        manager = StreamManager()

        async def failing_generator():
            yield "Start"
            raise ConnectionError("Connection lost")

        result = await manager.stream_response(failing_generator())
        assert result == "Start"

    def test_sync_stream_processes_tokens(self):
        """Test synchronous token processing."""
        manager = StreamManager()
        tokens = ["Hello", " ", "World"]

        result = manager.stream_response_sync(tokens)
        assert result == "Hello World"

    def test_reset_clears_state(self):
        """Test that reset clears manager state."""
        manager = StreamManager()
        manager.cancel()
        manager._buffer = ["leftover"]

        manager.reset()

        assert not manager.is_cancelled
        assert len(manager._buffer) == 0


class TestSupportsStreaming:
    """Tests for supports_streaming function."""

    def test_openai_models_support_streaming(self):
        """Test that OpenAI models are detected as streaming-capable."""
        assert supports_streaming("openai/gpt-4o")
        assert supports_streaming("gpt-4")
        assert supports_streaming("gpt-3.5-turbo")

    def test_anthropic_models_support_streaming(self):
        """Test that Anthropic models are detected as streaming-capable."""
        assert supports_streaming("anthropic/claude-3")
        assert supports_streaming("claude-sonnet-4")

    def test_ollama_models_support_streaming(self):
        """Test that Ollama models are detected as streaming-capable."""
        assert supports_streaming("ollama/llama3")
        assert supports_streaming("ollama/mistral")

    def test_unknown_models_may_not_support_streaming(self):
        """Test that unknown models return False."""
        assert not supports_streaming("unknown-model-xyz")


class TestStreamingFallback:
    """Tests for StreamingFallback."""

    @pytest.mark.asyncio
    async def test_fallback_chunks_response(self):
        """Test that fallback chunks the response."""
        fallback = StreamingFallback(chunk_size=5)
        response = "Hello World!"

        chunks = []
        async for chunk in fallback.simulate_stream(response):
            chunks.append(chunk)

        assert "".join(chunks) == response
        assert len(chunks) == 3  # "Hello", " Worl", "d!"

    @pytest.mark.asyncio
    async def test_fallback_handles_empty_response(self):
        """Test that fallback handles empty response."""
        fallback = StreamingFallback()

        chunks = []
        async for chunk in fallback.simulate_stream(""):
            chunks.append(chunk)

        assert chunks == []


class TestStreamConfig:
    """Tests for StreamConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = StreamConfig()
        assert config.enabled is True
        assert config.buffer_size == 1
        assert config.show_progress is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = StreamConfig(enabled=False, buffer_size=10, show_progress=False)
        assert config.enabled is False
        assert config.buffer_size == 10
        assert config.show_progress is False
