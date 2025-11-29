"""
Main RAG orchestrator for codebase knowledge.

This module provides the main interface for the RAG system, coordinating
between indexing, search, and context building for LLM requests.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..core.config import ConfigManager
from .indexer import CodeIndexer
from .models import SearchResult
from .search import CodeSearch

logger = logging.getLogger(__name__)


class CodebaseRAG:
    """Main orchestrator for codebase RAG system.

    Coordinates indexing, search, and context building to provide
    LLMs with relevant code examples from installed packages.
    """

    def __init__(self, config_manager: ConfigManager | None = None, cache_dir: Path | None = None):
        """Initialize the RAG system.

        Args:
            config_manager: Configuration manager
            cache_dir: Cache directory (defaults to .dspy_code/cache/codebase_index in CWD)
        """
        self.config_manager = config_manager
        self.enabled = self._is_enabled()

        if not self.enabled:
            logger.info("CodebaseRAG is disabled in config")
            self.indexer = None
            self.search = None
            self.index = None
            return

        # Initialize indexer
        self.indexer = CodeIndexer(cache_dir=cache_dir, config_manager=config_manager)

        # Try to load index from cache ONLY (indexing happens during /init)
        try:
            self.index = self.indexer.load_index()

            if self.index is None:
                logger.info("No index found - run /init to build codebase index")
                self.search = None
            else:
                # Check if stale and warn user
                if self.indexer.is_index_stale(self.index):
                    logger.warning("Codebase index is stale - run /init to rebuild")

                # Initialize search with existing index
                self.search = CodeSearch(self.index)
                logger.info(f"CodebaseRAG loaded: {len(self.index.elements)} elements indexed")

        except Exception as e:
            logger.error(f"Failed to load CodebaseRAG index: {e}")
            self.search = None
            self.index = None

    def _is_enabled(self) -> bool:
        """Check if RAG is enabled in config."""
        if not self.config_manager:
            return False  # Default to disabled for faster responses

        try:
            if hasattr(self.config_manager.config, "codebase_rag"):
                rag_config = self.config_manager.config.codebase_rag
                if hasattr(rag_config, "enabled"):
                    return rag_config.enabled
        except:
            pass

        return False  # Default to disabled for faster responses

    def search(self, query: str, top_k: int = 5, strategy: str = "hybrid") -> list[SearchResult]:
        """Search for relevant code snippets.

        Args:
            query: Search query
            top_k: Number of results to return
            strategy: Search strategy ('hybrid', 'semantic', 'keyword')

        Returns:
            List of SearchResult ordered by relevance
        """
        if not self.enabled or not self.search:
            logger.warning("CodebaseRAG not available")
            return []

        try:
            if strategy == "semantic":
                return self.search.semantic_search(query, top_k)
            elif strategy == "keyword":
                return self.search.keyword_search(query, top_k)
            else:  # hybrid
                return self.search.hybrid_search(query, top_k)

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def build_context(self, query: str, max_tokens: int = 4000, top_k: int = 5) -> str:
        """Build comprehensive context string for LLM with relevant code from DSPy and GEPA.

        Similar to Claude Code/Gemini CLI - provides rich context from actual source code.

        Args:
            query: User's query or request
            max_tokens: Maximum tokens to include in context
            top_k: Number of code snippets to retrieve

        Returns:
            Formatted context string with code examples from DSPy and GEPA source code
        """
        if not self.enabled or not self.search:
            return ""

        try:
            # Search for relevant code (hybrid search for best results)
            results = self.search.hybrid_search(query, top_k)

            if not results:
                return ""

            # Build context with token awareness and source attribution
            context_parts = []
            context_parts.append("# Relevant Code Examples from DSPy and GEPA Source Code\n")
            context_parts.append("# These examples are from the user's installed packages\n")

            estimated_tokens = 0
            included_count = 0
            codebases_seen = set()

            for result in results:
                snippet = result.to_snippet()
                formatted = snippet.format_for_llm()

                # Track codebases for summary
                if hasattr(snippet, "codebase_name") and snippet.codebase_name:
                    codebases_seen.add(snippet.codebase_name)
                elif snippet.element.codebase:
                    codebases_seen.add(snippet.element.codebase)

                # Rough token estimation (1 token ≈ 4 characters)
                # Note: format_for_llm() already includes source attribution
                snippet_tokens = len(formatted) // 4

                if estimated_tokens + snippet_tokens > max_tokens:
                    break

                # Add formatted snippet (already includes source info from format_for_llm)
                context_parts.append(formatted)
                context_parts.append("")  # Empty line between snippets
                estimated_tokens += snippet_tokens
                included_count += 1

            if included_count == 0:
                return ""

            # Add summary
            codebase_list = ", ".join(sorted(codebases_seen)) if codebases_seen else "DSPy/GEPA"
            context_parts.append(
                f"\n# Summary: {included_count} relevant code example(s) from {codebase_list} source code\n"
            )
            context_parts.append(
                "# Use these examples as reference for syntax, patterns, and best practices\n"
            )

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Failed to build context: {e}")
            return ""

    def refresh_index(self, force: bool = False) -> bool:
        """Refresh the code index.

        Args:
            force: Force rebuild even if cache is fresh

        Returns:
            True if refresh successful
        """
        if not self.enabled or not self.indexer:
            logger.warning("CodebaseRAG not available")
            return False

        try:
            logger.info("Refreshing code index...")
            self.index = self.indexer.build_index(force=force)

            # Reinitialize search with new index
            self.search = CodeSearch(self.index)

            logger.info(f"Index refreshed: {len(self.index.elements)} elements")
            return True

        except Exception as e:
            logger.error(f"Failed to refresh index: {e}")
            return False

    def get_index_status(self) -> dict[str, Any]:
        """Get current index status and statistics.

        Returns:
            Dictionary with index information
        """
        if not self.enabled:
            return {"enabled": False, "status": "disabled"}

        if not self.index:
            return {"enabled": True, "status": "not_initialized", "error": "Index not available"}

        try:
            # Calculate age
            age = datetime.now() - self.index.created_at
            age_days = age.days
            age_hours = age.seconds // 3600

            # Get cache size
            cache_size_bytes = self.indexer.get_cache_size() if self.indexer else 0
            cache_size_mb = cache_size_bytes / (1024 * 1024)

            # Build status
            status = {
                "enabled": True,
                "status": "ready",
                "version": self.index.version,
                "created_at": self.index.created_at.isoformat(),
                "age_days": age_days,
                "age_hours": age_hours,
                "is_stale": self.indexer.is_index_stale(self.index) if self.indexer else False,
                "total_elements": len(self.index.elements),
                "total_codebases": len(self.index.codebases),
                "cache_size_mb": round(cache_size_mb, 2),
                "codebases": {},
            }

            # Add per-codebase stats
            for name, info in self.index.codebases.items():
                status["codebases"][name] = {
                    "version": info.version,
                    "file_count": info.file_count,
                    "element_count": info.element_count,
                    "last_indexed": info.last_indexed.isoformat(),
                }

            return status

        except Exception as e:
            logger.error(f"Failed to get index status: {e}")
            return {"enabled": True, "status": "error", "error": str(e)}

    def search_by_name(self, name: str, exact: bool = False) -> list[SearchResult]:
        """Search for code elements by name.

        Args:
            name: Name to search for
            exact: Whether to require exact match

        Returns:
            List of matching elements
        """
        if not self.enabled or not self.search:
            return []

        try:
            return self.search.search_by_name(name, exact)
        except Exception as e:
            logger.error(f"Name search failed: {e}")
            return []

    def search_by_type(
        self, element_type: str, query: str | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        """Search for elements of a specific type.

        Args:
            element_type: Type to search for ('function', 'class', 'method')
            query: Optional query to filter results
            top_k: Number of results to return

        Returns:
            List of matching elements
        """
        if not self.enabled or not self.search:
            return []

        try:
            return self.search.search_by_type(element_type, query, top_k)
        except Exception as e:
            logger.error(f"Type search failed: {e}")
            return []

    def search_by_codebase(
        self, codebase: str, query: str | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        """Search within a specific codebase.

        Args:
            codebase: Codebase to search in
            query: Optional query to filter results
            top_k: Number of results to return

        Returns:
            List of matching elements
        """
        if not self.enabled or not self.search:
            return []

        try:
            return self.search.search_by_codebase(codebase, query, top_k)
        except Exception as e:
            logger.error(f"Codebase search failed: {e}")
            return []

    def get_element_by_name(self, name: str) -> Any | None:
        """Get a specific code element by name.

        Args:
            name: Name of the element

        Returns:
            CodeElement if found, None otherwise
        """
        if not self.enabled or not self.index:
            return None

        return self.index.get_element_by_name(name)

    def clear_cache(self) -> None:
        """Clear all caches (search cache and index cache)."""
        if self.search:
            self.search.clear_cache()

        if self.indexer:
            self.indexer.clear_cache()

        logger.info("All caches cleared")
