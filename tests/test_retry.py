"""
Tests for MCP retry controller.
"""

import asyncio
import pytest
from hypothesis import given, strategies as st, assume

from dspy_code.mcp.retry import RetryConfig, RetryController


class TestRetryConfig:
    """Tests for RetryConfig."""

    # **Feature: dspy-code-improvements, Property 6: Retry Delay Exponential Growth**
    @given(
        base_delay=st.floats(min_value=0.1, max_value=5.0),
        exponential_base=st.floats(min_value=1.5, max_value=3.0),
        max_delay=st.floats(min_value=10.0, max_value=100.0),
        attempt=st.integers(min_value=0, max_value=10),
    )
    def test_delay_follows_exponential_growth(
        self,
        base_delay: float,
        exponential_base: float,
        max_delay: float,
        attempt: int,
    ):
        """
        Property 6: Retry Delay Exponential Growth
        
        For any sequence of retry attempts, the delay between attempts SHALL
        follow exponential backoff (delay_n = base * exponential_base^n) up to max_delay.
        
        **Validates: Requirements 5.1**
        """
        config = RetryConfig(
            base_delay=base_delay,
            exponential_base=exponential_base,
            max_delay=max_delay,
        )
        
        delay = config.calculate_delay(attempt)
        expected = min(base_delay * (exponential_base ** attempt), max_delay)
        
        assert abs(delay - expected) < 0.0001, f"Expected {expected}, got {delay}"

    def test_delay_capped_at_max(self):
        """Test that delay is capped at max_delay."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=10.0)
        
        # After many attempts, delay should be capped
        delay = config.calculate_delay(100)
        assert delay == 10.0


class TestRetryController:
    """Tests for RetryController."""

    # **Feature: dspy-code-improvements, Property 7: Retry Count Limit**
    @given(
        max_attempts=st.integers(min_value=1, max_value=5),
    )
    def test_respects_max_retry_count(self, max_attempts: int):
        """
        Property 7: Retry Count Limit
        
        For any RetryConfig with max_attempts=N, the retry controller SHALL
        make at most N attempts before raising the final error.
        
        **Validates: Requirements 5.2**
        """
        config = RetryConfig(max_attempts=max_attempts, base_delay=0.001)
        controller = RetryController(config)
        
        attempt_count = 0
        
        def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            controller.execute_sync_with_retry(failing_operation, "test_op")
        
        assert attempt_count == max_attempts, f"Expected {max_attempts} attempts, got {attempt_count}"

    @pytest.mark.asyncio
    async def test_async_retry_respects_max_attempts(self):
        """Test async retry respects max attempts."""
        config = RetryConfig(max_attempts=3, base_delay=0.001)
        controller = RetryController(config)
        
        attempt_count = 0
        
        async def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            raise ConnectionError("Connection failed")
        
        with pytest.raises(ConnectionError):
            await controller.execute_with_retry(failing_operation, "test_async_op")
        
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_async_retry_succeeds_on_later_attempt(self):
        """Test that retry succeeds if operation eventually works."""
        config = RetryConfig(max_attempts=5, base_delay=0.001)
        controller = RetryController(config)
        
        attempt_count = 0
        
        async def eventually_succeeds():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise ConnectionError("Not yet")
            return "success"
        
        result = await controller.execute_with_retry(eventually_succeeds, "test_op")
        
        assert result == "success"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_on_retry_callback_called(self):
        """Test that on_retry callback is called before each retry."""
        config = RetryConfig(max_attempts=3, base_delay=0.001)
        controller = RetryController(config)
        
        retry_calls = []
        
        def on_retry(attempt, error, delay):
            retry_calls.append((attempt, type(error).__name__, delay))
        
        async def failing_operation():
            raise ValueError("Fail")
        
        with pytest.raises(ValueError):
            await controller.execute_with_retry(
                failing_operation, "test_op", on_retry=on_retry
            )
        
        # Should have 2 retry callbacks (before attempts 2 and 3)
        assert len(retry_calls) == 2
        assert retry_calls[0][0] == 1  # First retry
        assert retry_calls[1][0] == 2  # Second retry

    @pytest.mark.asyncio
    async def test_should_retry_predicate(self):
        """Test that should_retry predicate controls retry behavior."""
        config = RetryConfig(max_attempts=5, base_delay=0.001)
        controller = RetryController(config)
        
        attempt_count = 0
        
        async def failing_operation():
            nonlocal attempt_count
            attempt_count += 1
            raise ValueError("Don't retry this")
        
        def should_retry(e):
            # Only retry ConnectionError, not ValueError
            return isinstance(e, ConnectionError)
        
        with pytest.raises(ValueError):
            await controller.execute_with_retry(
                failing_operation, "test_op", should_retry=should_retry
            )
        
        # Should only attempt once since ValueError is not retryable
        assert attempt_count == 1

    def test_sync_retry_succeeds_on_later_attempt(self):
        """Test sync retry succeeds if operation eventually works."""
        config = RetryConfig(max_attempts=5, base_delay=0.001)
        controller = RetryController(config)
        
        attempt_count = 0
        
        def eventually_succeeds():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise ConnectionError("Not yet")
            return "success"
        
        result = controller.execute_sync_with_retry(eventually_succeeds, "test_op")
        
        assert result == "success"
        assert attempt_count == 2
