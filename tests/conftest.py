"""
Pytest configuration and fixtures for DSPy Code tests.
"""

import pytest
from hypothesis import settings, Verbosity

# Configure hypothesis settings for property-based testing
settings.register_profile(
    "default",
    max_examples=100,
    verbosity=Verbosity.normal,
    deadline=None,  # Disable deadline for slow operations
)

settings.register_profile(
    "ci",
    max_examples=200,
    verbosity=Verbosity.normal,
    deadline=None,
)

settings.register_profile(
    "dev",
    max_examples=10,
    verbosity=Verbosity.verbose,
    deadline=None,
)

# Load profile from environment or use default
import os
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))


@pytest.fixture
def sample_dspy_signature_code():
    """Sample valid DSPy signature code for testing."""
    return '''import dspy

class SentimentAnalysis(dspy.Signature):
    """Analyze the sentiment of text."""
    
    text = dspy.InputField(desc="The text to analyze")
    sentiment = dspy.OutputField(desc="The sentiment: positive, negative, or neutral")
'''


@pytest.fixture
def sample_dspy_module_code():
    """Sample valid DSPy module code for testing."""
    return '''import dspy

class SentimentSignature(dspy.Signature):
    """Analyze sentiment."""
    text = dspy.InputField()
    sentiment = dspy.OutputField()

class SentimentModule(dspy.Module):
    """A module for sentiment analysis."""
    
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(SentimentSignature)
    
    def forward(self, text):
        """Analyze the sentiment of the given text."""
        return self.predictor(text=text)
'''


@pytest.fixture
def sample_invalid_code():
    """Sample invalid Python code for testing."""
    return '''
def broken_function(
    # Missing closing parenthesis
'''


@pytest.fixture
def sample_code_with_eval():
    """Sample code containing eval() for security testing."""
    return '''
def calculate(expression):
    return eval(expression)
'''


@pytest.fixture
def sample_code_with_exec():
    """Sample code containing exec() for security testing."""
    return '''
def run_code(code_string):
    exec(code_string)
'''
