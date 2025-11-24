# Generating Code

Master code generation with DSPy Code to create Signatures, Modules, and complete programs.

## Overview

DSPy Code generates DSPy code from natural language descriptions. You can create:

- **Signatures** - Input/output specifications
- **Modules** - DSPy programs with predictors
- **Complete Programs** - Full applications with examples
- **Optimizers** - GEPA optimization scripts
- **Evaluations** - Testing and evaluation code

## Generating Signatures

### Basic Signature

Describe inputs and outputs:

```
Create a signature for sentiment analysis with text input and sentiment output
```

**Generated:**

```python
import dspy

class SentimentSignature(dspy.Signature):
    """Analyze sentiment of text."""

    text: str = dspy.InputField(
        desc="Text to analyze"
    )
    sentiment: str = dspy.OutputField(
        desc="Sentiment: positive, negative, or neutral"
    )
```

### Multiple Fields

Specify multiple inputs/outputs:

```
Create a signature for email classification with subject, body, and sender as inputs, and category and priority as outputs
```

**Generated:**

```python
class EmailClassificationSignature(dspy.Signature):
    """Classify emails by category and priority."""

    subject: str = dspy.InputField(desc="Email subject line")
    body: str = dspy.InputField(desc="Email body content")
    sender: str = dspy.InputField(desc="Sender email address")

    category: str = dspy.OutputField(
        desc="Email category: work, personal, spam, etc."
    )
    priority: str = dspy.OutputField(
        desc="Priority level: high, medium, low"
    )
```

### With Type Specifications

Specify field types:

```
Create a signature with question (string) and context (string) as inputs, answer (string) and confidence (float) as outputs
```

**Generated:**

```python
class QASignature(dspy.Signature):
    """Answer questions based on context."""

    question: str = dspy.InputField(desc="Question to answer")
    context: str = dspy.InputField(desc="Context for answering")

    answer: str = dspy.OutputField(desc="Answer to the question")
    confidence: float = dspy.OutputField(
        desc="Confidence score (0.0 to 1.0)"
    )
```

### With Examples

Include example values:

```
Create a signature for text classification where:
- Input: "I love this product!" → Output: "positive"
- Input: "Terrible experience" → Output: "negative"
- Input: "It's okay" → Output: "neutral"
```

**Generated with examples in docstring:**

```python
class TextClassificationSignature(dspy.Signature):
    """
    Classify text sentiment.

    Examples:
        "I love this product!" → "positive"
        "Terrible experience" → "negative"
        "It's okay" → "neutral"
    """

    text: str = dspy.InputField(desc="Text to classify")
    sentiment: str = dspy.OutputField(
        desc="Sentiment: positive, negative, or neutral"
    )
```

## Generating Modules

### Basic Module

Specify the task:

```
Build a module for sentiment analysis
```

**Generated:**

```python
import dspy

class SentimentSignature(dspy.Signature):
    """Analyze sentiment of text."""
    text: str = dspy.InputField(desc="Text to analyze")
    sentiment: str = dspy.OutputField(desc="Sentiment classification")

class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(SentimentSignature)

    def forward(self, text: str) -> dspy.Prediction:
        return self.predictor(text=text)
```

### With Specific Predictor

Choose reasoning pattern:

```
Build a module using ChainOfThought for sentiment analysis
```

**Generated:**

```python
class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentSignature)

    def forward(self, text: str) -> dspy.Prediction:
        return self.predictor(text=text)
```

**Available predictors:**

- `Predict` - Basic prediction
- `ChainOfThought` - Step-by-step reasoning
- `ReAct` - Reasoning + Acting
- `ProgramOfThought` - Code-based reasoning
- `MultiChainComparison` - Multiple reasoning chains

### Multi-Step Module

Create complex workflows:

```
Build a RAG module that retrieves context then generates an answer
```

**Generated:**

```python
class RetrievalSignature(dspy.Signature):
    """Retrieve relevant context."""
    question: str = dspy.InputField()
    context: str = dspy.OutputField()

class GenerationSignature(dspy.Signature):
    """Generate answer from context."""
    question: str = dspy.InputField()
    context: str = dspy.InputField()
    answer: str = dspy.OutputField()

class RAGModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retriever = dspy.Predict(RetrievalSignature)
        self.generator = dspy.ChainOfThought(GenerationSignature)

    def forward(self, question: str) -> dspy.Prediction:
        # Step 1: Retrieve context
        retrieval = self.retriever(question=question)

        # Step 2: Generate answer
        answer = self.generator(
            question=question,
            context=retrieval.context
        )

        return answer
```

