"""
Project Context Manager

Manages project context for DSPy Code sessions.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from .scanner import ComponentInfo, ProjectScanner, ProjectState


@dataclass
class ProjectContext:
    """Context information about the current project."""

    name: str
    description: str
    directory: str
    use_case: str
    has_dspy_md: bool
    has_config: bool
    components: dict[str, list[ComponentInfo]]
    lm_providers: list[str]
    goals: list[str]
    is_initialized: bool


class ProjectContextManager:
    """Manages project context for CLI sessions."""

    def __init__(self):
        """Initialize the context manager."""
        self._context: ProjectContext | None = None
        self._scanner = ProjectScanner()

    def load_context(self, directory: str = ".") -> ProjectContext | None:
        """
        Load project context from directory.

        Args:
            directory: Directory to load context from

        Returns:
            ProjectContext if found, None otherwise
        """
        directory = Path(directory).resolve()

        # Check if DSPy.md exists
        dspy_md_path = directory / "DSPy.md"
        if dspy_md_path.exists():
            context = self._load_from_dspy_md(str(directory))
        else:
            # Scan directory to create basic context
            state = self._scanner.scan_directory(str(directory))
            context = self._create_from_state(state)

        self._context = context
        return context

    def _load_from_dspy_md(self, directory: str) -> ProjectContext:
        """Load context from DSPy.md file."""
        dspy_md_path = Path(directory) / "DSPy.md"

        try:
            content = dspy_md_path.read_text()

            # Parse DSPy.md content
            name = self._extract_project_name(content)
            description = self._extract_description(content)
            use_case = self._extract_use_case(content)
            goals = self._extract_goals(content)

            # Also scan directory for current state
            state = self._scanner.scan_directory(directory)

            return ProjectContext(
                name=name,
                description=description,
                directory=directory,
                use_case=use_case,
                has_dspy_md=True,
                has_config=state.has_config,
                components=state.components,
                lm_providers=state.lm_providers,
                goals=goals,
                is_initialized=True,
            )

        except Exception:
            # Fallback to scanning if parsing fails
            state = self._scanner.scan_directory(directory)
            return self._create_from_state(state)

    def _create_from_state(self, state: ProjectState) -> ProjectContext:
        """Create context from project state."""
        project_name = os.path.basename(state.directory)

        return ProjectContext(
            name=project_name,
            description=f"DSPy project in {project_name}",
            directory=state.directory,
            use_case="Unknown",
            has_dspy_md=state.has_dspy_md,
            has_config=state.has_config,
            components=state.components,
            lm_providers=state.lm_providers,
            goals=[],
            is_initialized=state.has_dspy_md,
        )

    def _extract_project_name(self, content: str) -> str:
        """Extract project name from DSPy.md content."""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("# DSPy Project:"):
                return line.replace("# DSPy Project:", "").strip()
        return "Unknown Project"

    def _extract_description(self, content: str) -> str:
        """Extract description from DSPy.md content."""
        lines = content.split("\n")
        in_overview = False
        description_lines = []

        for line in lines:
            if line.strip() == "## Overview":
                in_overview = True
                continue
            elif line.startswith("##") and in_overview:
                break
            elif in_overview and line.strip():
                description_lines.append(line.strip())

        return " ".join(description_lines) if description_lines else "No description available"

    def _extract_use_case(self, content: str) -> str:
        """Extract use case from DSPy.md content."""
        lines = content.split("\n")
        in_use_case = False

        for line in lines:
            if line.strip() == "## Use Case":
                in_use_case = True
                continue
            elif line.startswith("##") and in_use_case:
                break
            elif in_use_case and line.strip():
                return line.strip()

        return "Unknown"

    def _extract_goals(self, content: str) -> list[str]:
        """Extract goals from DSPy.md content."""
        lines = content.split("\n")
        in_goals = False
        goals = []

        for line in lines:
            if line.strip() == "## Goals":
                in_goals = True
                continue
            elif line.startswith("##") and in_goals:
                break
            elif in_goals and line.strip().startswith("- [ ]"):
                goal = line.strip().replace("- [ ]", "").strip()
                goals.append(goal)

        return goals

    def get_context(self) -> ProjectContext | None:
        """Get current project context."""
        return self._context

    def has_context(self) -> bool:
        """Check if context is loaded."""
        return self._context is not None

    def get_suggestions(self) -> list[str]:
        """Get context-aware suggestions."""
        if not self._context:
            return ["Use /init to set up your project"]

        suggestions = []

        if not self._context.is_initialized:
            suggestions.append("Use /init to initialize your project")

        if not self._context.components.get("signatures"):
            suggestions.append("Create a signature: /generate signature")

        if self._context.components.get("signatures") and not self._context.components.get(
            "modules"
        ):
            suggestions.append("Create a module: /generate module")

        if self._context.components.get("modules") and not self._context.lm_providers:
            suggestions.append("Configure your LM: edit dspy_config.yaml")

        if not suggestions:
            suggestions.append("Your project looks good! Try /validate to check code quality")

        return suggestions

    def get_component_count(self) -> dict[str, int]:
        """Get count of components by type."""
        if not self._context:
            return {"signatures": 0, "modules": 0, "predictors": 0}

        return {
            "signatures": len(self._context.components.get("signatures", [])),
            "modules": len(self._context.components.get("modules", [])),
            "predictors": len(self._context.components.get("predictors", [])),
        }

    def refresh_context(self) -> ProjectContext | None:
        """Refresh context by rescanning the directory."""
        if self._context:
            return self.load_context(self._context.directory)
        return None

    def clear_context(self):
        """Clear current context."""
        self._context = None
