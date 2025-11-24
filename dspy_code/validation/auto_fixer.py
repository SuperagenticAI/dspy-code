"""
DSPy Code Auto-Fixer

Automatically fixes common DSPy code issues.
"""

import re
from dataclasses import dataclass

from .models import IssueSeverity, ValidationIssue


@dataclass
class CodeFix:
    """Represents a code fix."""

    line: int
    original: str
    fixed: str
    description: str
    issue: ValidationIssue


class AutoFixer:
    """Automatically fixes common DSPy code issues."""

    def __init__(self):
        """Initialize the auto-fixer."""
        self.safe_fixes = [
            self._fix_missing_field_descriptions,
            self._fix_missing_type_hints,
            self._fix_missing_imports,
        ]

    def can_fix(self, issue: ValidationIssue) -> bool:
        """
        Check if an issue can be automatically fixed.

        Args:
            issue: ValidationIssue to check

        Returns:
            True if the issue can be auto-fixed
        """
        # Only auto-fix INFO and WARNING level issues for safety
        if issue.severity == IssueSeverity.ERROR:
            return False

        # Check if we have a fix strategy for this issue
        fixable_patterns = [
            "missing description",
            "description",
            "missing type hint",
            "type hint",
            "missing import",
            "import",
            "missing docstring",
            "docstring",
        ]

        return any(pattern in issue.message.lower() for pattern in fixable_patterns)

    def generate_fixes(self, code: str, issues: list[ValidationIssue]) -> list[CodeFix]:
        """
        Generate fixes for a list of issues.

        Args:
            code: Source code to fix
            issues: List of validation issues

        Returns:
            List of CodeFix objects
        """
        fixes = []
        code_lines = code.split("\n")

        for issue in issues:
            if not self.can_fix(issue):
                continue

            # Try each fix strategy
            for fix_func in self.safe_fixes:
                fix = fix_func(code_lines, issue)
                if fix:
                    fixes.append(fix)
                    break

        return fixes

    def apply_fixes(self, code: str, fixes: list[CodeFix]) -> str:
        """
        Apply fixes to code.

        Args:
            code: Original source code
            fixes: List of fixes to apply

        Returns:
            Fixed source code
        """
        code_lines = code.split("\n")

        # Sort fixes by line number (descending) to avoid line number shifts
        sorted_fixes = sorted(fixes, key=lambda f: f.line, reverse=True)

        for fix in sorted_fixes:
            if 0 <= fix.line - 1 < len(code_lines):
                code_lines[fix.line - 1] = fix.fixed

        return "\n".join(code_lines)

    def _fix_missing_field_descriptions(
        self, code_lines: list[str], issue: ValidationIssue
    ) -> CodeFix | None:
        """Fix missing field descriptions."""
        if "description" not in issue.message.lower():
            return None

        line_idx = issue.line - 1
        if line_idx < 0 or line_idx >= len(code_lines):
            return None

        line = code_lines[line_idx]

        # Check if it's an InputField or OutputField without desc
        if "InputField()" in line or "OutputField()" in line:
            # Extract field name
            match = re.search(r"(\w+)\s*:\s*\w+\s*=\s*dspy\.(Input|Output)Field\(\)", line)
            if match:
                field_name = match.group(1)
                field_type = match.group(2)

                # Generate description
                desc = f"Description of {field_name}"

                # Replace the field definition
                fixed_line = line.replace(
                    f"dspy.{field_type}Field()",
                    f'dspy.{field_type}Field(desc="{desc}")',
                )

                return CodeFix(
                    line=issue.line,
                    original=line,
                    fixed=fixed_line,
                    description=f"Added description to {field_name} field",
                    issue=issue,
                )

        return None

    def _fix_missing_type_hints(
        self, code_lines: list[str], issue: ValidationIssue
    ) -> CodeFix | None:
        """Fix missing type hints."""
        if "type hint" not in issue.message.lower():
            return None

        line_idx = issue.line - 1
        if line_idx < 0 or line_idx >= len(code_lines):
            return None

        line = code_lines[line_idx]

        # Check if it's a field without type hint
        match = re.search(r"(\w+)\s*=\s*dspy\.(Input|Output)Field\(", line)
        if match:
            field_name = match.group(1)

            # Add str type hint (most common)
            fixed_line = line.replace(f"{field_name} =", f"{field_name}: str =")

            return CodeFix(
                line=issue.line,
                original=line,
                fixed=fixed_line,
                description=f"Added type hint to {field_name} field",
                issue=issue,
            )

        return None

    def _fix_missing_imports(self, code_lines: list[str], issue: ValidationIssue) -> CodeFix | None:
        """Fix missing imports."""
        if "import" not in issue.message.lower() and "dspy" not in issue.message.lower():
            return None

        # Find the best place to add import (after existing imports or at top)
        import_line = 0
        for i, line in enumerate(code_lines):
            if line.strip().startswith("import ") or line.strip().startswith("from "):
                import_line = i + 1

        # Add dspy import if missing
        if "dspy" in issue.message.lower() or "import" in issue.message.lower():
            # Check if dspy is already imported
            has_dspy_import = any("import dspy" in line for line in code_lines)
            if not has_dspy_import:
                return CodeFix(
                    line=import_line + 1 if import_line > 0 else 1,
                    original="",
                    fixed="import dspy",
                    description="Added missing dspy import",
                    issue=issue,
                )

        return None

    def preview_fixes(self, code: str, fixes: list[CodeFix]) -> str:
        """
        Generate a preview of fixes showing before/after.

        Args:
            code: Original source code
            fixes: List of fixes to preview

        Returns:
            Formatted preview string
        """
        preview_lines = []
        preview_lines.append("=" * 70)
        preview_lines.append("PREVIEW OF AUTO-FIXES")
        preview_lines.append("=" * 70)
        preview_lines.append("")

        for i, fix in enumerate(fixes, 1):
            preview_lines.append(f"Fix {i}: {fix.description}")
            preview_lines.append(f"Line {fix.line}:")
            preview_lines.append("")
            preview_lines.append(f"  - {fix.original}")
            preview_lines.append(f"  + {fix.fixed}")
            preview_lines.append("")

        preview_lines.append("=" * 70)
        preview_lines.append(f"Total fixes: {len(fixes)}")
        preview_lines.append("=" * 70)

        return "\n".join(preview_lines)

    def get_fix_summary(self, fixes: list[CodeFix]) -> dict:
        """
        Get a summary of fixes.

        Args:
            fixes: List of fixes

        Returns:
            Dictionary with fix statistics
        """
        summary = {
            "total_fixes": len(fixes),
            "by_type": {},
            "by_severity": {},
        }

        for fix in fixes:
            # Count by issue category
            category = (
                fix.issue.category.value
                if hasattr(fix.issue.category, "value")
                else str(fix.issue.category)
            )
            summary["by_type"][category] = summary["by_type"].get(category, 0) + 1

            # Count by severity
            severity = (
                fix.issue.severity.value
                if hasattr(fix.issue.severity, "value")
                else str(fix.issue.severity)
            )
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1

        return summary
