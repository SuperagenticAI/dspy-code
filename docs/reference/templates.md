# Templates Reference

DSPy Code includes templates for common DSPy patterns and use cases.

---

## Overview

Templates provide pre-built structures for:
- DSPy Signatures
- DSPy Modules
- Complete Programs
- Optimizers
- Evaluation Scripts

---

## Signature Templates

### Basic Signature

```python
class BasicSignature(dspy.Signature):
    """Basic signature template."""
    input: str = dspy.InputField(desc="Input description")
    output: str = dspy.OutputField(desc="Output description")
```

### Multi-Input Signature

```python
class MultiInputSignature(dspy.Signature):
    """Signature with multiple inputs."""
    input1: str = dspy.InputField(desc="First input")
    input2: str = dspy.InputField(desc="Second input")
    output: str = dspy.OutputField(desc="Output")
```

### Classification Signature

```python
class ClassificationSignature(dspy.Signature):
    """Classification task signature."""
    text: str = dspy.InputField(desc="Text to classify")
    category: str = dspy.OutputField(desc="Classification category")
```

---

## Module Templates

### Predict Module

```python
class PredictModule(dspy.Module):
    """Basic prediction module."""
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(BasicSignature)

    def forward(self, input):
        return self.predictor(input=input)
```

### ChainOfThought Module

```python
class ChainOfThoughtModule(dspy.Module):
    """Chain of thought reasoning module."""
    def __init__(self):
        super().__init__()
        self.generate_answer = dspy.ChainOfThought("question -> reasoning -> answer")

    def forward(self, question):
        return self.generate_answer(question=question)
```

### ReAct Module

```python
class ReActModule(dspy.Module):
    """ReAct (Reasoning + Acting) module."""
    def __init__(self):
        super().__init__()
        self.react = dspy.ReAct("question -> thought, action, observation -> answer")

    def forward(self, question):
        return self.react(question=question)
```

### Multi-Step Module

```python
class MultiStepModule(dspy.Module):
    """Module with multiple reasoning steps."""
    def __init__(self):
        super().__init__()
        self.step1 = dspy.ChainOfThought("input -> intermediate")
        self.step2 = dspy.ChainOfThought("intermediate -> output")

    def forward(self, input):
        intermediate = self.step1(input=input)
        return self.step2(intermediate=intermediate.intermediate)
```

---

## Complete Program Templates

### Sentiment Analyzer

```python
import dspy

class SentimentAnalyzer(dspy.Module):
    """Sentiment analysis program."""
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(
            "text -> reasoning -> sentiment"
        )

    def forward(self, text):
        return self.classify(text=text)

# Usage
lm = dspy.LM(model="ollama/llama3.1:8b")
dspy.configure(lm=lm)

analyzer = SentimentAnalyzer()
result = analyzer(text="I love this product!")
print(result.sentiment)
```

### Question Answering with RAG

```python
import dspy

class RAGQA(dspy.Module):
    """Question answering with retrieval."""
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=num_passages)
        self.generate_answer = dspy.ChainOfThought(
            "context, question -> reasoning -> answer"
        )

    def forward(self, question):
        passages = self.retrieve(question)
        context = "\n\n".join([p.text for p in passages])
        return self.generate_answer(context=context, question=question)
```

### Email Classifier

```python
import dspy

class EmailClassifier(dspy.Module):
    """Email classification program."""
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought(
            "subject, body -> reasoning -> category, priority"
        )

    def forward(self, subject, body):
        return self.classify(subject=subject, body=body)
```

---

## Optimizer Templates

### Bootstrap Finetune

```python
from dspy.teleprompt import BootstrapFinetune

teleprompter = BootstrapFinetune(
    metric=my_metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=16
)

optimized_program = teleprompter.compile(
    student=my_program,
    trainset=training_data
)
```

### MIPRO

```python
from dspy.teleprompt import MIPRO

teleprompter = MIPRO(
    metric=my_metric,
    num_candidates=10
)

optimized_program = teleprompter.compile(
    student=my_program,
    trainset=training_data
)
```

### GEPA

```python
from gepa import GEPAOptimizer

optimizer = GEPAOptimizer(
    population_size=50,
    generations=10,
    mutation_rate=0.1
)

optimized_program = optimizer.optimize(
    program=my_program,
    training_data=training_data,
    metric=my_metric
)
```

---

## Evaluation Templates

### Basic Evaluation

```python
import dspy

def evaluate(program, testset):
    """Basic evaluation function."""
    correct = 0
    total = len(testset)

    for example in testset:
        prediction = program(**example.inputs)
        if prediction.answer == example.outputs.answer:
            correct += 1

    accuracy = correct / total
    return {"accuracy": accuracy, "correct": correct, "total": total}
```

### Metric Function

```python
def my_metric(example, pred, trace=None):
    """Custom metric function."""
    # Compare prediction with expected output
    if pred.answer.lower() == example.answer.lower():
        return 1.0
    return 0.0
```

---

## Industry Templates

DSPy Code includes templates for common industry use cases:

### Customer Support

- Ticket classification
- Response generation
- Sentiment analysis

### Content Moderation

- Toxicity detection
- Spam classification
- Content categorization

### E-commerce

- Product recommendation
- Review analysis
- Search query understanding

### Healthcare

- Symptom analysis
- Medical Q&A
- Report summarization

---

## Using Templates

### Generate from Template

```bash
dspy-code
> Create a sentiment analyzer module
```

DSPy Code will generate code based on templates.

### Custom Templates

You can create custom templates by:

1. Saving your module to `templates/` directory
2. Using it as a reference for generation
3. Sharing with the community

---

## Template Best Practices

1. **Start Simple** - Begin with basic templates
2. **Iterate** - Refine based on your needs
3. **Optimize** - Use GEPA for production
4. **Evaluate** - Test with your data
5. **Document** - Add docstrings and comments

---

## Accessing Templates

Templates are available in:

- **Code Generation** - DSPy Code uses templates when generating code
- **Examples** - See `examples/` directory
- **Source** - `dspy_code/templates/` directory

---

**For more details, see [Generating Code](../guide/generating-code.md)**
