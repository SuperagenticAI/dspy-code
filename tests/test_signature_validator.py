"""
Tests for DSPy signature validator.
"""

import ast

import pytest

from dspy_code.validation.models import IssueSeverity
from dspy_code.validation.signature_validator import SignatureValidator


class TestSignatureValidator:
    """Test signature validator."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = SignatureValidator()
        assert validator is not None

    def test_validate_good_signature(self):
        """Test validating a well-formed signature."""
        code = '''
class EmailSignature(dspy.Signature):
    """Classify email as spam or not spam."""
    email: str = dspy.InputField(desc="Email text to classify")
    category: str = dspy.OutputField(desc="Classification result")
'''
        tree = ast.parse(code)
        signature_node = tree.body[0]

        validator = SignatureValidator()
        issues = validator.validate(signature_node, code.split("\n"))

        # Should have no errors
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0

    def test_validate_signature_without_docstring(self):
        """Test signature without docstring."""
        code = """
class EmailSignature(dspy.Signature):
    email: str = dspy.InputField(desc="Email text")
    category: str = dspy.OutputField(desc="Category")
"""
        tree = ast.parse(code)
        signature_node = tree.body[0]

        validator = SignatureValidator()
        issues = validator.validate(signature_node, code.split("\n"))

        # Should have info about missing docstring
        assert any("docstring" in i.message.lower() for i in issues)

    def test_validate_field_without_description(self):
        """Test field without description."""
        code = '''
class EmailSignature(dspy.Signature):
    """Classify emails."""
    email: str = dspy.InputField()
    category: str = dspy.OutputField()
'''
        tree = ast.parse(code)
        signature_node = tree.body[0]

        validator = SignatureValidator()
        issues = validator.validate(signature_node, code.split("\n"))

        # Should have warnings about missing descriptions
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert len(warnings) >= 2  # Both fields missing descriptions
        assert any("description" in i.message.lower() for i in warnings)

    def test_validate_field_without_dspy_field(self):
        """Test field not using InputField/OutputField."""
        code = '''
class EmailSignature(dspy.Signature):
    """Classify emails."""
    email: str = "default"
    category: str = "spam"
'''
        tree = ast.parse(code)
        signature_node = tree.body[0]

        validator = SignatureValidator()
        issues = validator.validate(signature_node, code.split("\n"))

        # Should have errors about not using DSPy fields
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) >= 2
        assert any("InputField" in i.message or "OutputField" in i.message for i in errors)

    def test_validate_field_without_type_hint(self):
        """Test field without type hint."""
        code = '''
class EmailSignature(dspy.Signature):
    """Classify emails."""
    email = dspy.InputField(desc="Email text")
'''
        tree = ast.parse(code)
        signature_node = tree.body[0]

        validator = SignatureValidator()
        issues = validator.validate(signature_node, code.split("\n"))

        # Should have warning about missing type hint
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert any("type hint" in i.message.lower() for i in warnings)

    def test_get_field_info(self):
        """Test extracting field information."""
        code = '''
class EmailSignature(dspy.Signature):
    """Classify emails."""
    email: str = dspy.InputField(desc="Email text")
    context: str = dspy.InputField(desc="Context")
    category: str = dspy.OutputField(desc="Category")
    confidence: float = dspy.OutputField(desc="Confidence score")
'''
        tree = ast.parse(code)
        signature_node = tree.body[0]

        validator = SignatureValidator()
        field_info = validator.get_field_info(signature_node)

        assert len(field_info["input_fields"]) == 2
        assert "email" in field_info["input_fields"]
        assert "context" in field_info["input_fields"]

        assert len(field_info["output_fields"]) == 2
        assert "category" in field_info["output_fields"]
        assert "confidence" in field_info["output_fields"]

    def test_validate_with_imported_fields(self):
        """Test validation with directly imported fields."""
        code = '''
from dspy import InputField, OutputField

class EmailSignature(dspy.Signature):
    """Classify emails."""
    email: str = InputField(desc="Email text")
    category: str = OutputField(desc="Category")
'''
        tree = ast.parse(code)
        signature_node = tree.body[1]  # Second node (after import)

        validator = SignatureValidator()
        issues = validator.validate(signature_node, code.split("\n"))

        # Should recognize InputField/OutputField even without dspy. prefix
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


class TestSignatureValidatorIntegration:
    """Test signature validator integration with main validator."""

    def test_full_validation_with_signature(self):
        """Test full validation including signature checks."""
        from dspy_code.validation import DSPyValidator

        code = """
import dspy

class EmailSignature(dspy.Signature):
    email: str = dspy.InputField()
    category: str = dspy.OutputField()
"""
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have warnings about missing descriptions
        assert len(report.warnings) > 0
        assert any("description" in i.message.lower() for i in report.warnings)

    def test_validation_with_perfect_signature(self):
        """Test validation with perfect signature."""
        from dspy_code.validation import DSPyValidator

        code = '''
import dspy

class EmailSignature(dspy.Signature):
    """Classify email as spam or not spam."""
    email: str = dspy.InputField(desc="Email text to classify")
    category: str = dspy.OutputField(desc="Classification result: spam or not_spam")
'''
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have minimal issues
        errors = [i for i in report.issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
