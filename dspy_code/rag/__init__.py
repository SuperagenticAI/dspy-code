"""
RAG (Retrieval-Augmented Generation) system for codebase knowledge.

This package provides functionality to index, search, and retrieve source code
from installed packages (dspy-cli, dspy, gepa, mcp) to enhance LLM responses
with real code examples.
"""

from .codebase_rag import CodebaseRAG
from .indexer import CodeIndexer
from .models import CodebaseInfo, CodeElement, CodeIndex, CodeSnippet, SearchResult
from .search import CodeSearch

__all__ = [
    "CodeElement",
    "CodeIndex",
    "CodeIndexer",
    "CodeSearch",
    "CodeSnippet",
    "CodebaseInfo",
    "CodebaseRAG",
    "SearchResult",
]
