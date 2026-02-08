"""
Tests for code generation cache.
"""

import time

import pytest
from hypothesis import given, strategies as st

from dspy_code.models.cache import CacheConfig, CacheEntry, CodeGenerationCache
from dspy_code.models.task_collector import FieldDefinition, ReasoningPattern, TaskDefinition


def make_task_def(description: str = "Test task", input_name: str = "input", output_name: str = "output") -> TaskDefinition:
    """Helper to create a TaskDefinition."""
    return TaskDefinition(
        description=description,
        input_fields=[FieldDefinition(name=input_name, type="str", description="Input field")],
        output_fields=[FieldDefinition(name=output_name, type="str", description="Output field")],
        complexity="simple",
        domain="test",
    )


def make_pattern(pattern_type: str = "predict") -> ReasoningPattern:
    """Helper to create a ReasoningPattern."""
    return ReasoningPattern(type=pattern_type, config={})


class TestCacheKeyDeterminism:
    """Tests for cache key computation."""

    # **Feature: dspy-code-improvements, Property 8: Cache Key Determinism**
    @given(
        description=st.text(min_size=1, max_size=50),
        input_name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=20),
        output_name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=20),
        pattern_type=st.sampled_from(["predict", "chain_of_thought", "react"]),
    )
    def test_cache_key_is_deterministic(
        self,
        description: str,
        input_name: str,
        output_name: str,
        pattern_type: str,
    ):
        """
        Property 8: Cache Key Determinism

        For any TaskDefinition and ReasoningPattern, computing the cache key
        multiple times SHALL produce the same result.

        **Validates: Requirements 6.1**
        """
        cache = CodeGenerationCache()
        task_def = make_task_def(description, input_name, output_name)
        pattern = make_pattern(pattern_type)

        key1 = cache._compute_key(task_def, pattern)
        key2 = cache._compute_key(task_def, pattern)
        key3 = cache._compute_key(task_def, pattern)

        assert key1 == key2 == key3


class TestCacheHitBehavior:
    """Tests for cache hit/miss behavior."""

    # **Feature: dspy-code-improvements, Property 9: Cache Hit Returns Cached Value**
    def test_cache_hit_returns_cached_value(self):
        """
        Property 9: Cache Hit Returns Cached Value

        For any cached code generation result, requesting the same task definition
        and pattern SHALL return the cached value without invoking the generator.

        **Validates: Requirements 6.2**
        """
        cache = CodeGenerationCache()
        task_def = make_task_def()
        pattern = make_pattern()

        # Create a mock result
        mock_result = "cached_program"

        # Put in cache
        cache.put(task_def, pattern, mock_result)

        # Get should return the same value
        result = cache.get(task_def, pattern)
        assert result == mock_result

        # Verify it was a hit
        assert cache._hits == 1
        assert cache._misses == 0

    def test_cache_miss_returns_none(self):
        """Test that cache miss returns None."""
        cache = CodeGenerationCache()
        task_def = make_task_def()
        pattern = make_pattern()

        result = cache.get(task_def, pattern)
        assert result is None
        assert cache._misses == 1

    def test_different_tasks_have_different_keys(self):
        """Test that different tasks produce different cache keys."""
        cache = CodeGenerationCache()
        task1 = make_task_def("Task one")
        task2 = make_task_def("Task two")
        pattern = make_pattern()

        key1 = cache._compute_key(task1, pattern)
        key2 = cache._compute_key(task2, pattern)

        assert key1 != key2


class TestLRUEviction:
    """Tests for LRU eviction behavior."""

    # **Feature: dspy-code-improvements, Property 10: LRU Eviction**
    @given(
        max_size=st.integers(min_value=1, max_value=10),
    )
    def test_lru_eviction_respects_max_size(self, max_size: int):
        """
        Property 10: LRU Eviction

        For any cache with max_size=N, after inserting N+1 items,
        the least recently used item SHALL be evicted.

        **Validates: Requirements 6.3**
        """
        config = CacheConfig(max_size=max_size)
        cache = CodeGenerationCache(config)

        # Insert max_size + 1 items
        for i in range(max_size + 1):
            task_def = make_task_def(f"Task {i}")
            pattern = make_pattern()
            cache.put(task_def, pattern, f"result_{i}")

        # Cache size should be at max_size
        assert cache.size == max_size

    def test_lru_evicts_oldest_item(self):
        """Test that LRU eviction removes the oldest item."""
        config = CacheConfig(max_size=2)
        cache = CodeGenerationCache(config)

        task1 = make_task_def("Task 1")
        task2 = make_task_def("Task 2")
        task3 = make_task_def("Task 3")
        pattern = make_pattern()

        # Add first two items
        cache.put(task1, pattern, "result_1")
        cache.put(task2, pattern, "result_2")

        # Access task1 to make it recently used
        cache.get(task1, pattern)

        # Add third item - should evict task2 (least recently used)
        cache.put(task3, pattern, "result_3")

        # task1 should still be there
        assert cache.get(task1, pattern) == "result_1"
        # task2 should be evicted
        assert cache.get(task2, pattern) is None
        # task3 should be there
        assert cache.get(task3, pattern) == "result_3"


class TestCacheExpiration:
    """Tests for TTL-based expiration."""

    def test_expired_entries_are_not_returned(self):
        """Test that expired entries return None."""
        config = CacheConfig(ttl_seconds=1)
        cache = CodeGenerationCache(config)

        task_def = make_task_def()
        pattern = make_pattern()

        cache.put(task_def, pattern, "result")

        # Should be available immediately
        assert cache.get(task_def, pattern) == "result"

        # Manually expire the entry
        key = cache._compute_key(task_def, pattern)
        cache._cache[key].created_at = time.time() - 2  # 2 seconds ago

        # Should now return None
        assert cache.get(task_def, pattern) is None


class TestCacheDisabled:
    """Tests for disabled cache behavior."""

    def test_disabled_cache_always_returns_none(self):
        """Test that disabled cache returns None on get."""
        config = CacheConfig(enabled=False)
        cache = CodeGenerationCache(config)

        task_def = make_task_def()
        pattern = make_pattern()

        cache.put(task_def, pattern, "result")
        assert cache.get(task_def, pattern) is None

    def test_disabled_cache_does_not_store(self):
        """Test that disabled cache doesn't store entries."""
        config = CacheConfig(enabled=False)
        cache = CodeGenerationCache(config)

        task_def = make_task_def()
        pattern = make_pattern()

        cache.put(task_def, pattern, "result")
        assert cache.size == 0


class TestCacheStats:
    """Tests for cache statistics."""

    def test_stats_tracking(self):
        """Test that cache tracks hits and misses."""
        cache = CodeGenerationCache()
        task_def = make_task_def()
        pattern = make_pattern()

        # Miss
        cache.get(task_def, pattern)

        # Put and hit
        cache.put(task_def, pattern, "result")
        cache.get(task_def, pattern)
        cache.get(task_def, pattern)

        stats = cache.stats
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 2 / 3
