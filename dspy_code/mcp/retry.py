"""
Retry controller for MCP operations with exponential backoff.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Awaitable, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.
        
        Args:
            attempt: The attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


class RetryController:
    """
    Controller for executing operations with exponential backoff retry.
    
    This controller handles transient failures by retrying operations
    with increasing delays between attempts.
    """
    
    def __init__(self, config: RetryConfig | None = None):
        """
        Initialize the retry controller.
        
        Args:
            config: Retry configuration. Uses defaults if not provided.
        """
        self.config = config or RetryConfig()
    
    async def execute_with_retry(
        self,
        operation: Callable[[], Awaitable[T]],
        operation_name: str = "operation",
        on_retry: Callable[[int, Exception, float], None] | None = None,
        should_retry: Callable[[Exception], bool] | None = None,
    ) -> T:
        """
        Execute an async operation with exponential backoff retry.
        
        Args:
            operation: Async callable to execute
            operation_name: Name of the operation for logging
            on_retry: Optional callback called before each retry.
                      Receives (attempt_number, exception, delay_seconds)
            should_retry: Optional predicate to determine if an exception
                         should trigger a retry. Defaults to retrying all exceptions.
        
        Returns:
            The result of the operation
            
        Raises:
            The last exception if all retries fail
        """
        last_error: Exception | None = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return await operation()
            except Exception as e:
                last_error = e
                
                # Check if we should retry this exception
                if should_retry is not None and not should_retry(e):
                    logger.debug(
                        f"{operation_name}: Not retrying due to exception type: {type(e).__name__}"
                    )
                    raise
                
                # Check if we have more attempts
                if attempt >= self.config.max_attempts - 1:
                    logger.warning(
                        f"{operation_name}: All {self.config.max_attempts} attempts failed"
                    )
                    raise
                
                # Calculate delay
                delay = self.config.calculate_delay(attempt)
                
                logger.info(
                    f"{operation_name}: Attempt {attempt + 1} failed with {type(e).__name__}: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                # Call retry callback if provided
                if on_retry:
                    on_retry(attempt + 1, e, delay)
                
                # Wait before retry
                await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        if last_error:
            raise last_error
        raise RuntimeError(f"{operation_name}: Unexpected state - no result and no error")
    
    def execute_sync_with_retry(
        self,
        operation: Callable[[], T],
        operation_name: str = "operation",
        on_retry: Callable[[int, Exception, float], None] | None = None,
        should_retry: Callable[[Exception], bool] | None = None,
    ) -> T:
        """
        Execute a synchronous operation with exponential backoff retry.
        
        Args:
            operation: Callable to execute
            operation_name: Name of the operation for logging
            on_retry: Optional callback called before each retry
            should_retry: Optional predicate to determine if an exception
                         should trigger a retry
        
        Returns:
            The result of the operation
            
        Raises:
            The last exception if all retries fail
        """
        import time
        
        last_error: Exception | None = None
        
        for attempt in range(self.config.max_attempts):
            try:
                return operation()
            except Exception as e:
                last_error = e
                
                if should_retry is not None and not should_retry(e):
                    raise
                
                if attempt >= self.config.max_attempts - 1:
                    raise
                
                delay = self.config.calculate_delay(attempt)
                
                logger.info(
                    f"{operation_name}: Attempt {attempt + 1} failed. Retrying in {delay:.1f}s..."
                )
                
                if on_retry:
                    on_retry(attempt + 1, e, delay)
                
                time.sleep(delay)
        
        if last_error:
            raise last_error
        raise RuntimeError(f"{operation_name}: Unexpected state")
