"""
Tests for DSPy Learning Integration
"""

import pytest

from dspy_code.validation.learning_integration import LearningIntegration, LearningResource
from dspy_code.validation.models import IssueCategory, IssueSeverity, ValidationIssue


@pytest.fixture
def learning():
    """Create a learning integration instance."""
    return LearningIntegration()


class TestLearningIntegration:
    """Test learning integration initialization."""

    def test_initialization(self, learning):
        """Should initialize with resources and comments."""
        assert learning.resources is not None
        assert learning.educational_comments is not None
        assert len(learning.resources) > 0
        assert len(learning.educational_comments) > 0

    def test_has_signature_resources(self, learning):
        """Should have signature learning resources."""
        assert "signatures" in learning.resources
        assert len(learning.resources["signatures"]) > 0

    def test_has_module_resources(self, learning):
        """Should have module learning resources."""
        assert "modules" in learning.resources
        assert len(learning.resources["modules"]) > 0

    def test_has_predictor_resources(self, learning):
        """Should have predictor learning resources."""
        assert "predictors" in learning.resources
        assert len(learning.resources["predictors"]) > 0


class TestEducationalComments:
    """Test educational comment generation."""

    def test_gets_signature_comment(self, learning):
        """Should get educational comment for signatures."""
        comment = learning.get_educational_comment("signature_definition")

        assert comment is not None
        assert "Signature" in comment
        assert "InputField" in comment or "OutputField" in comment

    def test_gets_module_comment(self, learning):
        """Should get educational comment for modules."""
        comment = learning.get_educational_comment("module_definition")

        assert comment is not None
        assert "Module" in comment
        assert "forward" in comment.lower()

    def test_gets_predictor_comment(self, learning):
        """Should get educational comment for predictors."""
        comment = learning.get_educational_comment("predictor_usage")

        assert comment is not None
        assert "Predictor" in comment
        assert "ChainOfThought" in comment or "Predict" in comment

    def test_returns_none_for_unknown_category(self, learning):
        """Should return None for unknown category."""
        comment = learning.get_educational_comment("unknown_category")

        assert comment is None


class TestResourcesForIssues:
    """Test getting resources for specific issues."""

    def test_gets_signature_resources(self, learning):
        """Should get signature resources for signature issues."""
        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.SIGNATURE,
            line=1,
            message="Signature issue",
            suggestion="Fix",
        )

        resources = learning.get_resources_for_issue(issue)

        assert len(resources) > 0
        assert all(r.category == "signatures" for r in resources)

    def test_gets_module_resources(self, learning):
        """Should get module resources for module issues."""
        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.MODULE,
            line=1,
            message="Module issue",
            suggestion="Fix",
        )

        resources = learning.get_resources_for_issue(issue)

        assert len(resources) > 0
        assert all(r.category == "modules" for r in resources)

    def test_gets_predictor_resources(self, learning):
        """Should get predictor resources for predictor issues."""
        issue = ValidationIssue(
            severity=IssueSeverity.WARNING,
            category=IssueCategory.PREDICTOR,
            line=1,
            message="Predictor issue",
            suggestion="Fix",
        )

        resources = learning.get_resources_for_issue(issue)

        assert len(resources) > 0
        assert all(r.category == "predictors" for r in resources)

    def test_gets_optimization_resources_for_metric_issues(self, learning):
        """Should get optimization resources for metric-related issues."""
        issue = ValidationIssue(
            severity=IssueSeverity.INFO,
            category=IssueCategory.BEST_PRACTICE,
            line=1,
            message="Missing metric function",
            suggestion="Add metric",
        )

        resources = learning.get_resources_for_issue(issue)

        assert len(resources) > 0
        assert any(r.category == "optimization" for r in resources)


class TestNextLearningSteps:
    """Test next learning steps suggestions."""

    def test_suggests_signature_learning(self, learning):
        """Should suggest signature learning for signature issues."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Signature issue",
                suggestion="Fix",
            )
        ]

        steps = learning.get_next_learning_steps(issues)

        assert len(steps) > 0
        assert any("signature" in step.lower() for step in steps)

    def test_suggests_module_learning(self, learning):
        """Should suggest module learning for module issues."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.MODULE,
                line=1,
                message="Module issue",
                suggestion="Fix",
            )
        ]

        steps = learning.get_next_learning_steps(issues)

        assert len(steps) > 0
        assert any("module" in step.lower() for step in steps)

    def test_suggests_optimization_learning(self, learning):
        """Should suggest optimization learning for metric issues."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.BEST_PRACTICE,
                line=1,
                message="Missing metric function",
                suggestion="Add metric",
            )
        ]

        steps = learning.get_next_learning_steps(issues)

        assert len(steps) > 0
        assert any("optimization" in step.lower() or "metric" in step.lower() for step in steps)

    def test_suggests_general_learning_for_no_issues(self, learning):
        """Should suggest general learning when no specific issues."""
        steps = learning.get_next_learning_steps([])

        assert len(steps) > 0
        assert any("pattern" in step.lower() or "best" in step.lower() for step in steps)

    def test_suggests_multiple_steps_for_multiple_issues(self, learning):
        """Should suggest multiple learning steps for multiple issue types."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Signature issue",
                suggestion="Fix",
            ),
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.MODULE,
                line=2,
                message="Module issue",
                suggestion="Fix",
            ),
        ]

        steps = learning.get_next_learning_steps(issues)

        assert len(steps) >= 2


