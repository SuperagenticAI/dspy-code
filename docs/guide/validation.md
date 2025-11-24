# Code Validation

Learn how DSPy Code validates your code for quality, correctness, and best practices.

## What is Validation?

DSPy Code's validation engine checks your DSPy code for:

- ✅ Correct DSPy patterns
- ✅ Best practices
- ✅ Syntax errors
- ✅ Type hints
- ✅ Documentation
- ✅ Anti-patterns

**Result**: High-quality, production-ready DSPy code!

## Quick Start

### Validate Generated Code

After generating code:

```
Create a sentiment analyzer
/validate
```

### Validate Existing File

```
/validate my_module.py
```

### Validate All Project Files

```
/validate-project
```

## Validation Checks

### 1. Signature Validation

**Checks:**

- ✅ Inherits from `dspy.Signature`
- ✅ Has at least one `InputField`
- ✅ Has at least one `OutputField`
- ✅ Fields have descriptions
- ✅ Docstring present
- ✅ Type hints used

**Example - Valid Signature:**

```python
class SentimentSignature(dspy.Signature):
    """Analyze sentiment of text."""

    text: str = dspy.InputField(
        desc="Text to analyze"
    )
    sentiment: str = dspy.OutputField(
        desc="positive, negative, or neutral"
    )
```

**Example - Invalid Signature:**

```python
# ✗ Missing docstring
# ✗ No field descriptions
# ✗ No type hints
class SentimentSignature(dspy.Signature):
    text = dspy.InputField()
    sentiment = dspy.OutputField()
```

### 2. Module Validation

**Checks:**

- ✅ Inherits from `dspy.Module`
- ✅ Has `__init__` method
- ✅ Calls `super().__init__()`
- ✅ Has `forward` method
- ✅ Uses DSPy predictors
- ✅ Returns proper values

**Example - Valid Module:**

```python
class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(SentimentSignature)

    def forward(self, text: str) -> dspy.Prediction:
        return self.predictor(text=text)
```

**Example - Invalid Module:**

```python
# ✗ Doesn't inherit from dspy.Module
# ✗ No super().__init__()
# ✗ No forward method
class SentimentAnalyzer:
    def __init__(self):
        self.predictor = dspy.Predict(SentimentSignature)

    def analyze(self, text):  # ✗ Should be 'forward'
        return self.predictor(text=text)
```

### 3. Predictor Usage

**Checks:**

- ✅ Uses valid DSPy predictors
- ✅ Predictor initialized correctly
- ✅ Signature passed to predictor
- ✅ Predictor called properly

**Valid predictors:**

- `dspy.Predict`
- `dspy.ChainOfThought`
- `dspy.ReAct`
- `dspy.ProgramOfThought`
- `dspy.MultiChainComparison`

**Example - Valid:**

```python
self.predictor = dspy.ChainOfThought(SentimentSignature)
result = self.predictor(text=input_text)
```

**Example - Invalid:**

```python
# ✗ Not a DSPy predictor
self.predictor = SentimentSignature()

# ✗ Wrong usage
result = self.predictor.predict(text=input_text)
```

### 4. Best Practices

**Checks:**

- ✅ Descriptive variable names
- ✅ Proper error handling
- ✅ No hardcoded values
- ✅ Modular design
- ✅ DRY principle
- ✅ Clear logic flow

**Example - Good Practices:**

```python
class EmailClassifier(dspy.Module):
    """Classify emails into categories."""

    def __init__(self, categories: List[str]):
        super().__init__()

        # Validate input
        if not categories:
            raise ValueError("Categories list cannot be empty")

        self.categories = categories
        self.classifier = dspy.ChainOfThought(EmailSignature)

    def forward(self, email: str) -> dspy.Prediction:
        """Classify an email."""

        # Input validation
        if not email or not email.strip():
            raise ValueError("Email cannot be empty")

        # Classify
        try:
            result = self.classifier(
                email=email,
                categories=", ".join(self.categories)
            )
            return result
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise
```

**Example - Bad Practices:**

```python
class EmailClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        # ✗ Hardcoded categories
        self.c = dspy.ChainOfThought(EmailSignature)

    def forward(self, e):  # ✗ Unclear parameter name
        # ✗ No error handling
        # ✗ No validation
        r = self.c(email=e, categories="spam,work,personal")
        return r
```

### 5. Type Hints

**Checks:**

- ✅ Function parameters have types
- ✅ Return types specified
- ✅ Field types in signatures
- ✅ Consistent type usage

**Example - Good Type Hints:**

