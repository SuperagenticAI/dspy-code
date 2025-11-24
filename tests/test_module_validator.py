"""
Tests for DSPy module validator.
"""

import ast

import pytest

from dspy_code.validation.models import IssueSeverity
from dspy_code.validation.module_validator import ModuleValidator


class TestModuleValidator:
    """Test module validator."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = ModuleValidator()
        assert validator is not None

    def test_validate_good_module(self):
        """Test validating a well-formed module."""
        code = '''
class EmailClassifier(dspy.Module):
    """Classify emails as spam or not spam."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(EmailSignature)

    def forward(self, email):
        return self.predictor(email=email)
'''
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should have no errors
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

    def test_validate_module_without_inheritance(self):
        """Test module not inheriting from dspy.Module."""
        code = '''
class EmailClassifier:
    """Classify emails."""

    def __init__(self):
        pass

    def forward(self, email):
        pass
'''
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should have error about missing inheritance
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) > 0
        assert any("inherit" in i.message.lower() for i in errors)

    def test_validate_module_without_init(self):
        """Test module without __init__ method."""
        code = '''
class EmailClassifier(dspy.Module):
    """Classify emails."""

    def forward(self, email):
        return email
'''
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should have warning about missing __init__
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert any("__init__" in i.message for i in warnings)

    def test_validate_module_without_super_init(self):
        """Test module without super().__init__() call."""
        code = '''
class EmailClassifier(dspy.Module):
    """Classify emails."""

    def __init__(self):
        self.predictor = dspy.Predict(EmailSignature)

    def forward(self, email):
        return self.predictor(email=email)
'''
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should have error about missing super().__init__()
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert any("super().__init__()" in i.message for i in errors)

    def test_validate_module_without_forward(self):
        """Test module without forward() method."""
        code = '''
class EmailClassifier(dspy.Module):
    """Classify emails."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(EmailSignature)
'''
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should have error about missing forward()
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert any("forward()" in i.message for i in errors)

    def test_validate_module_without_docstring(self):
        """Test module without docstring."""
        code = """
class EmailClassifier(dspy.Module):
    def __init__(self):
        super().__init__()

    def forward(self, email):
        return email
"""
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should have info about missing docstring
        infos = [i for i in issues if i.severity == IssueSeverity.INFO]
        assert any("docstring" in i.message.lower() for i in infos)

    def test_get_module_info(self):
        """Test extracting module information."""
        code = '''
class EmailClassifier(dspy.Module):
    """Classify emails."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(EmailSignature)
        self.fallback = dspy.Predict(EmailSignature)

    def forward(self, email):
        return self.predictor(email=email)

    def validate(self, email):
        return True
'''
        tree = ast.parse(code)
        module_node = tree.body[0]

        validator = ModuleValidator()
        info = validator.get_module_info(module_node)

        assert info["name"] == "EmailClassifier"
        assert info["has_init"] == True
        assert info["has_forward"] == True
        assert len(info["predictors"]) == 2
        assert "predictor" in info["predictors"]
        assert "fallback" in info["predictors"]
        assert "validate" in info["methods"]

    def test_validate_with_imported_module(self):
        """Test validation with directly imported Module."""
        code = '''
from dspy import Module

class EmailClassifier(Module):
    """Classify emails."""

    def __init__(self):
        super().__init__()

    def forward(self, email):
        return email
'''
        tree = ast.parse(code)
        module_node = tree.body[1]  # Second node (after import)

        validator = ModuleValidator()
        issues = validator.validate(module_node, code.split("\n"))

        # Should recognize Module even without dspy. prefix
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        # Should not have inheritance error
        assert not any("inherit" in i.message.lower() for i in errors)


class TestModuleValidatorIntegration:
    """Test module validator integration with main validator."""

    def test_full_validation_with_module(self):
        """Test full validation including module checks."""
        from dspy_code.validation import DSPyValidator

        code = """
import dspy

class EmailClassifier(dspy.Module):
    def __init__(self):
        self.predictor = dspy.Predict(EmailSignature)

    def forward(self, email):
        return self.predictor(email=email)
"""
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have error about missing super().__init__()
        assert len(report.errors) > 0
        assert any("super().__init__()" in i.message for i in report.errors)

    def test_validation_with_perfect_module(self):
        """Test validation with perfect module."""
        from dspy_code.validation import DSPyValidator

        code = '''
import dspy

class EmailClassifier(dspy.Module):
    """Classify emails as spam or not spam."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(EmailSignature)

    def forward(self, email):
        return self.predictor(email=email)
'''
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have minimal issues
        errors = [i for i in report.issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
