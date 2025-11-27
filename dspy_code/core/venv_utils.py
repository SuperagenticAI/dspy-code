"""
Utilities for detecting and working with virtual environments.
Supports both standard venv and uv-created venvs.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Tuple


def find_project_venv(project_dir: Path) -> Optional[Path]:
    """
    Find virtual environment in project directory.

    Checks for:
    - .venv/ (standard location)
    - venv/ (alternative location)

    Args:
        project_dir: Project directory to search

    Returns:
        Path to venv directory if found, None otherwise
    """
    for venv_name in [".venv", "venv"]:
        venv_path = project_dir / venv_name
        if venv_path.exists() and _is_valid_venv(venv_path):
            return venv_path
    return None


def _is_valid_venv(venv_path: Path) -> bool:
    """Check if directory is a valid virtual environment."""
    # Check for Python executable
    if os.name == "nt":  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"

    return python_exe.exists()


def get_venv_python(venv_path: Path) -> Optional[Path]:
    """
    Get Python executable path from venv.

    Args:
        venv_path: Path to virtual environment directory

    Returns:
        Path to Python executable, or None if not found
    """
    if os.name == "nt":  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"

    return python_exe if python_exe.exists() else None


def is_uv_available() -> bool:
    """Check if uv is installed and available."""
    return shutil.which("uv") is not None


def is_uv_venv(venv_path: Path) -> bool:
    """
    Detect if venv was created with uv.

    uv creates venvs with a .uv-venv marker file or specific structure.
    Check for:
    - .uv-venv marker file
    - pyvenv.cfg with uv-specific markers

    Args:
        venv_path: Path to venv directory

    Returns:
        True if venv appears to be created by uv
    """
    # Check for uv marker
    uv_marker = venv_path / ".uv-venv"
    if uv_marker.exists():
        return True

    # Check pyvenv.cfg for uv indicators
    pyvenv_cfg = venv_path / "pyvenv.cfg"
    if pyvenv_cfg.exists():
        try:
            content = pyvenv_cfg.read_text()
            # uv may add specific comments or markers
            if "uv" in content.lower():
                return True
        except Exception:
            pass

    return False


def get_project_python(project_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Get Python executable from project's venv.

    CRITICAL: This function ONLY returns Python from project venv.
    If no project venv found, returns None (caller should handle).

    Args:
        project_dir: Project directory (defaults to current working directory)

    Returns:
        Path to Python executable from project venv, or None if not found
    """
    if project_dir is None:
        project_dir = Path.cwd()

    # Try to find project venv
    venv_path = find_project_venv(project_dir)
    if venv_path:
        python_exe = get_venv_python(venv_path)
        if python_exe:
            return python_exe

    # No project venv found - return None
    # Caller should handle this (warn user, use sys.executable as fallback)
    return None


def check_project_venv(project_dir: Optional[Path] = None) -> Tuple[bool, Optional[str]]:
    """
    Check if project has a venv in the root directory.

    Args:
        project_dir: Project directory (defaults to current working directory)

    Returns:
        Tuple of (has_venv: bool, warning_message: Optional[str])
        If has_venv is False, warning_message explains the impact
    """
    if project_dir is None:
        project_dir = Path.cwd()

    venv_path = find_project_venv(project_dir)
    if venv_path:
        return True, None

    # No venv found - return warning message
    warning = (
        "⚠️  No virtual environment found in project root!\n\n"
        "dspy-code will work but with LIMITED functionality:\n\n"
        "❌ MISSING FEATURES:\n"
        "  • RAG indexing of installed packages (dspy, gepa, mcp)\n"
        "  • Real DSPy source code examples in code generation\n"
        "  • Version-specific code patterns from installed packages\n"
        "  • Optimal code generation quality\n\n"
        "✅ STILL WORKS:\n"
        "  • Basic code generation (templates only)\n"
        "  • Project code indexing\n"
        "  • All slash commands\n"
        "  • Model connections\n\n"
        "🔧 TO FIX:\n"
        "  1. Create venv in project root:\n"
        "     python -m venv .venv  OR  uv venv\n"
        "  2. Activate it:\n"
        "     source .venv/bin/activate  # (fish: source .venv/bin/activate.fish)\n"
        "  3. Install dspy-code:\n"
        "     pip install dspy-code  # (or: uv pip install dspy-code)\n\n"
        "💡 For faster responses, you can disable RAG indexing:\n"
        "   /config set codebase_rag.enabled false  OR  /disable-rag"
    )
    return False, warning
