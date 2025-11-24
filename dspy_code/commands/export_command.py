"""
Export command for sharing DSPy components.
"""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.prompt import Confirm

from ..core.config import ConfigManager
from ..core.directory_utils import ensure_directory
from ..core.exceptions import DSPyCLIError
from ..core.logging import get_logger

console = Console()
logger = get_logger(__name__)


def execute(
    component_path: str,
    output_path: str | None = None,
    export_format: str = "python",
    include_config: bool = False,
    verbose: bool = False,
) -> None:
    """
    Export DSPy components for sharing.

    Args:
        component_path: Path to the component to export
        output_path: Output file path
        export_format: Export format (python, json)
        include_config: Include configuration in export
        verbose: Enable verbose output
    """
    logger.info(f"Exporting DSPy component: {component_path}")

    # Check if we're in a DSPy project
    config_manager = ConfigManager()
    if not config_manager.is_project_initialized():
        console.print("[red]Error:[/red] No dspy_config.yaml found in current directory.")
        console.print("Run 'dspy-cli init' to create a configuration file.")
        return

    try:
        component_file = Path(component_path)
        if not component_file.exists():
            raise DSPyCLIError(f"Component file not found: {component_path}")

        # Determine output path
        if not output_path:
            if export_format == "json":
                output_path = f"{component_file.stem}_export.json"
            else:
                output_path = f"{component_file.stem}_export.zip"

        output_file = Path(output_path)

        # Ensure output directory exists
        ensure_directory(output_file.parent)

        # Check if output file exists
        if output_file.exists():
            if not Confirm.ask(f"Output file '{output_file}' exists. Overwrite?"):
                console.print("[yellow]Export cancelled.[/yellow]")
                return

        # Export based on format
        if export_format == "json":
            _export_as_json(component_file, output_file, config_manager, include_config, verbose)
        else:
            _export_as_package(component_file, output_file, config_manager, include_config, verbose)

        console.print("[green]✓[/green] Component exported successfully!")
        console.print(f"[blue]Export file:[/blue] {output_file}")

        # Show sharing instructions
        _show_sharing_instructions(output_file, export_format)

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise DSPyCLIError(f"Export failed: {e}")


def _export_as_json(
    component_file: Path,
    output_file: Path,
    config_manager: ConfigManager,
    include_config: bool,
    verbose: bool,
) -> None:
    """Export component as JSON metadata."""

    # Read component code
    component_code = component_file.read_text()

    # Extract metadata
    metadata = _extract_component_metadata(component_file, component_code)

    # Create export data
    export_data = {
        "export_info": {
            "format": "dspy-cli-json",
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "exported_by": "dspy-cli",
        },
        "component": {
            "name": component_file.stem,
            "file_name": component_file.name,
            "code": component_code,
            "metadata": metadata,
        },
    }

    # Include configuration if requested
    if include_config:
        export_data["config"] = {
            "project_name": config_manager.config.name,
            "dspy_version": config_manager.config.dspy_version,
            "default_model": config_manager.config.default_model,
        }

    # Look for related files
    related_files = _find_related_files(component_file)
    if related_files:
        export_data["related_files"] = {}
        for rel_file in related_files:
            try:
                export_data["related_files"][rel_file.name] = rel_file.read_text()
            except Exception as e:
                if verbose:
                    console.print(f"[yellow]Warning: Could not read {rel_file}: {e}[/yellow]")

    # Write JSON export
    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)

    if verbose:
        console.print("[blue]Exported as JSON metadata[/blue]")
        console.print(f"[blue]Component code size:[/blue] {len(component_code)} characters")
        if related_files:
            console.print(f"[blue]Related files:[/blue] {len(related_files)}")


def _export_as_package(
    component_file: Path,
    output_file: Path,
    config_manager: ConfigManager,
    include_config: bool,
    verbose: bool,
) -> None:
    """Export component as a complete package."""

    # Create temporary directory for package
    import tempfile

    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = Path(temp_dir) / "dspy_export"
        package_dir.mkdir()

        # Copy main component
        shutil.copy2(component_file, package_dir / component_file.name)

        # Copy related files
        related_files = _find_related_files(component_file)
        for rel_file in related_files:
            try:
                shutil.copy2(rel_file, package_dir / rel_file.name)
            except Exception as e:
                if verbose:
                    console.print(f"[yellow]Warning: Could not copy {rel_file}: {e}[/yellow]")

        # Create README
        _create_export_readme(package_dir, component_file, config_manager)

        # Create requirements.txt
        _create_export_requirements(package_dir)

        # Include configuration if requested
        if include_config:
            config_export = {
                "project_name": config_manager.config.name,
                "dspy_version": config_manager.config.dspy_version,
                "default_model": config_manager.config.default_model,
                "exported_at": datetime.now().isoformat(),
            }

            with open(package_dir / "dspy_config.json", "w") as f:
                json.dump(config_export, f, indent=2)

        # Create ZIP package
        with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in package_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(package_dir)
                    zipf.write(file_path, arcname)

        if verbose:
            console.print("[blue]Exported as ZIP package[/blue]")
            console.print("[blue]Package contents:[/blue]")
            for file_path in package_dir.rglob("*"):
                if file_path.is_file():
                    console.print(f"  - {file_path.name}")