### With Configuration

Add configurable parameters:

```
Build a classifier module with configurable categories
```

**Generated:**

```python
from typing import List

class Classifier(dspy.Module):
    def __init__(self, categories: List[str]):
        super().__init__()

        if not categories:
            raise ValueError("Categories cannot be empty")

        self.categories = categories
        self.predictor = dspy.ChainOfThought(ClassificationSignature)

    def forward(self, text: str) -> dspy.Prediction:
        categories_str = ", ".join(self.categories)
        return self.predictor(
            text=text,
            categories=categories_str
        )
```

## Generating Complete Programs

### Full Application

Request a complete solution:

```
Generate a complete program for sentiment analysis with examples and configuration
```

**Generated:**

```python
"""
Sentiment Analysis Program
Generated by DSPy Code
"""

import dspy
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Signature
class SentimentSignature(dspy.Signature):
    """Analyze sentiment of text."""
    text: str = dspy.InputField(desc="Text to analyze")
    sentiment: str = dspy.OutputField(
        desc="Sentiment: positive, negative, or neutral"
    )

# Module
class SentimentAnalyzer(dspy.Module):
    """Sentiment analysis module using DSPy."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentSignature)

    def forward(self, text: str) -> dspy.Prediction:
        """Analyze sentiment of text."""
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            result = self.predictor(text=text)
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise

# Configuration
def configure_dspy(
    provider: str = "ollama",
    model: str = "llama3.1:8b",
    api_key: Optional[str] = None
):
    """Configure DSPy with specified model."""

    if provider == "ollama":
        lm = dspy.OllamaLocal(model=model)
    elif provider == "openai":
        lm = dspy.OpenAI(model=model, api_key=api_key)
    elif provider == "anthropic":
        lm = dspy.Anthropic(model=model, api_key=api_key)
    else:
        raise ValueError(f"Unknown provider: {provider}")

    dspy.settings.configure(lm=lm)
    logger.info(f"Configured DSPy with {provider}/{model}")

# Main
def main():
    """Main execution."""

    # Configure
    configure_dspy(provider="ollama", model="llama3.1:8b")

    # Create analyzer
    analyzer = SentimentAnalyzer()

    # Test examples
    examples = [
        "I love this product! It's amazing!",
        "Terrible experience, very disappointed.",
        "It's okay, nothing special."
    ]

    print("Sentiment Analysis Results:\n")
    for text in examples:
        result = analyzer(text=text)
        print(f"Text: {text}")
        print(f"Sentiment: {result.sentiment}")
        print(f"Reasoning: {result.rationale}\n")

if __name__ == "__main__":
    main()
```

### With Data Generation

Include synthetic data:

```
Generate a complete program with 20 training examples for sentiment analysis
```

**Includes data generation code:**

```python
# ... (program code) ...

def generate_training_data(num_examples: int = 20):
    """Generate synthetic training data."""

    examples = []

    # Positive examples
    positive_texts = [
        "I love this!",
        "Amazing product!",
        "Best purchase ever!",
        # ... more examples
    ]

    # Negative examples
    negative_texts = [
        "Terrible quality",
        "Very disappointed",
        "Waste of money",
        # ... more examples
    ]

    # Neutral examples
    neutral_texts = [
        "It's okay",
        "Nothing special",
        "Average product",
        # ... more examples
    ]

    # Create dspy.Example objects
    for text in positive_texts[:num_examples//3]:
        examples.append(
            dspy.Example(text=text, sentiment="positive").with_inputs('text')
        )

    for text in negative_texts[:num_examples//3]:
        examples.append(
            dspy.Example(text=text, sentiment="negative").with_inputs('text')
        )

    for text in neutral_texts[:num_examples//3]:
        examples.append(
            dspy.Example(text=text, sentiment="neutral").with_inputs('text')
        )

    return examples
```

## Generation Options

### Specify Complexity

**Simple:**

```
Create a simple sentiment analyzer
```

**Advanced:**

```
Create an advanced sentiment analyzer with confidence scores, error handling, and logging
```

