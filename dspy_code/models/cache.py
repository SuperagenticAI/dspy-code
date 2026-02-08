"""
Code generation cache with LRU eviction and TTL support.
"""

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .code_generator import GeneratedProgram
    from .task_collector import ReasoningPattern, TaskDefinition


@dataclass
class CacheEntry:
    """Entry in the code generation cache."""

    value: Any
    created_at: float

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if this entry has expired."""
        return time.time() - self.created_at > ttl_seconds


@dataclass
class CacheConfig:
    """Configuration for code generation cache."""

    enabled: bool = True
    max_size: int = 100
    ttl_seconds: int = 3600  # 1 hour default


class CodeGenerationCache:
    """
    LRU cache for code generation results.

    This cache stores generated programs keyed by a hash of the task definition
    and reasoning pattern. It uses LRU eviction when the cache exceeds max_size
    and TTL-based expiration for stale entries.
    """

    def __init__(self, config: CacheConfig | None = None):
        """
        Initialize the cache.

        Args:
            config: Cache configuration. Uses defaults if not provided.
        """
        self.config = config or CacheConfig()
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def _compute_key(
        self,
        task_def: "TaskDefinition",
        pattern: "ReasoningPattern",
    ) -> str:
        """
        Compute a content-based cache key.

        Args:
            task_def: Task definition
            pattern: Reasoning pattern

        Returns:
            Hash string for cache key
        """
        # Build content string from task definition
        content_parts = [
            task_def.description,
            pattern.type,
            str(task_def.complexity),
            str(task_def.domain or ""),
        ]

        # Add input fields
        for field in task_def.input_fields:
            content_parts.extend([field.name, field.type, field.description])

        # Add output fields
        for field in task_def.output_fields:
            content_parts.extend([field.name, field.type, field.description])

        # Add pattern config
        for key, value in sorted(pattern.config.items()):
            content_parts.extend([str(key), str(value)])

        content = ":".join(content_parts)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def get(
        self,
        task_def: "TaskDefinition",
        pattern: "ReasoningPattern",
    ) -> "GeneratedProgram | None":
        """
        Get cached result if available and not expired.

        Args:
            task_def: Task definition
            pattern: Reasoning pattern

        Returns:
            Cached GeneratedProgram if available, None otherwise
        """
        if not self.config.enabled:
            return None

        key = self._compute_key(task_def, pattern)

        if key in self._cache:
            entry = self._cache[key]

            # Check expiration
            if entry.is_expired(self.config.ttl_seconds):
                del self._cache[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

        self._misses += 1
        return None

    def put(
        self,
        task_def: "TaskDefinition",
        pattern: "ReasoningPattern",
        result: "GeneratedProgram",
    ) -> None:
        """
        Cache a generation result.

        Args:
            task_def: Task definition
            pattern: Reasoning pattern
            result: Generated program to cache
        """
        if not self.config.enabled:
            return

        key = self._compute_key(task_def, pattern)

        # Add or update entry
        self._cache[key] = CacheEntry(value=result, created_at=time.time())
        self._cache.move_to_end(key)

        # Evict if needed
        self._evict_if_needed()

    def _evict_if_needed(self) -> None:
        """Evict least recently used entries if cache exceeds max size."""
        while len(self._cache) > self.config.max_size:
            # Remove oldest (first) item
            self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def invalidate(
        self,
        task_def: "TaskDefinition",
        pattern: "ReasoningPattern",
    ) -> bool:
        """
        Invalidate a specific cache entry.

        Args:
            task_def: Task definition
            pattern: Reasoning pattern

        Returns:
            True if entry was found and removed, False otherwise
        """
        key = self._compute_key(task_def, pattern)
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    @property
    def size(self) -> int:
        """Current number of entries in cache."""
        return len(self._cache)

    @property
    def stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            "size": self.size,
            "max_size": self.config.max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
            "enabled": self.config.enabled,
        }
