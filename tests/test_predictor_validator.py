"""
Tests for DSPy predictor validator.
"""

import ast

import pytest

from dspy_code.validation.models import IssueSeverity
from dspy_code.validation.predictor_validator import PredictorValidator


class TestPredictorValidator:
    """Test predictor validator."""

    def test_validator_initialization(self):
        """Test validator can be initialized."""
        validator = PredictorValidator()
        assert validator is not None

    def test_validate_predictor_with_signature(self):
        """Test validating predictor with signature."""
        code = """
import dspy

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(MySignature)
"""
        tree = ast.parse(code)

        validator = PredictorValidator()
        issues = validator.validate(tree, code.split("\n"))

        # Should have warning about missing configure
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert any("configure" in i.message.lower() for i in warnings)

    def test_validate_predictor_without_signature(self):
        """Test predictor without signature."""
        code = """
import dspy

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict()
"""
        tree = ast.parse(code)

        validator = PredictorValidator()
        issues = validator.validate(tree, code.split("\n"))

        # Should have error about missing signature
        errors = [i for i in issues if i.severity == IssueSeverity.ERROR]
        assert any("signature" in i.message.lower() for i in errors)

    def test_suggest_upgrade_from_predict(self):
        """Test suggestion to upgrade from Predict."""
        code = """
import dspy

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(MySignature)
"""
        tree = ast.parse(code)

        validator = PredictorValidator()
        issues = validator.validate(tree, code.split("\n"))

        # Should suggest ChainOfThought
        infos = [i for i in issues if i.severity == IssueSeverity.INFO]
        assert any("ChainOfThought" in i.message for i in infos)

    def test_validate_with_configure_call(self):
        """Test validation with dspy.configure() present."""
        code = """
import dspy

lm = dspy.LM(model='ollama/llama3.2')
dspy.configure(lm=lm)

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(MySignature)
"""
        tree = ast.parse(code)

        validator = PredictorValidator()
        issues = validator.validate(tree, code.split("\n"))

        # Should not have warning about missing configure
        warnings = [i for i in issues if i.severity == IssueSeverity.WARNING]
        assert not any("configure" in i.message.lower() for i in warnings)

    def test_suggest_predictor_for_task(self):
        """Test predictor suggestion based on task."""
        validator = PredictorValidator()

        # Test different task types
        assert validator.suggest_predictor("Use tools to search") == "ReAct"
        assert validator.suggest_predictor("Calculate math problem") == "ProgramOfThought"
        assert validator.suggest_predictor("Generate code") == "CodeAct"
        assert validator.suggest_predictor("Complex reasoning task") == "ChainOfThought"
        assert validator.suggest_predictor("Refine the output") == "Refine"
        assert validator.suggest_predictor("Simple classification") == "ChainOfThought"  # Default

    def test_get_predictor_info(self):
        """Test getting predictor information."""
        validator = PredictorValidator()

        info = validator.get_predictor_info("ChainOfThought")
        assert info is not None
        assert info["description"] == "Step-by-step reasoning"
        assert "complex reasoning" in info["best_for"]

        info = validator.get_predictor_info("ReAct")
        assert info is not None
        assert "tool usage" in info["best_for"]

    def test_compare_predictors(self):
        """Test comparing two predictors."""
        validator = PredictorValidator()

        comparison = validator.compare_predictors("Predict", "ChainOfThought")

        assert comparison["predictor1"]["name"] == "Predict"
        assert comparison["predictor2"]["name"] == "ChainOfThought"
        assert comparison["predictor1"]["complexity"] == "simple"
        assert comparison["predictor2"]["complexity"] == "moderate"

    def test_validate_multiple_predictors(self):
        """Test validation with multiple predictors."""
        code = """
import dspy

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor1 = dspy.Predict(Signature1)
        self.predictor2 = dspy.ChainOfThought(Signature2)
        self.predictor3 = dspy.ReAct(Signature3)
"""
        tree = ast.parse(code)

        validator = PredictorValidator()
        issues = validator.validate(tree, code.split("\n"))

        # Should have suggestions for Predict
        infos = [i for i in issues if i.severity == IssueSeverity.INFO]
        assert len(infos) > 0


class TestPredictorValidatorIntegration:
    """Test predictor validator integration."""

    def test_full_validation_with_predictors(self):
        """Test full validation including predictor checks."""
        from dspy_code.validation import DSPyValidator

        code = '''
import dspy

class EmailClassifier(dspy.Module):
    """Classify emails."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict()

    def forward(self, email):
        return self.predictor(email=email)
'''
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have error about missing signature
        assert len(report.errors) > 0
        assert any("signature" in i.message.lower() for i in report.errors)

    def test_validation_with_good_predictor_usage(self):
        """Test validation with proper predictor usage."""
        from dspy_code.validation import DSPyValidator

        code = '''
import dspy

lm = dspy.LM(model='ollama/llama3.2')
dspy.configure(lm=lm)

class EmailSignature(dspy.Signature):
    """Classify emails."""
    email: str = dspy.InputField(desc="Email text")
    category: str = dspy.OutputField(desc="Category")

class EmailClassifier(dspy.Module):
    """Classify emails."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(EmailSignature)

    def forward(self, email):
        return self.predictor(email=email)
'''
        validator = DSPyValidator()
        report = validator.validate_code(code, "test.py")

        # Should have minimal errors
        errors = [i for i in report.issues if i.severity == IssueSeverity.ERROR]
        assert len(errors) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
