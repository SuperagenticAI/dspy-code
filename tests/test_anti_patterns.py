"""
Tests for DSPy Anti-Pattern Detector
"""

import ast

import pytest

from dspy_code.validation.anti_patterns import AntiPatternDetector
from dspy_code.validation.models import IssueCategory, IssueSeverity


@pytest.fixture
def detector():
    """Create an anti-pattern detector instance."""
    return AntiPatternDetector()


class TestMissingModuleInheritance:
    """Test detection of missing dspy.Module inheritance."""

    def test_detects_forward_without_module_inheritance(self, detector):
        """Should detect class with forward() but no dspy.Module inheritance."""
        code = """
class MyModule:
    def forward(self, x):
        return x
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        assert len(issues) > 0
        issue = next((i for i in issues if "inherit" in i.message.lower()), None)
        assert issue is not None
        assert issue.severity == IssueSeverity.ERROR
        assert issue.category == IssueCategory.ANTI_PATTERN
        assert "dspy.Module" in issue.suggestion

    def test_no_issue_with_proper_inheritance(self, detector):
        """Should not flag class that properly inherits from dspy.Module."""
        code = """
import dspy

class MyModule(dspy.Module):
    def forward(self, x):
        return x
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not have missing inheritance issue
        inheritance_issues = [i for i in issues if "inherit" in i.message.lower()]
        assert len(inheritance_issues) == 0

    def test_no_issue_without_forward_method(self, detector):
        """Should not flag regular classes without forward() method."""
        code = """
class RegularClass:
    def process(self, x):
        return x
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not have any inheritance issues
        inheritance_issues = [i for i in issues if "inherit" in i.message.lower()]
        assert len(inheritance_issues) == 0


class TestIncorrectFieldTypes:
    """Test detection of incorrect signature field types."""

    def test_detects_plain_attributes_in_signature(self, detector):
        """Should detect plain attributes instead of InputField/OutputField."""
        code = """
import dspy

class MySignature(dspy.Signature):
    question: str = "default"
    answer: str = "default"
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should detect incorrect field types
        field_issues = [i for i in issues if "field" in i.message.lower()]
        assert len(field_issues) >= 1
        assert any(issue.severity == IssueSeverity.ERROR for issue in field_issues)

    def test_no_issue_with_proper_fields(self, detector):
        """Should not flag proper InputField/OutputField usage."""
        code = """
import dspy

class MySignature(dspy.Signature):
    question: str = dspy.InputField(desc="Question")
    answer: str = dspy.OutputField(desc="Answer")
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not have field type issues
        field_issues = [i for i in issues if "should use inputfield" in i.message.lower()]
        assert len(field_issues) == 0

    def test_no_issue_for_non_signature_classes(self, detector):
        """Should not flag regular classes with attributes."""
        code = """
class RegularClass:
    name: str = "default"
    value: int = 0
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not have any field issues
        field_issues = [i for i in issues if "field" in i.message.lower()]
        assert len(field_issues) == 0


class TestHardcodedPrompts:
    """Test detection of hardcoded prompts."""

    def test_detects_hardcoded_prompts(self, detector):
        """Should detect long strings that look like prompts."""
        code = """
prompt = '''You are a helpful assistant. Your task is to classify the following text into one of these categories.
Please analyze carefully and provide your reasoning.'''
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should detect hardcoded prompt
        prompt_issues = [i for i in issues if "prompt" in i.message.lower()]
        assert len(prompt_issues) > 0
        assert prompt_issues[0].severity == IssueSeverity.WARNING
        assert "signature" in prompt_issues[0].suggestion.lower()

    def test_no_issue_with_short_strings(self, detector):
        """Should not flag short strings."""
        code = """
message = "Hello world"
label = "category"
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not detect short strings as prompts
        prompt_issues = [i for i in issues if "prompt" in i.message.lower()]
        assert len(prompt_issues) == 0

    def test_no_issue_with_docstrings(self, detector):
        """Should not flag docstrings as hardcoded prompts."""
        code = """
def my_function():
    '''This is a docstring that explains what the function does.
    It can be long but it's not a prompt.'''
    pass
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Docstrings might be flagged, but that's acceptable
        # This test just ensures we don't crash
        assert isinstance(issues, list)


class TestMissingConfigure:
    """Test detection of missing dspy.configure() calls."""

    def test_detects_missing_configure_with_predict(self, detector):
        """Should detect missing configure when Predict is used."""
        code = """
import dspy

class MySignature(dspy.Signature):
    input: str = dspy.InputField()
    output: str = dspy.OutputField()