def _extract_component_metadata(component_file: Path, code: str) -> dict[str, Any]:
    """Extract metadata from component code."""
    metadata = {
        "file_size": len(code),
        "line_count": len(code.split("\n")),
        "has_signature": "dspy.Signature" in code,
        "has_module": "dspy.Module" in code,
        "reasoning_patterns": [],
    }

    # Detect reasoning patterns
    if "dspy.Predict" in code:
        metadata["reasoning_patterns"].append("predict")
    if "dspy.ChainOfThought" in code:
        metadata["reasoning_patterns"].append("chain_of_thought")
    if "dspy.ReAct" in code:
        metadata["reasoning_patterns"].append("react")

    # Extract docstring
    lines = code.split("\n")
    in_docstring = False
    docstring_lines = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            if in_docstring:
                break
            else:
                in_docstring = True
                if len(stripped) > 3:
                    docstring_lines.append(stripped[3:])
        elif in_docstring:
            docstring_lines.append(line)

    if docstring_lines:
        metadata["description"] = "\n".join(docstring_lines).strip()

    return metadata


def _find_related_files(component_file: Path) -> list[Path]:
    """Find files related to the component."""
    related_files = []

    # Look for files with similar names
    base_name = component_file.stem
    parent_dir = component_file.parent

    # Common patterns
    patterns = [
        f"{base_name}_examples.jsonl",
        f"{base_name}_test.py",
        f"{base_name}_config.json",
        f"{base_name}.md",
        "examples.jsonl",
        "test_data.jsonl",
    ]

    for pattern in patterns:
        potential_file = parent_dir / pattern
        if potential_file.exists() and potential_file != component_file:
            related_files.append(potential_file)

    return related_files


def _create_export_readme(
    package_dir: Path, component_file: Path, config_manager: ConfigManager
) -> None:
    """Create README for exported package."""

    readme_content = f"""# DSPy Component Export: {component_file.stem}

This package contains a DSPy component exported from DSPy Code.

## Contents

- `{component_file.name}` - Main DSPy component
- `README.md` - This file
- `requirements.txt` - Python dependencies

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the component:
   ```bash
   python {component_file.name}
   ```

3. Or import in your code:
   ```python
   from {component_file.stem} import *
   ```

## About DSPy Code

This component was created using DSPy Code, a command-line interface for the DSPy framework.

- Learn more: https://github.com/dspy-cli/dspy-cli
- DSPy Documentation: https://dspy-docs.vercel.app/

## Export Information

- Exported from project: {config_manager.config.name}
- DSPy version: {config_manager.config.dspy_version}
- Export date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

    (package_dir / "README.md").write_text(readme_content)


def _create_export_requirements(package_dir: Path) -> None:
    """Create requirements.txt for exported package."""

    requirements = [
        "dspy>=3.0.4",
        "openai>=1.0.0",
        "anthropic>=0.25.0",
        "google-generativeai>=0.3.0",
    ]

    (package_dir / "requirements.txt").write_text("\n".join(requirements))


def _show_sharing_instructions(output_file: Path, export_format: str) -> None:
    """Show instructions for sharing the exported component."""

    console.print("\n[bold]Sharing Instructions:[/bold]")

    if export_format == "json":
        console.print("1. Share the JSON file with others")
        console.print("2. Recipients can import with:")
        console.print("   [cyan]dspy-cli import component.json[/cyan]")
    else:
        console.print("1. Share the ZIP file with others")
        console.print("2. Recipients can extract and use:")
        console.print(f"   [cyan]unzip {output_file.name}[/cyan]")
        console.print("   [cyan]cd dspy_export[/cyan]")
        console.print("   [cyan]pip install -r requirements.txt[/cyan]")

    console.print("\n[bold]What's included:[/bold]")
    console.print("- Complete component code")
    console.print("- Documentation and examples")
    console.print("- Dependency information")
    console.print("- Usage instructions")
