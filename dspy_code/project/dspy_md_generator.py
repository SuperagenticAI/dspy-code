"""
DSPy.md Generator

Generates DSPy.md context files for projects.
"""

from dataclasses import dataclass
from datetime import datetime

from .scanner import ComponentInfo, ProjectState


@dataclass
class ProjectInfo:
    """Information about a DSPy project."""

    name: str
    description: str
    use_case: str
    components: dict[str, list[ComponentInfo]]
    lm_provider: str | None
    lm_model: str | None
    goals: list[str]
    notes: str


class DSPyMdGenerator:
    """Generates DSPy.md context files."""

    def __init__(self):
        """Initialize the generator."""
        self.templates = self._load_templates()

    def _load_templates(self) -> dict[str, str]:
        """Load project templates."""
        return {
            "rag": {
                "use_case": "RAG (Retrieval-Augmented Generation)",
                "description": "Question answering with document retrieval",
                "goals": [
                    "Implement document retrieval system",
                    "Create question-answering module",
                    "Add optimization workflow",
                    "Deploy to production",
                ],
            },
            "classification": {
                "use_case": "Classification",
                "description": "Text classification with DSPy",
                "goals": [
                    "Define classification signature",
                    "Implement classifier module",
                    "Add evaluation metrics",
                    "Optimize with GEPA",
                ],
            },
            "agent": {
                "use_case": "Agent",
                "description": "ReAct agent with tool use",
                "goals": [
                    "Define agent signature",
                    "Implement tool interfaces",
                    "Create ReAct module",
                    "Test agent workflows",
                ],
            },
            "custom": {
                "use_case": "Custom",
                "description": "Custom DSPy application",
                "goals": [
                    "Define project requirements",
                    "Implement core functionality",
                    "Add tests and validation",
                ],
            },
        }

    def generate_from_template(self, template_name: str, project_name: str) -> str:
        """
        Generate DSPy.md from a template.

        Args:
            template_name: Name of the template (rag, classification, agent, custom)
            project_name: Name of the project

        Returns:
            DSPy.md content as string
        """
        template = self.templates.get(template_name, self.templates["custom"])

        project_info = ProjectInfo(
            name=project_name,
            description=template["description"],
            use_case=template["use_case"],
            components={"signatures": [], "modules": [], "predictors": []},
            lm_provider=None,
            lm_model=None,
            goals=template["goals"],
            notes="",
        )

        return self._generate_content(project_info)

    def generate_from_existing(self, state: ProjectState, project_name: str | None = None) -> str:
        """
        Generate DSPy.md from existing project scan.

        Args:
            state: ProjectState from scanner
            project_name: Optional project name (defaults to directory name)

        Returns:
            DSPy.md content as string
        """
        if project_name is None:
            import os

            project_name = os.path.basename(state.directory)

        # Infer use case from components
        use_case = self._infer_use_case(state)

        # Generate description
        description = self._generate_description(state)

        # Get LM info
        lm_provider = state.lm_providers[0] if state.lm_providers else None
        lm_model = None  # Could be extracted from config

        # Generate goals based on what's missing
        goals = self._generate_goals(state)

        project_info = ProjectInfo(
            name=project_name,
            description=description,
            use_case=use_case,
            components=state.components,
            lm_provider=lm_provider,
            lm_model=lm_model,
            goals=goals,
            notes="Generated from existing project",
        )

        return self._generate_content(project_info)

    def _generate_content(self, info: ProjectInfo) -> str:
        """Generate the actual DSPy.md content."""
        lines = []

        # Header
        lines.append(f"# DSPy Project: {info.name}")
        lines.append("")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d')}*")
        lines.append("")

        # Overview
        lines.append("## Overview")
        lines.append("")
        lines.append(info.description)
        lines.append("")

        # Use Case
        lines.append("## Use Case")
        lines.append("")
        lines.append(info.use_case)
        lines.append("")

        # Components
        lines.append("## Components")
        lines.append("")

        if info.components.get("signatures"):
            lines.append("### Signatures")
            lines.append("")
            for sig in info.components["signatures"]:
                lines.append(f"- `{sig.name}` ({sig.file_path}:{sig.line_number})")
            lines.append("")

        if info.components.get("modules"):
            lines.append("### Modules")
            lines.append("")
            for mod in info.components["modules"]:
                lines.append(f"- `{mod.name}` ({mod.file_path}:{mod.line_number})")
            lines.append("")

        if info.components.get("predictors"):
            lines.append("### Predictors")
            lines.append("")
            predictor_types = set(p.name for p in info.components["predictors"])
            for pred_type in predictor_types:
                lines.append(f"- {pred_type}")
            lines.append("")

        # Configuration
        lines.append("## Configuration")
        lines.append("")

        if info.lm_provider or info.lm_model:
            lines.append("### Language Model")
            lines.append("")
            if info.lm_provider:
                lines.append(f"- Provider: {info.lm_provider}")
            if info.lm_model:
                lines.append(f"- Model: {info.lm_model}")
            lines.append("")
        else:
            lines.append("### Language Model")
            lines.append("")
            lines.append("- Provider: [To be configured]")
            lines.append("- Model: [To be configured]")
            lines.append("")

        lines.append("### Optimization")
        lines.append("")
        lines.append("- Optimizer: [To be configured]")
        lines.append("- Metric: [To be defined]")
        lines.append("")

        # Project Structure
        lines.append("## Project Structure")
        lines.append("")
        lines.append("```")
        lines.append("project/")
        lines.append("├── signatures/")
        lines.append("│   └── [your signatures]")
        lines.append("├── modules/")
        lines.append("│   └── [your modules]")
        lines.append("├── tests/")
        lines.append("│   └── [your tests]")
        lines.append("├── dspy_config.yaml")
        lines.append("└── DSPy.md")
        lines.append("```")
        lines.append("")

        # Goals
        lines.append("## Goals")
        lines.append("")
        for goal in info.goals:
            lines.append(f"- [ ] {goal}")
        lines.append("")

        # Notes
        lines.append("## Notes")
        lines.append("")
        if info.notes:
            lines.append(info.notes)
        else:
            lines.append("[Add any additional context or notes about your project here]")
        lines.append("")

        # Tips
        lines.append("## Tips")
        lines.append("")
        lines.append("- Use `/validate` to check code quality")
        lines.append("- Use `/generate` to create new components")
        lines.append("- Use `/project info` to see current project status")
        lines.append("- Update this file as your project evolves")
        lines.append("")

        return "\n".join(lines)

    def _infer_use_case(self, state: ProjectState) -> str:
        """Infer use case from project components."""
        # Simple heuristics based on component names
        component_names = [
            c.name.lower() for components in state.components.values() for c in components
        ]

        if any("rag" in name or "retriev" in name for name in component_names):
            return "RAG (Retrieval-Augmented Generation)"
        elif any("classif" in name or "categor" in name for name in component_names):
            return "Classification"
        elif any("agent" in name or "react" in name for name in component_names):
            return "Agent"
        else:
            return "Custom DSPy Application"

    def _generate_description(self, state: ProjectState) -> str:
        """Generate project description from state."""
        num_sigs = len(state.components.get("signatures", []))
        num_mods = len(state.components.get("modules", []))

        if num_sigs > 0 and num_mods > 0:
            return f"A DSPy project with {num_sigs} signature(s) and {num_mods} module(s)."
        elif num_sigs > 0:
            return f"A DSPy project with {num_sigs} signature(s)."
        elif num_mods > 0:
            return f"A DSPy project with {num_mods} module(s)."
        else:
            return "A DSPy project."

    def _generate_goals(self, state: ProjectState) -> list[str]:
        """Generate goals based on what's missing in the project."""
        goals = []

        if not state.components.get("signatures"):
            goals.append("Define DSPy signatures")

        if not state.components.get("modules"):
            goals.append("Implement DSPy modules")

        if not state.has_config:
            goals.append("Configure language model")

        # Always suggest these
        goals.append("Add evaluation metrics")
        goals.append("Implement optimization workflow")
        goals.append("Add comprehensive tests")

        return goals

    def update_dspy_md(self, existing_content: str, updates: dict[str, any]) -> str:
        """
        Update existing DSPy.md with new information.

        Args:
            existing_content: Current DSPy.md content
            updates: Dictionary of updates to apply

        Returns:
            Updated DSPy.md content
        """
        # For now, just append updates as notes
        # In the future, could parse and update specific sections

        lines = existing_content.split("\n")

        # Find Notes section
        notes_idx = -1
        for i, line in enumerate(lines):
            if line.strip() == "## Notes":
                notes_idx = i
                break

        if notes_idx >= 0:
            # Add update note
            update_note = f"\n*Updated: {datetime.now().strftime('%Y-%m-%d')}*\n"
            for key, value in updates.items():
                update_note += f"- {key}: {value}\n"

            lines.insert(notes_idx + 2, update_note)

        return "\n".join(lines)
