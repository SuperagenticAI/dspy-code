# Question Answering System

Build a question answering system with DSPy Code.

---

## Overview

This tutorial shows you how to build a question answering system that can answer questions based on context.

---

## Step 1: Start and Initialize

```bash
dspy-code
/init
/connect ollama llama3.1:8b
```

---

## Step 2: Create the QA System

```
Create a question answering module that takes a question and context and generates an answer
```

---

## Step 3: Review Generated Code

```python
import dspy

class QuestionAnswering(dspy.Module):
    """Question answering module."""

    def __init__(self):
        super().__init__()
        self.answer = dspy.ChainOfThought(
            "context, question -> reasoning -> answer"
        )

    def forward(self, context, question):
        return self.answer(context=context, question=question)
```

---

## Step 4: Save and Test

```bash
/save qa_system.py
/run qa_system.py --input context="DSPy is a framework..." question="What is DSPy?"
```

---

## Complete Example

```python
import dspy

# Configure model
lm = dspy.LM(model="ollama/llama3.1:8b")
dspy.configure(lm=lm)

# Create QA module
class QuestionAnswering(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer = dspy.ChainOfThought(
            "context, question -> reasoning -> answer"
        )

    def forward(self, context, question):
        return self.answer(context=context, question=question)

# Use it
qa = QuestionAnswering()
result = qa(
    context="DSPy is a framework for building AI systems.",
    question="What is DSPy?"
)
print(result.answer)
```

---

## Enhancements

### Add Reasoning

```python
self.answer = dspy.ChainOfThought(
    "context, question -> reasoning -> answer"
)
```

### Add Confidence

```python
class QuestionAnswering(dspy.Module):
    def __init__(self):
        super().__init__()
        self.answer = dspy.ChainOfThought(
            "context, question -> reasoning -> answer, confidence"
        )
```

---

## Next Steps

- Add retrieval for RAG
- Optimize with GEPA
- Add evaluation metrics

---

**For more details, see [RAG System](rag-system.md)**
