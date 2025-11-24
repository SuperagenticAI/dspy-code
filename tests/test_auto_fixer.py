"""
Tests for DSPy Auto-Fixer
"""

import pytest

from dspy_code.validation.auto_fixer import AutoFixer, CodeFix
from dspy_code.validation.models import IssueCategory, IssueSeverity, ValidationIssue


@pytest.fixture
def fixer():
    """Create an auto-fixer instance."""
    return AutoFixer()


class TestAutoFixerInitialization:
    """Test auto-fixer initialization."""

    def test_fixer_initialization(self, fixer):
        """Should initialize with safe fix strategies."""
        assert fixer.safe_fixes is not None
        assert len(fixer.safe_fixes) > 0


class TestCanFix:
    """Test fix capability detection."""

    def test_can_fix_missing_description(self, fixer):
        """Should be able to fix missing descriptions."""
        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.BEST_PRACTICE,
            line=1,
            message="Missing description on field",
            suggestion="Add description",
        )

        assert fixer.can_fix(issue)

    def test_can_fix_missing_type_hint(self, fixer):
        """Should be able to fix missing type hints."""
        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            category=IssueCategory.BEST_PRACTICE,
            line=1,
            message="Missing type hint",
            suggestion="Add type hint",
        )

        assert fixer.can_fix(issue)

    def test_cannot_fix_errors(self, fixer):
        """Should not auto-fix ERROR level issues for safety."""
        issue = ValidationIssue(
            severity=IssueSeverity.ERROR,
            category=IssueCategory.SIGNATURE,
            line=1,
            message="Missing description",
            suggestion="Add description",
        )

        assert not fixer.can_fix(issue)

    def test_cannot_fix_unknown_issues(self, fixer):
        """Should not fix unknown issue types."""
        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.MODULE,
            line=1,
            message="Some complex issue",
            suggestion="Manual fix required",
        )

        assert not fixer.can_fix(issue)


class TestFixMissingDescriptions:
    """Test fixing missing field descriptions."""

    def test_fixes_input_field_without_desc(self, fixer):
        """Should add description to InputField."""
        code = """class MySignature(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()"""

        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.BEST_PRACTICE,
            line=2,
            message="Missing description on field",
            suggestion="Add description",
        )

        fixes = fixer.generate_fixes(code, [issue])

        assert len(fixes) > 0
        assert 'desc="' in fixes[0].fixed
        assert "question" in fixes[0].description.lower()

    def test_fixes_output_field_without_desc(self, fixer):
        """Should add description to OutputField."""
        code = """class MySignature(dspy.Signature):
    question: str = dspy.InputField(desc="Question")
    answer: str = dspy.OutputField()"""

        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.BEST_PRACTICE,
            line=3,
            message="Missing description on field",
            suggestion="Add description",
        )

        fixes = fixer.generate_fixes(code, [issue])

        assert len(fixes) > 0
        assert 'desc="' in fixes[0].fixed
        assert "answer" in fixes[0].description.lower()

    def test_preserves_existing_descriptions(self, fixer):
        """Should not modify fields that already have descriptions."""
        code = """class MySignature(dspy.Signature):
    question: str = dspy.InputField(desc="The question")"""

        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.BEST_PRACTICE,
            line=2,
            message="Some other issue",
            suggestion="Fix",
        )

        fixes = fixer.generate_fixes(code, [issue])

        # Should not generate a fix for this
        assert len(fixes) == 0


class TestFixMissingTypeHints:
    """Test fixing missing type hints."""

    def test_adds_type_hint_to_field(self, fixer):
        """Should add type hint to field without one."""
        code = """class MySignature(dspy.Signature):
    question = dspy.InputField(desc="Question")"""

        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            category=IssueCategory.BEST_PRACTICE,
            line=2,
            message="Missing type hint",
            suggestion="Add type hint",
        )

        fixes = fixer.generate_fixes(code, [issue])

        assert len(fixes) > 0
        assert ": str" in fixes[0].fixed
        assert "type hint" in fixes[0].description.lower()


class TestFixMissingImports:
    """Test fixing missing imports."""

    def test_adds_dspy_import(self, fixer):
        """Should add missing dspy import."""
        code = """class MySignature(Signature):
    question: str = InputField()"""

        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.BEST_PRACTICE,
            line=1,
            message="Missing dspy import",
            suggestion="Add import dspy",
        )

        fixes = fixer.generate_fixes(code, [issue])

        assert len(fixes) > 0
        assert "import dspy" in fixes[0].fixed


