"""
Security validator for DSPy code.

Checks for potentially dangerous patterns like eval(), exec(), and other
security-sensitive operations.
"""

import re
from dataclasses import dataclass

from .models import IssueCategory, IssueSeverity, ValidationIssue


@dataclass
class SecurityPattern:
    """A security pattern to check for."""

    pattern: str
    message: str
    suggestion: str
    severity: IssueSeverity = IssueSeverity.WARNING


class SecurityValidator:
    """
    Validator for security-sensitive code patterns.

    This validator checks for potentially dangerous operations like eval(),
    exec(), and other patterns that could pose security risks.
    """

    # Patterns to check for security issues
    DANGEROUS_PATTERNS = [
        SecurityPattern(
            pattern=r"\beval\s*\(",
            message="eval() is a security risk - it can execute arbitrary code",
            suggestion="Use ast.literal_eval() for safe evaluation of literals, or avoid dynamic code execution",
        ),
        SecurityPattern(
            pattern=r"\bexec\s*\(",
            message="exec() is a security risk - it can execute arbitrary code",
            suggestion="Avoid dynamic code execution; use safer alternatives like predefined functions",
        ),
        SecurityPattern(
            pattern=r"\b__import__\s*\(",
            message="__import__() can be used to import arbitrary modules",
            suggestion="Use explicit imports instead of dynamic importing",
        ),
        SecurityPattern(
            pattern=r"\bcompile\s*\(",
            message="compile() can be used to create executable code objects",
            suggestion="Avoid dynamic code compilation; use predefined code paths",
            severity=IssueSeverity.INFO,
        ),
        SecurityPattern(
            pattern=r"\bos\.system\s*\(",
            message="os.system() can execute arbitrary shell commands",
            suggestion="Use subprocess with explicit arguments instead of shell=True",
        ),
        SecurityPattern(
            pattern=r"\bsubprocess\..*shell\s*=\s*True",
            message="subprocess with shell=True can be vulnerable to shell injection",
            suggestion="Use subprocess with shell=False and pass arguments as a list",
        ),
        SecurityPattern(
            pattern=r"\bpickle\.loads?\s*\(",
            message="pickle can execute arbitrary code during deserialization",
            suggestion="Use safer serialization formats like JSON for untrusted data",
            severity=IssueSeverity.INFO,
        ),
    ]

    def __init__(self) -> None:
        """Initialize the security validator."""
        self._compiled_patterns: list[tuple[re.Pattern[str], SecurityPattern]] = [
            (re.compile(p.pattern), p) for p in self.DANGEROUS_PATTERNS
        ]

    def validate(self, code: str) -> list[ValidationIssue]:
        """
        Check code for security issues.

        Args:
            code: Python code to validate

        Returns:
            List of ValidationIssue for any security concerns found
        """
        issues = []
        lines = code.split("\n")

        for compiled_pattern, pattern_info in self._compiled_patterns:
            for match in compiled_pattern.finditer(code):
                # Calculate line number
                line_num = code[:match.start()].count("\n") + 1

                # Get the actual line content for context
                line_content = lines[line_num - 1] if line_num <= len(lines) else ""

                # Skip if it's in a comment
                stripped_line = line_content.lstrip()
                if stripped_line.startswith("#"):
                    continue

                # Skip if it's in a string (basic check)
                before_match = code[:match.start()]
                if self._is_in_string(before_match):
                    continue

                issues.append(
                    ValidationIssue(
                        severity=pattern_info.severity,
                        category=IssueCategory.ANTI_PATTERN,
                        line=line_num,
                        message=pattern_info.message,
                        suggestion=pattern_info.suggestion,
                    )
                )

        return issues

    def _is_in_string(self, text: str) -> bool:
        """
        Basic check if position is inside a string literal.

        This is a simplified check that counts quotes.
        """
        # Count unescaped quotes
        single_quotes = len(re.findall(r"(?<!\\)'", text))
        double_quotes = len(re.findall(r'(?<!\\)"', text))
        triple_single = len(re.findall(r"'''", text))
        triple_double = len(re.findall(r'"""', text))

        # Adjust for triple quotes
        single_quotes -= triple_single * 3
        double_quotes -= triple_double * 3

        # If odd number of quotes, we're inside a string
        return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)

    def has_eval(self, code: str) -> bool:
        """Check if code contains eval() calls."""
        pattern = re.compile(r"\beval\s*\(")
        return bool(pattern.search(code))

    def has_exec(self, code: str) -> bool:
        """Check if code contains exec() calls."""
        pattern = re.compile(r"\bexec\s*\(")
        return bool(pattern.search(code))
