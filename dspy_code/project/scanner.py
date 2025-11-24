"""
Project Scanner

Scans directories to detect DSPy projects and their components.
"""

import ast
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ProjectType(Enum):
    """Type of project detected."""

    EMPTY = "empty"
    EXISTING_DSPY = "existing_dspy"
    PYTHON_PROJECT = "python_project"
    OTHER = "other"


@dataclass
class ComponentInfo:
    """Information about a DSPy component."""

    name: str
    file_path: str
    line_number: int
    component_type: str  # 'signature', 'module', 'predictor'


@dataclass
class ProjectState:
    """State of the scanned project."""

    project_type: ProjectType
    directory: str
    python_files: list[str]
    dspy_files: list[str]
    has_config: bool
    config_path: str | None
    has_dspy_md: bool
    components: dict[str, list[ComponentInfo]]
    lm_providers: list[str]
    total_files: int


class ProjectScanner:
    """Scans directories to understand project structure."""

    def __init__(self):
        """Initialize the project scanner."""
        self.dspy_imports = ["dspy", "from dspy"]
        self.component_bases = {
            "Signature": "signature",
            "Module": "module",
        }
        self.predictor_types = ["Predict", "ChainOfThought", "ReAct", "ProgramOfThought"]

    def scan_directory(self, path: str = ".") -> ProjectState:
        """
        Scan directory and return project state.

        Args:
            path: Directory path to scan

        Returns:
            ProjectState with scan results
        """
        path = Path(path).resolve()

        # Get all files
        all_files = self._get_all_files(path)
        python_files = [f for f in all_files if f.endswith(".py")]

        # Check for config files
        has_config = os.path.exists(path / "dspy_config.yaml")
        config_path = str(path / "dspy_config.yaml") if has_config else None

        # Check for DSPy.md
        has_dspy_md = os.path.exists(path / "DSPy.md")

        # Detect DSPy files
        dspy_files = self._detect_dspy_files(path, python_files)

        # Determine project type
        project_type = self._determine_project_type(
            len(all_files), len(python_files), len(dspy_files), has_config
        )

        # Scan for components if DSPy project
        components = {}
        lm_providers = []
        if dspy_files:
            components = self._detect_components(path, dspy_files)
            lm_providers = self._detect_lm_providers(path, dspy_files)

        return ProjectState(
            project_type=project_type,
            directory=str(path),
            python_files=python_files,
            dspy_files=dspy_files,
            has_config=has_config,
            config_path=config_path,
            has_dspy_md=has_dspy_md,
            components=components,
            lm_providers=lm_providers,
            total_files=len(all_files),
        )

    def _get_all_files(self, path: Path) -> list[str]:
        """Get all files in directory (excluding hidden and common ignore patterns)."""
        files = []
        ignore_patterns = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            ".venv",
            "venv",
            "env",
            ".env",
            ".DS_Store",
            "*.pyc",
        }

        try:
            for item in path.rglob("*"):
                if item.is_file():
                    # Skip ignored patterns
                    if any(pattern in str(item) for pattern in ignore_patterns):
                        continue
                    files.append(str(item.relative_to(path)))
        except PermissionError:
            pass

        return files

    def _detect_dspy_files(self, path: Path, python_files: list[str]) -> list[str]:
        """Detect Python files that import DSPy."""
        dspy_files = []

        for py_file in python_files:
            file_path = path / py_file
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                    if any(imp in content for imp in self.dspy_imports):
                        dspy_files.append(py_file)
            except (UnicodeDecodeError, PermissionError):
                continue

        return dspy_files

    def _determine_project_type(
        self, total_files: int, python_files: int, dspy_files: int, has_config: bool
    ) -> ProjectType:
        """Determine the type of project."""
        if total_files == 0:
            return ProjectType.EMPTY

        if dspy_files > 0 or has_config:
            return ProjectType.EXISTING_DSPY

        if python_files > 0:
            return ProjectType.PYTHON_PROJECT

        return ProjectType.OTHER

    def _detect_components(
        self, path: Path, dspy_files: list[str]
    ) -> dict[str, list[ComponentInfo]]:
        """Detect DSPy components (signatures, modules, predictors)."""
        components = {
            "signatures": [],
            "modules": [],
            "predictors": [],
        }

        for py_file in dspy_files:
            file_path = path / py_file
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                # Find class definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Check for Signature
                        if self._inherits_from(node, "Signature"):
                            components["signatures"].append(
                                ComponentInfo(
                                    name=node.name,
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    component_type="signature",
                                )
                            )

                        # Check for Module
                        if self._inherits_from(node, "Module"):
                            components["modules"].append(
                                ComponentInfo(
                                    name=node.name,
                                    file_path=py_file,
                                    line_number=node.lineno,
                                    component_type="module",
                                )
                            )

                    # Check for predictor usage
                    if isinstance(node, ast.Call):
                        if self._is_predictor_call(node):
                            predictor_type = self._get_predictor_type(node)
                            if predictor_type:
                                components["predictors"].append(
                                    ComponentInfo(
                                        name=predictor_type,
                                        file_path=py_file,
                                        line_number=node.lineno,
                                        component_type="predictor",
                                    )
                                )

            except (SyntaxError, UnicodeDecodeError, PermissionError):
                continue

        return components

    def _inherits_from(self, node: ast.ClassDef, base_name: str) -> bool:
        """Check if a class inherits from a specific base."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == base_name:
                return True
            if isinstance(base, ast.Attribute) and base.attr == base_name:
                return True
        return False

    def _is_predictor_call(self, node: ast.Call) -> bool:
        """Check if a call is a predictor instantiation."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr in self.predictor_types
        if isinstance(node.func, ast.Name):
            return node.func.id in self.predictor_types
        return False

    def _get_predictor_type(self, node: ast.Call) -> str | None:
        """Get the predictor type from a call node."""
        if isinstance(node.func, ast.Attribute):
            return node.func.attr
        if isinstance(node.func, ast.Name):
            return node.func.id
        return None

    def _detect_lm_providers(self, path: Path, dspy_files: list[str]) -> list[str]:
        """Detect which LM providers are being used."""
        providers = set()
        provider_patterns = {
            "openai": ["openai/", "gpt-", "OpenAI"],
            "anthropic": ["anthropic/", "claude-", "Anthropic"],
            "ollama": ["ollama/", "Ollama"],
            "cohere": ["cohere/", "Cohere"],
        }

        for py_file in dspy_files:
            file_path = path / py_file
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()

                for provider, patterns in provider_patterns.items():
                    if any(pattern in content for pattern in patterns):
                        providers.add(provider)

            except (UnicodeDecodeError, PermissionError):
                continue

        return list(providers)

    def get_summary(self, state: ProjectState) -> str:
        """Get a human-readable summary of the project state."""
        lines = []

        lines.append(f"📁 Directory: {state.directory}")
        lines.append(f"📊 Project Type: {state.project_type.value}")
        lines.append("")

        if state.project_type == ProjectType.EMPTY:
            lines.append("Empty directory - ready for new project")
        elif state.project_type == ProjectType.EXISTING_DSPY:
            lines.append("Existing DSPy project detected!")
            lines.append("")
            lines.append("Found:")
            if state.has_config:
                lines.append(f"  ✓ Configuration: {state.config_path}")
            if state.has_dspy_md:
                lines.append("  ✓ DSPy.md context file")
            lines.append(f"  ✓ {len(state.dspy_files)} DSPy files")
            lines.append(f"  ✓ {len(state.components.get('signatures', []))} signatures")
            lines.append(f"  ✓ {len(state.components.get('modules', []))} modules")
            lines.append(f"  ✓ {len(state.components.get('predictors', []))} predictors")
            if state.lm_providers:
                lines.append(f"  ✓ LM Providers: {', '.join(state.lm_providers)}")
        elif state.project_type == ProjectType.PYTHON_PROJECT:
            lines.append("Python project detected (no DSPy yet)")
            lines.append(f"  • {len(state.python_files)} Python files")
        else:
            lines.append("Directory contains files but no Python/DSPy detected")

        return "\n".join(lines)
