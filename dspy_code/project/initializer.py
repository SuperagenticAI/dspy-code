"""
Smart Initializer

Intelligently initializes DSPy projects based on current state.
"""

import os
from dataclasses import dataclass
from pathlib import Path

import yaml

from .dspy_md_generator import DSPyMdGenerator
from .scanner import ProjectState, ProjectType


@dataclass
class InitResult:
    """Result of initialization."""

    success: bool
    files_created: list[str]
    files_updated: list[str]
    message: str
    project_name: str


class SmartInitializer:
    """Intelligently initializes DSPy projects."""

    def __init__(self):
        """Initialize the smart initializer."""
        self.md_generator = DSPyMdGenerator()

    def initialize(
        self,
        state: ProjectState,
        template: str | None = None,
        project_name: str | None = None,
    ) -> InitResult:
        """
        Initialize project based on state.

        Args:
            state: Current project state from scanner
            template: Optional template name for new projects
            project_name: Optional project name

        Returns:
            InitResult with initialization details
        """
        if project_name is None:
            project_name = os.path.basename(state.directory)

        files_created = []
        files_updated = []

        try:
            # Handle based on project type
            if state.project_type == ProjectType.EMPTY:
                result = self._initialize_empty(state, template, project_name)
            elif state.project_type == ProjectType.EXISTING_DSPY:
                result = self._initialize_existing(state, project_name)
            elif state.project_type == ProjectType.PYTHON_PROJECT:
                result = self._initialize_python_project(state, project_name)
            else:
                result = self._initialize_other(state, project_name)

            return result

        except Exception as e:
            return InitResult(
                success=False,
                files_created=[],
                files_updated=[],
                message=f"Initialization failed: {e!s}",
                project_name=project_name,
            )

    def _initialize_empty(
        self, state: ProjectState, template: str | None, project_name: str
    ) -> InitResult:
        """Initialize an empty directory."""
        files_created = []

        # Create DSPy.md
        if template:
            dspy_md_content = self.md_generator.generate_from_template(template, project_name)
        else:
            dspy_md_content = self.md_generator.generate_from_template("custom", project_name)

        dspy_md_path = Path(state.directory) / "DSPy.md"
        dspy_md_path.write_text(dspy_md_content)
        files_created.append("DSPy.md")

        # Create dspy_config.yaml
        config_content = self._generate_default_config()
        config_path = Path(state.directory) / "dspy_config.yaml"
        config_path.write_text(config_content)
        files_created.append("dspy_config.yaml")

        # Create basic project structure
        if template and template != "custom":
            starter_files = self._create_starter_files(state.directory, template)
            files_created.extend(starter_files)

        return InitResult(
            success=True,
            files_created=files_created,
            files_updated=[],
            message=f"Initialized new {template or 'custom'} DSPy project",
            project_name=project_name,
        )

    def _initialize_existing(self, state: ProjectState, project_name: str) -> InitResult:
        """Initialize an existing DSPy project."""
        files_created = []
        files_updated = []

        # Create DSPy.md if it doesn't exist
        if not state.has_dspy_md:
            dspy_md_content = self.md_generator.generate_from_existing(state, project_name)
            dspy_md_path = Path(state.directory) / "DSPy.md"
            dspy_md_path.write_text(dspy_md_content)
            files_created.append("DSPy.md")

        # Create config if it doesn't exist
        if not state.has_config:
            config_content = self._generate_default_config()
            config_path = Path(state.directory) / "dspy_config.yaml"
            config_path.write_text(config_content)
            files_created.append("dspy_config.yaml")

        message = "Initialized context for existing DSPy project"
        if files_created:
            message += f" (created {len(files_created)} file(s))"

        return InitResult(
            success=True,
            files_created=files_created,
            files_updated=files_updated,
            message=message,
            project_name=project_name,
        )

    def _initialize_python_project(self, state: ProjectState, project_name: str) -> InitResult:
        """Initialize a Python project (add DSPy support)."""
        files_created = []

        # Create DSPy.md
        dspy_md_content = self.md_generator.generate_from_template("custom", project_name)
        dspy_md_path = Path(state.directory) / "DSPy.md"
        dspy_md_path.write_text(dspy_md_content)
        files_created.append("DSPy.md")

        # Create dspy_config.yaml
        config_content = self._generate_default_config()
        config_path = Path(state.directory) / "dspy_config.yaml"
        config_path.write_text(config_content)
        files_created.append("dspy_config.yaml")

        return InitResult(
            success=True,
            files_created=files_created,
            files_updated=[],
            message="Added DSPy support to Python project",
            project_name=project_name,
        )

    def _initialize_other(self, state: ProjectState, project_name: str) -> InitResult:
        """Initialize other directory types."""
        # Same as empty for now
        return self._initialize_empty(state, "custom", project_name)

    def _generate_default_config(self) -> str:
        """Generate default dspy_config.yaml content."""
        config = {
            "model": {
                "provider": "openai",
                "model_name": "gpt-4o-mini",
                "api_key": "${OPENAI_API_KEY}",
            },
            "optimization": {
                "optimizer": "GEPA",
                "metric": "accuracy",
            },
            "logging": {
                "level": "INFO",
            },
        }

        return yaml.dump(config, default_flow_style=False, sort_keys=False)

    def _create_starter_files(self, directory: str, template: str) -> list[str]:
        """Create starter files based on template."""
        files_created = []
        base_path = Path(directory)

        if template == "classification":
            # Create signatures directory
            sig_dir = base_path / "signatures"
            sig_dir.mkdir(exist_ok=True)

            # Create starter signature
            sig_file = sig_dir / "classifier.py"
            sig_file.write_text("""import dspy


class ClassifySignature(dspy.Signature):
    \"\"\"Classify text into categories.\"\"\"

    text: str = dspy.InputField(desc="Text to classify")
    category: str = dspy.OutputField(desc="Category label")
""")
            files_created.append("signatures/classifier.py")

        elif template == "rag":
            # Create signatures directory
            sig_dir = base_path / "signatures"
            sig_dir.mkdir(exist_ok=True)

            # Create RAG signature
            sig_file = sig_dir / "rag.py"
            sig_file.write_text("""import dspy


class RAGSignature(dspy.Signature):
    \"\"\"Answer questions using retrieved context.\"\"\"

    question: str = dspy.InputField(desc="Question to answer")
    context: str = dspy.InputField(desc="Retrieved context")
    answer: str = dspy.OutputField(desc="Answer to the question")
""")
            files_created.append("signatures/rag.py")

        elif template == "agent":
            # Create signatures directory
            sig_dir = base_path / "signatures"
            sig_dir.mkdir(exist_ok=True)

            # Create agent signature
            sig_file = sig_dir / "agent.py"
            sig_file.write_text("""import dspy


class AgentSignature(dspy.Signature):
    \"\"\"Agent reasoning and action.\"\"\"

    task: str = dspy.InputField(desc="Task to accomplish")
    observation: str = dspy.InputField(desc="Current observation")
    thought: str = dspy.OutputField(desc="Reasoning about next action")
    action: str = dspy.OutputField(desc="Action to take")
""")
            files_created.append("signatures/agent.py")

        return files_created

    def create_or_update_config(self, existing_config: dict | None = None) -> dict:
        """
        Create or update dspy_config.yaml.

        Args:
            existing_config: Existing configuration if any

        Returns:
            Configuration dictionary
        """
        if existing_config:
            # Preserve existing config, just ensure required fields
            config = existing_config.copy()
        else:
            # Create new config
            config = {
                "model": {
                    "provider": "openai",
                    "model_name": "gpt-4o-mini",
                    "api_key": "${OPENAI_API_KEY}",
                },
                "optimization": {
                    "optimizer": "GEPA",
                    "metric": "accuracy",
                },
                "logging": {
                    "level": "INFO",
                },
            }

        return config
