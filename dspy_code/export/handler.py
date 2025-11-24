"""
Export and import handler for DSPy Code.

Handles various export/import formats and operations.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from ..core.exceptions import ExportError, ImportError, InvalidFormatError
from ..core.logging import get_logger

logger = get_logger(__name__)


class ExportImportHandler:
    """Handles export and import operations."""

    def __init__(self, config_manager=None):
        """
        Initialize handler.

        Args:
            config_manager: Optional configuration manager
        """
        self.config_manager = config_manager
        self.export_dir = Path.home() / ".dspy_cli" / "exports"
        self.export_dir.mkdir(parents=True, exist_ok=True)

    def export_code(self, code: str, format: str, output_path: Path) -> None:
        """
        Export code in specified format.

        Args:
            code: Code to export
            format: Export format (python, json, markdown)
            output_path: Output file path
        """
        try:
            if format == "python":
                output_path.write_text(code)
            elif format == "json":
                data = {
                    "code": code,
                    "exported_at": datetime.now().isoformat(),
                    "format": "dspy_module",
                }
                output_path.write_text(json.dumps(data, indent=2))
            elif format == "markdown":
                markdown = f"# DSPy Module\n\n```python\n{code}\n```\n"
                output_path.write_text(markdown)
            else:
                raise ValueError(f"Unsupported format: {format}")

            logger.info(f"Exported code to {output_path} ({format})")

        except Exception as e:
            raise ExportError(f"Failed to export code: {e}")

    def export_config(self, config: dict[str, Any], output_path: Path) -> None:
        """
        Export configuration template.

        Args:
            config: Configuration dictionary
            output_path: Output file path
        """
        try:
            # Export as YAML for readability
            with open(output_path, "w") as f:
                yaml.dump(config, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Exported config to {output_path}")

        except Exception as e:
            raise ExportError(f"Failed to export config: {e}")

    def export_conversation(self, history: list[dict], format: str = "markdown") -> str:
        """
        Export conversation history.

        Args:
            history: Conversation history
            format: Export format (markdown, json, text)

        Returns:
            Formatted conversation string
        """
        if format == "markdown":
            lines = ["# Conversation History\n"]
            for msg in history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                lines.append(f"## {role.title()}\n\n{content}\n")
            return "\n".join(lines)

        elif format == "json":
            return json.dumps(history, indent=2)

        elif format == "text":
            lines = []
            for msg in history:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                lines.append(f"{role.upper()}: {content}\n")
            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def import_session(self, file_path: Path) -> dict[str, Any]:
        """
        Import a saved session.

        Args:
            file_path: Path to session file

        Returns:
            Session data dictionary
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            with open(file_path) as f:
                data = json.load(f)

            # Validate session format
            required_fields = ["version", "timestamp", "conversation_history"]
            for field in required_fields:
                if field not in data:
                    raise InvalidFormatError("session", f"missing {field}")

            logger.info(f"Imported session from {file_path}")
            return data

        except json.JSONDecodeError as e:
            raise ImportError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ImportError(f"Failed to import session: {e}")

    def import_config(self, file_path: Path) -> dict[str, Any]:
        """
        Import configuration.

        Args:
            file_path: Path to config file

        Returns:
            Configuration dictionary
        """
        try:
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            # Try YAML first, then JSON
            try:
                with open(file_path) as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError:
                with open(file_path) as f:
                    data = json.load(f)

            logger.info(f"Imported config from {file_path}")
            return data

        except Exception as e:
            raise ImportError(f"Failed to import config: {e}")

    def export_session_bundle(
        self, session_data: dict[str, Any], code_files: list[str], output_dir: Path
    ) -> Path:
        """
        Export complete session bundle with code files.

        Args:
            session_data: Session data
            code_files: List of code file paths
            output_dir: Output directory

        Returns:
            Path to bundle directory
        """
        try:
            # Create bundle directory
            bundle_name = f"session_bundle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            bundle_dir = output_dir / bundle_name
            bundle_dir.mkdir(parents=True, exist_ok=True)

            # Export session data
            session_file = bundle_dir / "session.json"
            with open(session_file, "w") as f:
                json.dump(session_data, f, indent=2)

            # Copy code files
            code_dir = bundle_dir / "code"
            code_dir.mkdir(exist_ok=True)

            for code_file in code_files:
                src = Path(code_file)
                if src.exists():
                    dst = code_dir / src.name
                    dst.write_text(src.read_text())

            # Create README
            readme = bundle_dir / "README.md"
            readme.write_text(f"""# DSPy Code Session Bundle

Exported: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Contents

- `session.json` - Session data
- `code/` - Generated code files

## Import

To import this session:

```bash
dspy-cli interactive
/import session session.json
```
""")

            logger.info(f"Created session bundle at {bundle_dir}")
            return bundle_dir

        except Exception as e:
            raise ExportError(f"Failed to create session bundle: {e}")