class TestCodeComments:
    """Test adding educational comments to code."""

    def test_adds_header_comment(self, learning):
        """Should add header comment to code."""
        code = "class MyClass:\n    pass"
        issues = []

        commented_code = learning.generate_code_comments(code, issues)

        assert "DSPy Code" in commented_code
        assert "Educational Comments" in commented_code

    def test_adds_educational_comments_for_issues(self, learning):
        """Should add educational comments for issues."""
        code = "class MySignature(dspy.Signature):\n    field = dspy.InputField()"
        issues = [
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Signature issue",
                suggestion="Fix",
            )
        ]

        commented_code = learning.generate_code_comments(code, issues)

        # Should contain educational content
        assert len(commented_code) > len(code)
        assert "Signature" in commented_code

    def test_preserves_original_code(self, learning):
        """Should preserve original code lines."""
        code = "class MyClass:\n    pass"
        issues = []

        commented_code = learning.generate_code_comments(code, issues)

        assert "class MyClass:" in commented_code
        assert "pass" in commented_code

    def test_does_not_duplicate_comments(self, learning):
        """Should not add duplicate educational comments."""
        code = "class MySignature(dspy.Signature):\n    field1 = dspy.InputField()\n    field2 = dspy.InputField()"
        issues = [
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Issue 1",
                suggestion="Fix",
            ),
            ValidationIssue(
                severity=IssueSeverity.INFO,
                category=IssueCategory.SIGNATURE,
                line=2,
                message="Issue 2",
                suggestion="Fix",
            ),
        ]

        commented_code = learning.generate_code_comments(code, issues)

        # Should only add signature comment once
        signature_comment_count = commented_code.count("DSPy Signature:")
        assert signature_comment_count == 1


class TestResourceFormatting:
    """Test formatting of learning resources."""

    def test_formats_resources(self, learning):
        """Should format resources for display."""
        resources = [
            LearningResource(
                title="Test Resource",
                description="Test description",
                link="https://example.com",
                category="test",
            )
        ]

        formatted = learning.format_learning_resources(resources)

        assert "Test Resource" in formatted
        assert "Test description" in formatted
        assert "https://example.com" in formatted

    def test_formats_multiple_resources(self, learning):
        """Should format multiple resources."""
        resources = [
            LearningResource(
                title="Resource 1",
                description="Description 1",
                link="https://example1.com",
                category="test",
            ),
            LearningResource(
                title="Resource 2",
                description="Description 2",
                link="https://example2.com",
                category="test",
            ),
        ]

        formatted = learning.format_learning_resources(resources)

        assert "Resource 1" in formatted
        assert "Resource 2" in formatted

    def test_handles_empty_resources(self, learning):
        """Should handle empty resource list."""
        formatted = learning.format_learning_resources([])

        assert "No specific resources" in formatted


class TestCLICommands:
    """Test CLI command suggestions."""

    def test_suggests_signature_commands(self, learning):
        """Should suggest signature-related commands."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Signature issue",
                suggestion="Fix",
            )
        ]

        commands = learning.get_cli_commands_for_learning(issues)

        assert len(commands) > 0
        assert any("signature" in cmd.lower() for cmd in commands)

    def test_suggests_module_commands(self, learning):
        """Should suggest module-related commands."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.MODULE,
                line=1,
                message="Module issue",
                suggestion="Fix",
            )
        ]

        commands = learning.get_cli_commands_for_learning(issues)

        assert len(commands) > 0
        assert any("module" in cmd.lower() for cmd in commands)

    def test_always_includes_validate_command(self, learning):
        """Should always include validate command."""
        issues = []

        commands = learning.get_cli_commands_for_learning(issues)

        assert any("validate" in cmd.lower() for cmd in commands)

    def test_suggests_multiple_commands_for_multiple_issues(self, learning):
        """Should suggest multiple commands for different issue types."""
        issues = [
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.SIGNATURE,
                line=1,
                message="Signature issue",
                suggestion="Fix",
            ),
            ValidationIssue(
                severity=IssueSeverity.WARNING,
                category=IssueCategory.MODULE,
                line=2,
                message="Module issue",
                suggestion="Fix",
            ),
        ]

        commands = learning.get_cli_commands_for_learning(issues)

        assert len(commands) >= 2