**Production-ready:**

```
Create a production-ready sentiment analyzer with full error handling, logging, configuration, tests, and documentation
```

### Specify Style

**Minimal:**

```
Create a minimal sentiment analyzer with no extra features
```

**Verbose:**

```
Create a sentiment analyzer with detailed comments and documentation
```

**Functional:**

```
Create a sentiment analyzer using functional programming style
```

### Specify Framework Integration

**With FastAPI:**

```
Create a sentiment analyzer with FastAPI endpoints
```

**With Streamlit:**

```
Create a sentiment analyzer with Streamlit UI
```

**With CLI:**

```
Create a sentiment analyzer with command-line interface
```

## Iterative Refinement

### Start Simple

```
→ Create a text classifier

  [Basic classifier generated]
```

### Add Features

```
→ Add confidence scores to the output

  [Updated with confidence field]
```

### Improve Quality

```
→ Use ChainOfThought instead of Predict

  [Updated with ChainOfThought]
```

### Add Error Handling

```
→ Add comprehensive error handling

  [Updated with try/except blocks]
```

### Add Documentation

```
→ Add detailed docstrings to all methods

  [Updated with documentation]
```

## Code Templates

### Industry Templates

Request industry-specific code:

```
Create a healthcare diagnosis assistant
Create a legal document analyzer
Create a financial sentiment analyzer
Create a customer support classifier
```

### Task Templates

Request task-specific code:

```
Create a question answering system
Create a summarization module
Create a translation module
Create a code generation module
```

### Pattern Templates

Request specific patterns:

```
Create a retrieval-augmented generation system
Create a multi-agent system
Create a self-improving system
Create a chain-of-thought reasoner
```

## Best Practices

### 1. Be Specific

**Good:**

```
Create a ChainOfThought module for email classification with subject, body, and sender as inputs, and category and priority as outputs
```

**Bad:**

```
Make email thing
```

### 2. Specify Reasoning

Choose appropriate predictor:

- Simple tasks → `Predict`
- Complex reasoning → `ChainOfThought`
- Multi-step → `ReAct`
- Code generation → `ProgramOfThought`

### 3. Include Examples

Help DSPy Code understand:

```
Create a classifier where:
- "urgent meeting tomorrow" → high priority
- "weekly newsletter" → low priority
- "project deadline" → high priority
```

### 4. Request Features

Be explicit about what you need:

```
Create a sentiment analyzer with:
- Confidence scores
- Error handling
- Logging
- Type hints
- Comprehensive documentation
```

### 5. Iterate

Refine through conversation:

```
→ Create classifier
→ Add feature X
→ Improve aspect Y
→ Fix issue Z
```

## Common Patterns

### Pattern 1: Classification

```
Create a [domain] classifier with [inputs] and [outputs]
```

### Pattern 2: Generation

```
Create a [content type] generator that takes [inputs] and produces [outputs]
```

### Pattern 3: RAG

```
Create a RAG system for [domain] that retrieves [data] and generates [output]
```

### Pattern 4: Multi-Step

```
Create a module that:
1. [Step 1]
2. [Step 2]
3. [Step 3]
```

### Pattern 5: Optimization

```
Create an optimizable [task] module with GEPA support
```

## Troubleshooting

### Generated Code Has Errors

**Validate first:**

```
/validate
```

**Ask for fixes:**

```
Fix the errors in the last generated code
```

### Wrong Predictor Type

**Specify explicitly:**

```
Use ChainOfThought instead of Predict
```

### Missing Features

**Request additions:**

```
Add [feature] to the last generated code
```

### Code Too Complex

**Simplify:**

```
Simplify the last generated code
Create a simpler version
```

### Code Too Simple

**Enhance:**

```
Make the code more robust
Add production-ready features
```

## Summary

Code generation supports:

- ✅ Signatures
- ✅ Modules
- ✅ Complete programs
- ✅ Multiple predictors
- ✅ Iterative refinement
- ✅ Industry templates
- ✅ Best practices

**Key tips:**

- Be specific in requests
- Choose appropriate predictors
- Include examples
- Iterate and refine
- Validate generated code

[Learn About Validation →](validation.md){ .md-button .md-button--primary }
[See Complete Examples →](../tutorials/sentiment-analyzer.md){ .md-button }
