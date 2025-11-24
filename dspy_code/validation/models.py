"""
Data models for DSPy code validation.
"""

from dataclasses import dataclass, field
from enum import Enum


class IssueSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class IssueCategory(Enum):
    """Categories of validation issues."""

    SIGNATURE = "signature"
    MODULE = "module"
    PREDICTOR = "predictor"
    BEST_PRACTICE = "best_practice"
    ANTI_PATTERN = "anti_pattern"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in code."""

    severity: IssueSeverity
    category: IssueCategory
    line: int
    message: str
    suggestion: str
    example: str | None = None
    docs_link: str | None = None

    def __str__(self) -> str:
        """String representation of the issue."""
        severity_icon = {
            IssueSeverity.ERROR: "❌",
            IssueSeverity.WARNING: "⚠️",
            IssueSeverity.INFO: "💡",
        }
        icon = severity_icon.get(self.severity, "•")
        return f"{icon} Line {self.line}: {self.message}"


@dataclass
class QualityMetrics:
    """Quality metrics for DSPy code."""

    pattern_compliance: int  # 0-100
    documentation: int  # 0-100
    optimization_ready: int  # 0-100
    production_ready: int  # 0-100
    overall_grade: str  # A, B, C, D, F

    @property
    def overall_score(self) -> int:
        """Calculate overall score."""
        return (
            self.pattern_compliance
            + self.documentation
            + self.optimization_ready
            + self.production_ready
        ) // 4

    @classmethod
    def calculate_grade(cls, score: int) -> str:
        """Calculate letter grade from score."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


@dataclass
class ValidationReport:
    """Complete validation report for DSPy code."""

    code_file: str
    issues: list[ValidationIssue] = field(default_factory=list)
    metrics: QualityMetrics | None = None
    suggestions: list[str] = field(default_factory=list)
    learning_resources: list[str] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        """Get all error-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Get all warning-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.WARNING]

    @property
    def infos(self) -> list[ValidationIssue]:
        """Get all info-level issues."""
        return [i for i in self.issues if i.severity == IssueSeverity.INFO]

    @property
    def passed_checks(self) -> int:
        """Count of passed checks (no errors)."""
        # This will be calculated based on total checks minus issues
        return max(0, 20 - len(self.issues))  # Assume 20 total checks

    def has_errors(self) -> bool:
        """Check if report has any errors."""
        return len(self.errors) > 0

    def is_production_ready(self) -> bool:
        """Check if code is production ready."""
        return not self.has_errors() and self.metrics and self.metrics.production_ready >= 80