```python
from typing import List, Optional
import dspy

class Analyzer(dspy.Module):
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        super().__init__()
        self.model_name: str = model_name
        self.predictor: dspy.Predict = dspy.Predict(AnalysisSignature)

    def forward(
        self,
        text: str,
        context: Optional[str] = None
    ) -> dspy.Prediction:
        return self.predictor(text=text, context=context or "")
```

**Example - Missing Type Hints:**

```python
class Analyzer(dspy.Module):
    def __init__(self, model_name="gpt-3.5-turbo"):  # ✗ No type
        super().__init__()
        self.model_name = model_name
        self.predictor = dspy.Predict(AnalysisSignature)

    def forward(self, text, context=None):  # ✗ No types
        return self.predictor(text=text, context=context or "")
```

### 6. Documentation

**Checks:**

- ✅ Module docstring
- ✅ Method docstrings
- ✅ Signature docstring
- ✅ Parameter descriptions
- ✅ Return value descriptions

**Example - Well Documented:**

```python
class SentimentAnalyzer(dspy.Module):
    """
    Analyze sentiment of text using DSPy.

    This module uses ChainOfThought reasoning to classify
    text sentiment as positive, negative, or neutral.

    Attributes:
        predictor: DSPy ChainOfThought predictor
    """

    def __init__(self):
        """Initialize the sentiment analyzer."""
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentSignature)

    def forward(self, text: str) -> dspy.Prediction:
        """
        Analyze sentiment of given text.

        Args:
            text: Text to analyze

        Returns:
            Prediction with sentiment field

        Raises:
            ValueError: If text is empty
        """
        if not text:
            raise ValueError("Text cannot be empty")

        return self.predictor(text=text)
```

## Validation Report

### Report Structure

```
╭─────────────────────── Validation Report ───────────────────────╮
│                                                                  │
│ File: sentiment_analyzer.py                                     │
│                                                                  │
│ ✓ Signature Structure                                           │
│   - Inherits from dspy.Signature                                │
│   - Has InputField and OutputField                              │
│   - Fields have descriptions                                    │
│                                                                  │
│ ✓ Module Structure                                              │
│   - Inherits from dspy.Module                                   │
│   - Has __init__ and forward methods                            │
│   - Uses DSPy predictors                                        │
│                                                                  │
│ ⚠ Best Practices                                                │
│   ✓ Descriptive names                                           │
│   ✓ Error handling                                              │
│   ✗ Missing type hints on line 15                               │
│                                                                  │
│ ✓ Documentation                                                 │
│   - Module docstring present                                    │
│   - Method docstrings present                                   │
│                                                                  │
│ Quality Score: 92/100                                           │
│                                                                  │
│ Issues Found: 1                                                 │
│ Warnings: 1                                                     │
│                                                                  │
╰──────────────────────────────────────────────────────────────────╯

Recommendations:
• Add type hint to parameter 'text' on line 15
```

### Score Breakdown

**100 points total:**

- Signature structure: 20 points
- Module structure: 20 points
- Best practices: 30 points
- Documentation: 15 points
- Type hints: 15 points

**Score ranges:**

- 90-100: Excellent ⭐⭐⭐
- 80-89: Good ⭐⭐
- 70-79: Acceptable ⭐
- <70: Needs improvement ⚠️

## Anti-Pattern Detection

### Common Anti-Patterns

**1. Direct LLM Calls:**

```python
# ✗ Anti-pattern
import openai
response = openai.ChatCompletion.create(...)

# ✓ Use DSPy
predictor = dspy.Predict(MySignature)
response = predictor(input=data)
```

**2. String-Based Prompts:**

```python
# ✗ Anti-pattern
prompt = f"Analyze this: {text}"
response = llm(prompt)

# ✓ Use Signatures
class AnalysisSignature(dspy.Signature):
    text = dspy.InputField()
    analysis = dspy.OutputField()

predictor = dspy.Predict(AnalysisSignature)
response = predictor(text=text)
```

**3. Manual Prompt Engineering:**

```python
# ✗ Anti-pattern
prompt = "You are an expert. Analyze carefully. Think step by step..."

# ✓ Use ChainOfThought
predictor = dspy.ChainOfThought(AnalysisSignature)
```

**4. Hardcoded Examples:**

```python
# ✗ Anti-pattern
prompt = """
Example 1: ...
Example 2: ...
Now analyze: {text}
"""

# ✓ Use DSPy optimization
optimized = optimizer.compile(program, trainset=examples)
```

**5. No Error Handling:**

```python
# ✗ Anti-pattern
def forward(self, text):
    return self.predictor(text=text)

# ✓ Add error handling
def forward(self, text: str) -> dspy.Prediction:
    if not text:
        raise ValueError("Text cannot be empty")

    try:
        return self.predictor(text=text)
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise
```