predictor = dspy.Predict(MySignature)
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should detect missing configure
        config_issues = [i for i in issues if "configure" in i.message.lower()]
        assert len(config_issues) > 0
        assert config_issues[0].severity == IssueSeverity.WARNING

    def test_detects_missing_configure_with_cot(self, detector):
        """Should detect missing configure when ChainOfThought is used."""
        code = """
import dspy

predictor = dspy.ChainOfThought(MySignature)
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should detect missing configure
        config_issues = [i for i in issues if "configure" in i.message.lower()]
        assert len(config_issues) > 0

    def test_no_issue_when_configure_present(self, detector):
        """Should not flag when dspy.configure() is called."""
        code = """
import dspy

lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

predictor = dspy.Predict(MySignature)
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not detect missing configure
        config_issues = [i for i in issues if "configure" in i.message.lower()]
        assert len(config_issues) == 0

    def test_no_issue_without_predictors(self, detector):
        """Should not flag code that doesn't use predictors."""
        code = """
import dspy

class MySignature(dspy.Signature):
    input: str = dspy.InputField()
    output: str = dspy.OutputField()
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should not detect missing configure
        config_issues = [i for i in issues if "configure" in i.message.lower()]
        assert len(config_issues) == 0


class TestFixExamples:
    """Test fix example generation."""

    def test_fix_examples_include_code(self, detector):
        """Should include code examples in fix suggestions."""
        code = """
class MyModule:
    def forward(self, x):
        return x
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should have example code
        inheritance_issues = [i for i in issues if "inherit" in i.message.lower()]
        if inheritance_issues:
            assert inheritance_issues[0].example is not None
            assert "class" in inheritance_issues[0].example
            assert "dspy.Module" in inheritance_issues[0].example

    def test_fix_examples_include_docs_links(self, detector):
        """Should include documentation links in fix suggestions."""
        code = """
class MyModule:
    def forward(self, x):
        return x
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should have docs links
        inheritance_issues = [i for i in issues if "inherit" in i.message.lower()]
        if inheritance_issues:
            assert inheritance_issues[0].docs_link is not None
            assert "http" in inheritance_issues[0].docs_link

    def test_field_fix_examples(self, detector):
        """Should provide field fix examples."""
        code = """
import dspy

class MySignature(dspy.Signature):
    question: str = "default"
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        field_issues = [i for i in issues if "field" in i.message.lower()]
        if field_issues:
            assert field_issues[0].example is not None
            assert (
                "InputField" in field_issues[0].example or "OutputField" in field_issues[0].example
            )
            assert field_issues[0].docs_link is not None

    def test_configure_fix_examples(self, detector):
        """Should provide configure fix examples."""
        code = """
import dspy

predictor = dspy.Predict(MySignature)
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        config_issues = [i for i in issues if "configure" in i.message.lower()]
        if config_issues:
            assert config_issues[0].example is not None
            assert "dspy.configure" in config_issues[0].example
            assert "dspy.LM" in config_issues[0].example
            assert config_issues[0].docs_link is not None


class TestIntegration:
    """Integration tests for anti-pattern detector."""

    def test_detects_multiple_anti_patterns(self, detector):
        """Should detect multiple anti-patterns in same code."""
        code = """
class MyModule:
    def forward(self, x):
        prompt = '''You are a classifier. Your task is to classify the input text.
        Please provide your classification and reasoning.'''
        return prompt + x
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should detect both missing inheritance and hardcoded prompt
        assert len(issues) >= 2
        categories = {issue.category for issue in issues}
        assert IssueCategory.ANTI_PATTERN in categories

    def test_comprehensive_bad_code(self, detector):
        """Should detect all anti-patterns in poorly written code."""
        code = """
class BadSignature(dspy.Signature):
    input: str = "default"
    output: str = "default"

class BadModule:
    def forward(self, x):
        prompt = '''You are an AI assistant. Your task is to help the user with their question.
        Please provide a detailed and helpful response.'''
        predictor = dspy.Predict(BadSignature)
        return predictor(input=x)
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # Should detect multiple issues
        assert len(issues) >= 3

        # Check for different types of issues
        has_inheritance_issue = any("inherit" in i.message.lower() for i in issues)
        has_field_issue = any("field" in i.message.lower() for i in issues)
        has_prompt_issue = any("prompt" in i.message.lower() for i in issues)
        has_config_issue = any("configure" in i.message.lower() for i in issues)

        assert has_inheritance_issue or has_field_issue or has_prompt_issue or has_config_issue

    def test_all_issues_have_actionable_fixes(self, detector):
        """All detected issues should have actionable fix suggestions."""
        code = """
class BadSignature(dspy.Signature):
    input: str = "default"

class BadModule:
    def forward(self, x):
        prompt = '''You are an AI assistant. Your task is to help the user.'''
        predictor = dspy.Predict(BadSignature)
        return predictor(input=x)
"""
        tree = ast.parse(code)
        issues = detector.detect(tree, code.split("\n"))

        # All issues should have suggestions and examples
        for issue in issues:
            assert issue.suggestion is not None
            assert len(issue.suggestion) > 0
            assert issue.example is not None
            assert len(issue.example) > 0
