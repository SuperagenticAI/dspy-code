"""DSPy version detection and validation."""

import importlib.metadata

from packaging import version
from rich.console import Console
from rich.panel import Panel

# Minimum recommended DSPy version
MIN_RECOMMENDED_VERSION = "2.5.0"
LATEST_KNOWN_VERSION = "3.0.4"


def get_dspy_version() -> str | None:
    """Get the currently installed DSPy version.

    Returns:
        Version string or None if DSPy is not installed
    """
    try:
        return importlib.metadata.version("dspy")
    except importlib.metadata.PackageNotFoundError:
        return None


def parse_version(version_string: str) -> version.Version | None:
    """Parse a version string safely.

    Args:
        version_string: Version string to parse

    Returns:
        Parsed version or None if invalid
    """
    try:
        return version.parse(version_string)
    except version.InvalidVersion:
        return None


def check_version_compatibility() -> tuple[str | None, bool, str]:
    """Check DSPy version compatibility.

    Returns:
        Tuple of (version_string, is_compatible, warning_message)
    """
    dspy_version = get_dspy_version()

    if dspy_version is None:
        return (None, False, "DSPy is not installed! Install it with: pip install dspy")

    current = parse_version(dspy_version)
    min_recommended = parse_version(MIN_RECOMMENDED_VERSION)

    if current is None:
        return (dspy_version, False, f"Could not parse DSPy version: {dspy_version}")

    if min_recommended and current < min_recommended:
        return (
            dspy_version,
            True,  # Still compatible, but old
            f"You're using DSPy {dspy_version}. Consider upgrading to {LATEST_KNOWN_VERSION} for latest features.",
        )

    return (dspy_version, True, "")


def display_version_info(console: Console, show_warning: bool = True) -> None:
    """Display DSPy version information in the console.

    Args:
        console: Rich console instance
        show_warning: Whether to show warning if version is old
    """
    dspy_version, is_compatible, warning = check_version_compatibility()

    if dspy_version is None:
        console.print(
            Panel(
                "[bold red]⚠️  DSPy Not Installed![/bold red]\n\n"
                "DSPy Code requires DSPy to be installed.\n"
                "Install it with: [cyan]pip install dspy[/cyan]",
                border_style="red",
            )
        )
        return

    # Display version info
    version_text = f"[bold green]✓[/bold green] DSPy Version: [cyan]{dspy_version}[/cyan]"

    if warning and show_warning:
        min_rec = parse_version(MIN_RECOMMENDED_VERSION)
        current = parse_version(dspy_version)

        if min_rec and current and current < min_rec:
            console.print(
                Panel(
                    f"{version_text}\n\n"
                    f"[yellow]⚠️  {warning}[/yellow]\n\n"
                    f"Upgrade with: [cyan]pip install --upgrade dspy[/cyan]",
                    border_style="yellow",
                    title="Version Info",
                )
            )
        else:
            console.print(f"{version_text}")
    else:
        console.print(f"{version_text}")


def get_version_banner() -> str:
    """Get a version banner string for display.

    Returns:
        Formatted version string
    """
    dspy_version, _, _ = check_version_compatibility()

    if dspy_version:
        return f"DSPy {dspy_version}"
    return "DSPy (not installed)"
