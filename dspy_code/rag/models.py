"""
Data models for the codebase RAG system.

This module defines the core data structures used for indexing and retrieving
source code from installed packages.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class CodeElement:
    """Represents a code element (function, class, method) extracted from source code.

    Attributes:
        type: Type of element ('function', 'class', 'method')
        name: Name of the element
        signature: Full signature (e.g., 'def foo(x: int) -> str')
        docstring: Docstring if available
        code: Full source code of the element
        file_path: Path to the source file
        line_start: Starting line number
        line_end: Ending line number
        codebase: Source codebase ('dspy-cli', 'dspy', 'gepa', 'mcp')
        imports: List of import statements in the file
        decorators: List of decorators applied to the element
    """

    type: str
    name: str
    signature: str
    docstring: str | None
    code: str
    file_path: str
    line_start: int
    line_end: int
    codebase: str
    imports: list[str] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type,
            "name": self.name,
            "signature": self.signature,
            "docstring": self.docstring,
            "code": self.code,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "codebase": self.codebase,
            "imports": self.imports,
            "decorators": self.decorators,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeElement":
        """Create from dictionary."""
        return cls(**data)


@dataclass
class CodeSnippet:
    """Represents a retrieved code snippet with context.

    Attributes:
        element: The code element
        relevance_score: Relevance score from search (0.0 to 1.0)
        context_before: Lines of code before the element
        context_after: Lines of code after the element
        related_elements: Related code elements (e.g., base classes, called functions)
    """

    element: CodeElement
    relevance_score: float
    context_before: str = ""
    context_after: str = ""
    related_elements: list[CodeElement] = field(default_factory=list)

    @property
    def codebase_name(self) -> str:
        """Get the codebase name from the element."""
        return self.element.codebase

    @property
    def file_path(self) -> str:
        """Get the file path from the element."""
        return self.element.file_path

    def format_for_llm(self) -> str:
        """Format the snippet for inclusion in LLM context with source attribution."""
        lines = []

        # Header with file path and line numbers (like Claude Code/Gemini CLI)
        file_name = Path(self.element.file_path).name
        lines.append(
            f"# From {self.element.codebase}/{file_name}:{self.element.line_start}-{self.element.line_end}"
        )

        # Add docstring if available (helpful context)
        if self.element.docstring:
            lines.append(f"# Docstring: {self.element.docstring[:200]}...")

        lines.append("")

        # Context before (if any)
        if self.context_before:
            lines.append(self.context_before)

        # Main code
        lines.append(self.element.code)

        # Context after (if any)
        if self.context_after:
            lines.append(self.context_after)

        return "\n".join(lines)


@dataclass
class CodebaseInfo:
    """Information about an indexed codebase.

    Attributes:
        name: Name of the codebase ('dspy-cli', 'dspy', etc.)
        path: Path to the codebase root
        version: Version string if available
        file_count: Number of Python files indexed
        element_count: Number of code elements extracted
        last_indexed: Timestamp of last indexing
    """

    name: str
    path: str
    version: str | None
    file_count: int
    element_count: int
    last_indexed: datetime

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "path": self.path,
            "version": self.version,
            "file_count": self.file_count,
            "element_count": self.element_count,
            "last_indexed": self.last_indexed.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodebaseInfo":
        """Create from dictionary."""
        data["last_indexed"] = datetime.fromisoformat(data["last_indexed"])
        return cls(**data)


@dataclass
class CodeIndex:
    """Complete code index containing all indexed codebases.

    Attributes:
        version: Index format version
        created_at: When the index was created
        codebases: Dictionary of codebase name to info
        elements: List of all code elements
        metadata: Additional metadata
    """

    version: str
    created_at: datetime
    codebases: dict[str, CodebaseInfo]
    elements: list[CodeElement]
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "codebases": {name: info.to_dict() for name, info in self.codebases.items()},
            "elements": [elem.to_dict() for elem in self.elements],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeIndex":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["codebases"] = {
            name: CodebaseInfo.from_dict(info) for name, info in data["codebases"].items()
        }
        data["elements"] = [CodeElement.from_dict(elem) for elem in data["elements"]]
        return cls(**data)

    def get_elements_by_codebase(self, codebase: str) -> list[CodeElement]:
        """Get all elements from a specific codebase."""
        return [elem for elem in self.elements if elem.codebase == codebase]

    def get_elements_by_type(self, element_type: str) -> list[CodeElement]:
        """Get all elements of a specific type."""
        return [elem for elem in self.elements if elem.type == element_type]

    def get_element_by_name(self, name: str) -> CodeElement | None:
        """Find an element by name (returns first match)."""
        for elem in self.elements:
            if elem.name == name:
                return elem
        return None


@dataclass
class SearchResult:
    """Result from a code search operation.

    Attributes:
        element: The matched code element
        score: Relevance score
        match_type: Type of match ('exact', 'semantic', 'keyword')
        matched_terms: Terms that matched in the search
    """

    element: CodeElement
    score: float
    match_type: str
    matched_terms: list[str] = field(default_factory=list)

    def to_snippet(self, context_lines: int = 3) -> CodeSnippet:
        """Convert to a CodeSnippet with context."""
        # TODO: Load context from file if needed
        return CodeSnippet(
            element=self.element,
            relevance_score=self.score,
            context_before="",
            context_after="",
            related_elements=[],
        )
