"""
Validation Report Generator

Generates beautiful, readable validation reports.
"""

from rich.console import Console

from .models import IssueSeverity, ValidationIssue, ValidationReport
from .quality_scorer import QualityMetrics, QualityScorer


class ReportGenerator:
    """Generates formatted validation reports."""

    def __init__(self):
        """Initialize the report generator."""
        self.console = Console()
        self.scorer = QualityScorer()

    def generate_report(self, report: ValidationReport) -> None:
        """
        Generate and display a validation report.

        Args:
            report: ValidationReport to display
        """
        self.console.print()
        self.console.print("[bold cyan]🔍 DSPy Code Validation Report[/bold cyan]")
        self.console.print()
        self.console.print(f"[bold]File:[/bold] {report.code_file}")

        if report.metrics:
            self.console.print(
                f"[bold]Quality Grade:[/bold] {report.metrics.overall_grade} ({report.metrics.overall_score}/100)"
            )

        self.console.print()
        self.console.print("━" * 70)
        self.console.print()

        # Show passed checks
        passed = report.passed_checks
        self.console.print(f"[bold green]✅ PASSED CHECKS ({passed})[/bold green]")
        self.console.print()

        # Show errors
        if report.errors:
            self.console.print(f"[bold red]❌ ERRORS ({len(report.errors)})[/bold red]")
            self.console.print()
            for issue in report.errors:
                self._print_issue(issue)
            self.console.print()

        # Show warnings
        if report.warnings:
            self.console.print(f"[bold yellow]⚠️  WARNINGS ({len(report.warnings)})[/bold yellow]")
            self.console.print()
            for issue in report.warnings:
                self._print_issue(issue)
            self.console.print()

        # Show info
        if report.infos:
            self.console.print(f"[bold blue]💡 SUGGESTIONS ({len(report.infos)})[/bold blue]")
            self.console.print()
            for issue in report.infos:
                self._print_issue(issue)
            self.console.print()

        # Show quality metrics
        if report.metrics:
            self._print_metrics(report.metrics)

        # Show suggestions
        if report.suggestions:
            self.console.print("[bold cyan]📝 RECOMMENDATIONS[/bold cyan]")
            self.console.print()
            for i, suggestion in enumerate(report.suggestions, 1):
                self.console.print(f"  {i}. {suggestion}")
            self.console.print()

        # Show learning resources
        if report.learning_resources:
            self.console.print("[bold cyan]📚 LEARNING RESOURCES[/bold cyan]")
            self.console.print()
            for resource in report.learning_resources:
                self.console.print(f"  • {resource}")
            self.console.print()

        # Show next steps
        self._print_next_steps(report)

    def _print_issue(self, issue) -> None:
        """Print a single validation issue."""
        severity_colors = {
            IssueSeverity.ERROR: "red",
            IssueSeverity.WARNING: "yellow",
            IssueSeverity.INFO: "blue",
        }
        color = severity_colors.get(issue.severity, "white")

        self.console.print(f"[{color}]Line {issue.line}:[/{color}] {issue.message}")
        self.console.print(f"  [dim]→ {issue.suggestion}[/dim]")

        if issue.example:
            self.console.print("  [dim]Example:[/dim]")
            self.console.print(f"  [dim]{issue.example}[/dim]")

        if issue.docs_link:
            self.console.print(f"  [dim]Docs: {issue.docs_link}[/dim]")

        self.console.print()

    def _print_metrics(self, metrics: QualityMetrics) -> None:
        """Print quality metrics with explanations."""
        self.console.print("[bold cyan]📊 QUALITY METRICS[/bold cyan]")
        self.console.print()

        # Get explanations for scores
        explanations = self.scorer.get_score_explanation(metrics)

        # Create progress bars with explanations
        self._print_metric_bar(
            "Pattern Compliance", metrics.pattern_compliance, explanations.get("pattern_compliance")
        )
        self._print_metric_bar(
            "Documentation", metrics.documentation, explanations.get("documentation")
        )
        self._print_metric_bar(
            "Optimization Ready", metrics.optimization_ready, explanations.get("optimization_ready")
        )
        self._print_metric_bar(
            "Production Ready", metrics.production_ready, explanations.get("production_ready")
        )

        self.console.print()
        self.console.print(
            f"[bold]Overall Grade: {metrics.overall_grade}[/bold] ({metrics.overall_score}/100)"
        )
        self.console.print()

    def _print_metric_bar(self, name: str, score: int, explanation: str | None = None) -> None:
        """Print a metric with progress bar and explanation."""
        filled = "█" * (score // 5)
        empty = "░" * (20 - (score // 5))

        color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        self.console.print(f"{name:20} [{color}]{filled}{empty}[/{color}] {score}/100")

        if explanation:
            self.console.print(f"  [dim]{explanation}[/dim]")

    def _print_next_steps(self, report: ValidationReport) -> None:
        """Print next steps based on report."""
        self.console.print("[bold cyan]🎯 NEXT STEPS[/bold cyan]")
        self.console.print()

        if report.has_errors():
            self.console.print("  1. Fix all errors before proceeding")

        if report.warnings:
            self.console.print("  2. Address warnings to improve code quality")

        if report.metrics and report.metrics.overall_score < 80:
            self.console.print("  3. Improve code to reach Grade B or higher")

        if not report.has_errors():
            self.console.print("  ✓ Code is ready for use!")
            if report.is_production_ready():
                self.console.print("  ✓ Code is production-ready!")

        self.console.print()
        self.console.print("[dim]Run '/validate --help' for more options[/dim]")
        self.console.print()

    def generate_summary(self, report: ValidationReport) -> str:
        """
        Generate a text summary of the validation report.

        Args:
            report: ValidationReport to summarize

        Returns:
            String summary of the report
        """
        lines = []
        lines.append(f"Validation Report for {report.code_file}")
        lines.append("=" * 50)

        if report.metrics:
            lines.append(
                f"Overall Grade: {report.metrics.overall_grade} ({report.metrics.overall_score}/100)"
            )

        lines.append(f"Passed Checks: {report.passed_checks}")
        lines.append(f"Errors: {len(report.errors)}")
        lines.append(f"Warnings: {len(report.warnings)}")
        lines.append(f"Info: {len(report.infos)}")

        return "\n".join(lines)

    def format_issues_by_severity(self, issues: list[ValidationIssue]) -> dict:
        """
        Group issues by severity level.

        Args:
            issues: List of validation issues

        Returns:
            Dictionary with severity levels as keys and lists of issues as values
        """
        grouped = {IssueSeverity.ERROR: [], IssueSeverity.WARNING: [], IssueSeverity.INFO: []}

        for issue in issues:
            if issue.severity in grouped:
                grouped[issue.severity].append(issue)

        return grouped

    def format_issues_by_line(self, issues: list[ValidationIssue]) -> dict:
        """
        Group issues by line number.

        Args:
            issues: List of validation issues

        Returns:
            Dictionary with line numbers as keys and lists of issues as values
        """
        grouped = {}

        for issue in issues:
            if issue.line not in grouped:
                grouped[issue.line] = []
            grouped[issue.line].append(issue)

        return grouped

    def generate_compact_report(self, report: ValidationReport) -> None:
        """
        Generate a compact version of the validation report.

        Args:
            report: ValidationReport to display
        """
        self.console.print()
        self.console.print(f"[bold cyan]🔍 {report.code_file}[/bold cyan]", end=" ")

        if report.metrics:
            grade_color = (
                "green"
                if report.metrics.overall_grade in ["A", "B"]
                else "yellow"
                if report.metrics.overall_grade == "C"
                else "red"
            )
            self.console.print(
                f"[{grade_color}]Grade: {report.metrics.overall_grade}[/{grade_color}]"
            )
        else:
            self.console.print()

        if report.has_errors():
            self.console.print(f"  [red]❌ {len(report.errors)} errors[/red]")

        if report.warnings:
            self.console.print(f"  [yellow]⚠️  {len(report.warnings)} warnings[/yellow]")

        if not report.has_errors() and not report.warnings:
            self.console.print("  [green]✓ All checks passed[/green]")

        self.console.print()

    def generate_json_report(self, report: ValidationReport) -> dict:
        """
        Generate a JSON-serializable version of the report.

        Args:
            report: ValidationReport to convert

        Returns:
            Dictionary representation of the report
        """
        return {
            "file": report.code_file,
            "metrics": {
                "pattern_compliance": report.metrics.pattern_compliance,
                "documentation": report.metrics.documentation,
                "optimization_ready": report.metrics.optimization_ready,
                "production_ready": report.metrics.production_ready,
                "overall_grade": report.metrics.overall_grade,
                "overall_score": report.metrics.overall_score,
            }
            if report.metrics
            else None,
            "passed_checks": report.passed_checks,
            "errors": [self._issue_to_dict(issue) for issue in report.errors],
            "warnings": [self._issue_to_dict(issue) for issue in report.warnings],
            "info": [self._issue_to_dict(issue) for issue in report.infos],
            "suggestions": report.suggestions,
            "learning_resources": report.learning_resources,
        }

    def _issue_to_dict(self, issue: ValidationIssue) -> dict:
        """Convert a ValidationIssue to a dictionary."""
        return {
            "severity": issue.severity.value
            if hasattr(issue.severity, "value")
            else str(issue.severity),
            "category": issue.category.value
            if hasattr(issue.category, "value")
            else str(issue.category),
            "line": issue.line,
            "message": issue.message,
            "suggestion": issue.suggestion,
            "example": issue.example,
            "docs_link": issue.docs_link,
        }
