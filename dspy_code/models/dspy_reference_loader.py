"""
DSPy Reference Documentation Loader.

Loads DSPy reference code and documentation to provide context
for intelligent code generation.
"""

from pathlib import Path

from ..core.logging import get_logger

logger = get_logger(__name__)


class DSPyReferenceLoader:
    """
    Loads and indexes DSPy reference documentation and code examples.

    This provides the LLM with accurate DSPy patterns and examples
    to generate correct code.
    """

    def __init__(self, reference_dir: Path | None = None):
        """
        Initialize the reference loader.

        All documentation is embedded in the class methods, so no external
        reference directory is needed.

        Args:
            reference_dir: Optional path to additional reference files (not used by default)
        """
        # Reference directory is optional and not used by default
        # All documentation is embedded in the class methods
        self.reference_dir = Path(reference_dir) if reference_dir else None
        self.reference_cache = {}
        self.examples_cache = {}

    def load_reference(self) -> str:
        """
        Load all DSPy reference documentation.

        Returns:
            Formatted reference documentation string
        """
        if self.reference_cache:
            return self.reference_cache.get("full_reference", "")

        reference_parts = []

        # Load core concepts
        reference_parts.append(self._load_core_concepts())

        # Load signature examples
        reference_parts.append(self._load_signature_examples())

        # Load module examples
        reference_parts.append(self._load_module_examples())

        # Load optimization examples
        reference_parts.append(self._load_optimization_examples())

        full_reference = "\n\n".join(filter(None, reference_parts))
        self.reference_cache["full_reference"] = full_reference

        return full_reference

    def _load_core_concepts(self) -> str:
        """Load DSPy core concepts."""
        return """
# DSPy Core Concepts

## Signatures
Signatures define the input-output specification for a task.

```python
import dspy

class MySignature(dspy.Signature):
    \"\"\"Description of what this signature does.\"\"\"

    input_field = dspy.InputField(desc="Description of input")
    output_field = dspy.OutputField(desc="Description of output")
```

## Modules
Modules implement the logic using signatures and predictors.

```python
class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(MySignature)

    def forward(self, input_field):
        return self.predictor(input_field=input_field)
```

## Reasoning Patterns

### Predict (Fast, Direct)
```python
self.predictor = dspy.Predict(MySignature)
```

### Chain of Thought (Reasoning)
```python
self.predictor = dspy.ChainOfThought(MySignature)
```

### ReAct (Tool Usage)
```python
self.predictor = dspy.ReAct(MySignature)
```
"""

    def _load_signature_examples(self) -> str:
        """Load signature examples from reference directory."""
        examples = []

        # Common signature patterns
        examples.append("""
# Signature Examples

## Classification
```python
class TextClassification(dspy.Signature):
    \"\"\"Classify text into categories.\"\"\"
    text = dspy.InputField(desc="Text to classify")
    category = dspy.OutputField(desc="Classification category")
```

## Generation
```python
class TextGeneration(dspy.Signature):
    \"\"\"Generate text based on input.\"\"\"
    prompt = dspy.InputField(desc="Generation prompt")
    generated_text = dspy.OutputField(desc="Generated text")
```

## Question Answering
```python
class QuestionAnswering(dspy.Signature):
    \"\"\"Answer questions based on context.\"\"\"
    question = dspy.InputField(desc="The question to answer")
    context = dspy.InputField(desc="Context or document")
    answer = dspy.OutputField(desc="The answer")
```

## Sentiment Analysis
```python
class SentimentAnalysis(dspy.Signature):
    \"\"\"Analyze sentiment of text.\"\"\"
    text = dspy.InputField(desc="Text to analyze")
    sentiment = dspy.OutputField(desc="positive, negative, or neutral")
    confidence = dspy.OutputField(desc="Confidence score 0-1")
```
""")

        return "\n".join(examples)

    def _load_module_examples(self) -> str:
        """Load module examples."""
        return """
# Module Examples

## Basic Classifier
```python
class TextClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classifier = dspy.Predict(TextClassification)

    def forward(self, text):
        return self.classifier(text=text)
```

## Chain of Thought Analyzer
```python
class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.analyzer = dspy.ChainOfThought(SentimentAnalysis)

    def forward(self, text):
        result = self.analyzer(text=text)
        return result
```

## Multi-Step Pipeline
```python
class MultiStepPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.step1 = dspy.ChainOfThought(Step1Signature)
        self.step2 = dspy.ChainOfThought(Step2Signature)

    def forward(self, input_data):
        result1 = self.step1(input_data=input_data)
        result2 = self.step2(intermediate=result1.output)
        return result2
```
"""

    def _load_optimization_examples(self) -> str:
        """Load optimization examples."""
        return """
# Optimization with GEPA

## Basic Optimization
```python
from dspy.teleprompt import BootstrapFewShot

# Define metric
def accuracy_metric(example, prediction, trace=None):
    return float(prediction.output == example.output)

# Create optimizer
optimizer = BootstrapFewShot(
    metric=accuracy_metric,
    max_bootstrapped_demos=3
)

# Optimize module
optimized_module = optimizer.compile(
    my_module,
    trainset=training_examples
)
```

## Training Examples Format
```python
import dspy

examples = [
    dspy.Example(
        input_field="example input",
        output_field="expected output"
    ).with_inputs("input_field"),
    # More examples...
]
```
"""

    def get_relevant_examples(self, intent: str) -> str:
        """
        Get relevant examples based on user intent.

        Args:
            intent: User's intent (e.g., "create_signature", "create_module")

        Returns:
            Relevant examples
        """
        if intent == "create_signature":
            return self._load_signature_examples()
        elif intent == "create_module":
            return self._load_module_examples()
        elif intent == "optimize":
            return self._load_optimization_examples()
        else:
            return self._load_core_concepts()

    def search_reference(self, query: str) -> str:
        """
        Search reference documentation for specific topics.

        Args:
            query: Search query

        Returns:
            Relevant documentation
        """
        query_lower = query.lower()

        # Simple keyword matching
        if "signature" in query_lower:
            return self._load_signature_examples()
        elif "module" in query_lower:
            return self._load_module_examples()
        elif "optimize" in query_lower or "gepa" in query_lower:
            return self._load_optimization_examples()
        elif "chain of thought" in query_lower or "cot" in query_lower:
            return """
# Chain of Thought

Chain of Thought prompting encourages step-by-step reasoning.

```python
self.predictor = dspy.ChainOfThought(MySignature)
```

Use when:
- Complex reasoning required
- Need explainable results
- Multi-step problems
"""
        elif "react" in query_lower:
            return """
# ReAct (Reasoning + Acting)

ReAct combines reasoning with tool usage.

```python
self.predictor = dspy.ReAct(MySignature)
```

Use when:
- Need to use external tools
- Require dynamic information gathering
- Multi-step processes with actions
"""
        else:
            return self._load_core_concepts()