class TestApplyFixes:
    """Test applying fixes to code."""

    def test_applies_single_fix(self, fixer):
        """Should apply a single fix to code."""
        code = """class MySignature(dspy.Signature):
    question: str = dspy.InputField()"""

        fix = CodeFix(
            line=2,
            original="    question: str = dspy.InputField()",
            fixed='    question: str = dspy.InputField(desc="Description of question")',
            description="Added description",
            issue=ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=2,
                message="Missing description",
                suggestion="Add description",
            ),
        )

        fixed_code = fixer.apply_fixes(code, [fix])

        assert 'desc="Description of question"' in fixed_code
        assert "InputField()" not in fixed_code

    def test_applies_multiple_fixes(self, fixer):
        """Should apply multiple fixes to code."""
        code = """class MySignature(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()"""

        fixes = [
            CodeFix(
                line=2,
                original="    question: str = dspy.InputField()",
                fixed='    question: str = dspy.InputField(desc="Description of question")',
                description="Added description to question",
                issue=ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=2,
                    message="Missing description",
                    suggestion="Add description",
                ),
            ),
            CodeFix(
                line=3,
                original="    answer: str = dspy.OutputField()",
                fixed='    answer: str = dspy.OutputField(desc="Description of answer")',
                description="Added description to answer",
                issue=ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=3,
                    message="Missing description",
                    suggestion="Add description",
                ),
            ),
        ]

        fixed_code = fixer.apply_fixes(code, fixes)

        assert 'desc="Description of question"' in fixed_code
        assert 'desc="Description of answer"' in fixed_code

    def test_handles_out_of_range_line_numbers(self, fixer):
        """Should handle fixes with invalid line numbers gracefully."""
        code = "line 1\nline 2"

        fix = CodeFix(
            line=100,  # Out of range
            original="line 100",
            fixed="fixed line 100",
            description="Fix",
            issue=ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=100,
                message="Issue",
                suggestion="Fix",
            ),
        )

        # Should not crash
        fixed_code = fixer.apply_fixes(code, [fix])
        assert fixed_code == code  # Unchanged


class TestPreviewFixes:
    """Test fix preview generation."""

    def test_generates_preview(self, fixer):
        """Should generate a preview of fixes."""
        fix = CodeFix(
            line=2,
            original="    question: str = dspy.InputField()",
            fixed='    question: str = dspy.InputField(desc="Description of question")',
            description="Added description",
            issue=ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=2,
                message="Missing description",
                suggestion="Add description",
            ),
        )

        preview = fixer.preview_fixes("", [fix])

        assert "PREVIEW" in preview
        assert "Line 2" in preview
        assert "Added description" in preview
        assert "Total fixes: 1" in preview

    def test_preview_shows_before_after(self, fixer):
        """Should show before and after in preview."""
        fix = CodeFix(
            line=2,
            original="original line",
            fixed="fixed line",
            description="Fix description",
            issue=ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=2,
                message="Issue",
                suggestion="Fix",
            ),
        )

        preview = fixer.preview_fixes("", [fix])

        assert "original line" in preview
        assert "fixed line" in preview
        assert "-" in preview  # Shows removal
        assert "+" in preview  # Shows addition


class TestFixSummary:
    """Test fix summary generation."""

    def test_generates_summary(self, fixer):
        """Should generate summary of fixes."""
        fixes = [
            CodeFix(
                line=1,
                original="",
                fixed="",
                description="Fix 1",
                issue=ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=1,
                    message="Issue 1",
                    suggestion="Fix 1",
                ),
            ),
            CodeFix(
                line=2,
                original="",
                fixed="",
                description="Fix 2",
                issue=ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.SIGNATURE,
                    line=2,
                    message="Issue 2",
                    suggestion="Fix 2",
                ),
            ),
        ]

        summary = fixer.get_fix_summary(fixes)

        assert summary["total_fixes"] == 2
        assert "by_type" in summary
        assert "by_severity" in summary

    def test_summary_counts_by_type(self, fixer):
        """Should count fixes by type."""
        fixes = [
            CodeFix(
                line=1,
                original="",
                fixed="",
                description="Fix",
                issue=ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=1,
                    message="Issue",
                    suggestion="Fix",
                ),
            ),
            CodeFix(
                line=2,
                original="",
                fixed="",
                description="Fix",
                issue=ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=2,
                    message="Issue",
                    suggestion="Fix",
                ),
            ),
        ]

        summary = fixer.get_fix_summary(fixes)

        assert len(summary["by_type"]) > 0

    def test_summary_counts_by_severity(self, fixer):
        """Should count fixes by severity."""
        fixes = [
            CodeFix(
                line=1,
                original="",
                fixed="",
                description="Fix",
                issue=ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.BEST_PRACTICE,
                    line=1,
                    message="Issue",
                    suggestion="Fix",
                ),
            ),
            CodeFix(
                line=2,
                original="",
                fixed="",
                description="Fix",
                issue=ValidationIssue(
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.BEST_PRACTICE,
                    line=2,
                    message="Issue",
                    suggestion="Fix",
                ),
            ),
        ]

        summary = fixer.get_fix_summary(fixes)

        assert len(summary["by_severity"]) > 0


class TestIntegration:
    """Integration tests for auto-fixer."""

    def test_end_to_end_fix_workflow(self, fixer):
        """Should handle complete fix workflow."""
        code = """class MySignature(dspy.Signature):
    question: str = dspy.InputField()
    answer: str = dspy.OutputField()"""

        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=2,
                message="Missing description on field",
                suggestion="Add description",
            ),
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.BEST_PRACTICE,
                line=3,
                message="Missing description on field",
                suggestion="Add description",
            ),
        ]

        # Generate fixes
        fixes = fixer.generate_fixes(code, issues)
        assert len(fixes) == 2

        # Preview fixes
        preview = fixer.preview_fixes(code, fixes)
        assert "PREVIEW" in preview

        # Get summary
        summary = fixer.get_fix_summary(fixes)
        assert summary["total_fixes"] == 2

        # Apply fixes
        fixed_code = fixer.apply_fixes(code, fixes)
        assert 'desc="' in fixed_code
        assert fixed_code.count('desc="') == 2
