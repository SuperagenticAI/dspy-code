# Custom Modules

Learn how to create and use custom DSPy modules in DSPy Code.

---

## Overview

Custom modules allow you to build specialized DSPy components tailored to your specific use case. DSPy Code can help you generate, validate, and optimize custom modules.

---

## Module Structure

A basic DSPy module follows this structure:

```python
import dspy

class MyCustomModule(dspy.Module):
    """Description of your custom module."""

    def __init__(self):
        super().__init__()
        # Initialize your predictors, retrievers, etc.
        self.predictor = dspy.Predict("input -> output")

    def forward(self, input):
        """Forward pass through the module."""
        result = self.predictor(input=input)
        return result
```

---

## Creating Custom Modules

### Using DSPy Code

**Natural Language:**
```
dspy-code
> Create a custom module for document summarization with title and summary outputs
```

**Slash Command:**
```
/create module document summarizer with text input and title, summary outputs
```

### Manual Creation

1. **Define the Signature:**
```python
class SummarizationSignature(dspy.Signature):
    """Summarize a document."""
    document: str = dspy.InputField(desc="Document to summarize")
    title: str = dspy.OutputField(desc="Document title")
    summary: str = dspy.OutputField(desc="Document summary")
```

2. **Create the Module:**
```python
class DocumentSummarizer(dspy.Module):
    """Document summarization module."""
    def __init__(self):
        super().__init__()
        self.summarize = dspy.ChainOfThought(SummarizationSignature)

    def forward(self, document):
        return self.summarize(document=document)
```

---

## Advanced Patterns

### Multi-Step Reasoning

```python
class MultiStepReasoning(dspy.Module):
    """Module with multiple reasoning steps."""
    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought("input -> analysis")
        self.synthesize = dspy.ChainOfThought("analysis -> conclusion")

    def forward(self, input):
        analysis = self.analyze(input=input)
        conclusion = self.synthesize(analysis=analysis.analysis)
        return conclusion
```

### Retrieval-Augmented

```python
class RAGModule(dspy.Module):
    """Module with retrieval augmentation."""
    def __init__(self, k=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=k)
        self.answer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        passages = self.retrieve(question)
        context = "\n\n".join([p.text for p in passages])
        return self.answer(context=context, question=question)
```

### Tool-Using Modules

```python
class ToolUsingModule(dspy.Module):
    """Module that uses external tools."""
    def __init__(self):
        super().__init__()
        self.react = dspy.ReAct("task -> thought, action, observation -> result")

    def forward(self, task):
        # ReAct automatically handles tool usage
        return self.react(task=task)
```

### Conditional Logic

```python
class ConditionalModule(dspy.Module):
    """Module with conditional logic."""
    def __init__(self):
        super().__init__()
        self.classify = dspy.Predict("input -> category")
        self.process_a = dspy.ChainOfThought("input -> output")
        self.process_b = dspy.ChainOfThought("input -> output")

    def forward(self, input):
        category = self.classify(input=input)

        if category.category == "type_a":
            return self.process_a(input=input)
        else:
            return self.process_b(input=input)
```

---

## Module Composition

### Sequential Composition

```python
class Pipeline(dspy.Module):
    """Compose multiple modules sequentially."""
    def __init__(self):
        super().__init__()
        self.step1 = Module1()
        self.step2 = Module2()
        self.step3 = Module3()

    def forward(self, input):
        result1 = self.step1(input)
        result2 = self.step2(result1)
        result3 = self.step3(result2)
        return result3
```

### Parallel Composition

```python
class ParallelModule(dspy.Module):
    """Run multiple modules in parallel."""
    def __init__(self):
        super().__init__()
        self.branch_a = ModuleA()
        self.branch_b = ModuleB()
        self.merge = dspy.ChainOfThought("result_a, result_b -> merged")

    def forward(self, input):
        result_a = self.branch_a(input)
        result_b = self.branch_b(input)
        return self.merge(result_a=result_a, result_b=result_b)
```

---

## Using Custom Modules

### Save Your Module

```bash
dspy-code
> /save my_custom_module.py
```

### Import and Use

```python
from my_custom_module import MyCustomModule

module = MyCustomModule()
result = module(input="your input here")
```

### Validate

```bash
dspy-code
> /validate my_custom_module.py
```

---

## Optimization

### Optimize Custom Modules

```bash
dspy-code
> /optimize my_custom_module.py training_data.jsonl
```

### Custom Metrics

```python
def my_custom_metric(example, pred, trace=None):
    """Define your custom metric."""
    # Your evaluation logic
    score = calculate_score(example, pred)
    return score
```

---

## Best Practices

1. **Clear Signatures** - Define clear input/output fields
2. **Documentation** - Add docstrings to all modules
3. **Type Hints** - Use type hints for better IDE support
4. **Testing** - Test modules with sample inputs
5. **Validation** - Use `/validate` before optimization
6. **Versioning** - Track module versions
7. **Reusability** - Design modules to be reusable

---

## Integration with DSPy Code

### Generate from Description

```
Create a module for [your use case] with [inputs] and [outputs]
```

### Validate Before Use

```
/validate my_module.py
```

### Optimize for Production

```
/optimize my_module.py training_data.jsonl
```

### Export for Sharing

```
/export my_module.py
```

---

## Examples

See the `examples/` directory for complete custom module examples:

- Email classifier
- Document analyzer
- Multi-agent systems
- Tool-using agents

---

## Troubleshooting

### Module Not Found

Ensure your module is in the Python path or current directory.

### Import Errors

Check that all dependencies are installed:
```bash
pip install dspy
```

### Validation Errors

Use `/validate` to check for common issues:
- Missing signatures
- Incorrect field types
- Import problems

---

**For more details, see [Generating Code](../guide/generating-code.md) and [Optimization](../guide/optimization.md)**