## Auto-Fix Suggestions

### Fixable Issues

DSPy Code can suggest fixes for common issues:

**Missing Type Hints:**

```
Issue: Missing type hint on parameter 'text'

Suggested fix:
  def forward(self, text: str) -> dspy.Prediction:
```

**Missing Docstring:**

```
Issue: Module missing docstring

Suggested fix:
  class MyModule(dspy.Module):
      """[Description of what this module does]"""
```

**Missing Field Description:**

```
Issue: InputField missing description

Suggested fix:
  text = dspy.InputField(desc="Text to analyze")
```

### Apply Fixes

```
/validate my_module.py
/fix my_module.py
```

DSPy Code applies suggested fixes automatically!

## Validation in Workflow

### During Development

Validate frequently:

```
→ Create a classifier
  [Code generated]

→ /validate
  ✓ Score: 95/100

→ Add confidence scores
  [Code updated]

→ /validate
  ⚠ Score: 88/100 - Missing type hint

→ Fix the type hint issue
  [Code fixed]

→ /validate
  ✓ Score: 98/100
```

### Before Saving

Always validate before saving:

```
/validate
/save module.py
```

### Before Optimization

Ensure code quality before GEPA:

```
/validate program.py
/optimize program.py data.jsonl
```

### In CI/CD

Integrate validation in CI:

```bash
#!/bin/bash
# validate.sh

for file in generated/*.py; do
    dspy-code validate "$file" || exit 1
done
```

## Custom Validation Rules

### Add Project-Specific Rules

Create `.dspy-code/validation-rules.yaml`:

```yaml
rules:
  # Require specific predictor types
  required_predictors:
    - ChainOfThought
    - ReAct

  # Disallow certain patterns
  disallowed_patterns:
    - "import openai"
    - "import anthropic"

  # Require specific fields
  required_signature_fields:
    - description
    - examples

  # Naming conventions
  naming:
    signature_suffix: "Signature"
    module_suffix: "Module"

  # Minimum quality score
  min_quality_score: 85
```

### Enable Custom Rules

```
/validate --strict my_module.py
```

## Validation API

### Programmatic Validation

Use validation in your scripts:

```python
from dspy_code.validation import ModuleValidator

# Create validator
validator = ModuleValidator()

# Validate file
report = validator.validate_file("my_module.py")

# Check results
if report.score >= 90:
    print("Excellent code!")
elif report.score >= 70:
    print("Good code, minor issues")
else:
    print("Needs improvement")

# Get issues
for issue in report.issues:
    print(f"{issue.severity}: {issue.message} (line {issue.line})")

# Get suggestions
for suggestion in report.suggestions:
    print(f"Suggestion: {suggestion}")
```

### Batch Validation

Validate multiple files:

```python
from dspy_code.validation import ProjectValidator

validator = ProjectValidator()
reports = validator.validate_project("./generated")

for filepath, report in reports.items():
    print(f"{filepath}: {report.score}/100")
```

## Best Practices

### 1. Validate Early and Often

Don't wait until the end:

```
Generate → Validate → Refine → Validate → Save
```

### 2. Aim for 90+

Strive for excellent scores:

- 90-100: Production-ready
- 80-89: Good for prototypes
- <80: Needs work

### 3. Fix Issues Incrementally

Don't try to fix everything at once:

```
→ /validate
  Issues: 5

→ Fix highest priority issue
→ /validate
  Issues: 4

→ Continue...
```

### 4. Use Auto-Fix

Let DSPy Code help:

```
/validate
/fix
/validate
```

### 5. Learn from Reports

Understand why issues occur:

```
→ Why is this an issue?
→ How can I avoid this in the future?
→ What's the best practice here?
```

## Troubleshooting

### False Positives

If validator flags valid code:

```
/validate --lenient my_module.py
```

### Custom Patterns

If your code uses custom patterns:

```
/validate --ignore-rule <rule-name> my_module.py
```

### Performance Issues

For large files:

```
/validate --quick my_module.py
```

## Summary

Validation ensures:

- ✅ Correct DSPy patterns
- ✅ Best practices followed
- ✅ High code quality
- ✅ Production readiness
- ✅ Maintainability

**Key points:**

- Validate frequently
- Aim for 90+ scores
- Fix issues incrementally
- Use auto-fix when available
- Learn from validation reports

[Learn About Running Code →](running-programs.md){ .md-button .md-button--primary }
[See Validation Examples →](../tutorials/sentiment-analyzer.md){ .md-button }
