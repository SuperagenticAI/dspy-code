# Build a RAG System

Learn how to build a Retrieval-Augmented Generation (RAG) system with DSPy Code.

---

## Overview

This tutorial will guide you through building a RAG system that can answer questions using retrieved context from a knowledge base.

---

## Step 1: Start DSPy Code

```bash
dspy-code
```

---

## Step 2: Initialize Project

```bash
/init
```

---

## Step 3: Connect to a Model

```bash
/connect ollama llama3.1:8b
# Or
/connect openai gpt-4o
```

---

## Step 4: Create the RAG System

Describe what you want to build:

```
Build a RAG system for question answering that retrieves relevant passages and generates answers
```

Or use the slash command:

```
/create program RAG question answering system with retrieval
```

---

## Step 5: Review Generated Code

DSPy Code will generate something like:

```python
import dspy

class RAGQA(dspy.Module):
    """Question answering with retrieval augmentation."""

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

---

## Step 6: Save the Code

```bash
/save rag_system.py
```

---

## Step 7: Set Up Retrieval

Configure your retrieval system:

```python
import dspy

# Configure your retrieval system
# For example, with a vector store:
from dspy.retrieve import ChromadbRM

retriever = ChromadbRM(
    collection_name="knowledge_base",
    persist_directory="./chroma_db"
)

# Update the RAG module to use your retriever
class RAGQA(dspy.Module):
    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = retriever
        self.generate_answer = dspy.ChainOfThought(
            "context, question -> reasoning -> answer"
        )

    def forward(self, question):
        passages = self.retrieve(question, k=num_passages)
        context = "\n\n".join([p.text for p in passages])
        return self.generate_answer(context=context, question=question)
```

---

## Step 8: Test the System

```bash
/run rag_system.py --input question="What is DSPy?"
```

---

## Step 9: Optimize (Optional)

Create training data:

```bash
/generate data 20 for question answering
```

Then optimize:

```bash
/optimize rag_system.py training_data.jsonl
```

---

## Complete Example

```python
import dspy
from dspy.retrieve import ChromadbRM

# Configure language model
lm = dspy.LM(model="ollama/llama3.1:8b")
dspy.configure(lm=lm)

# Set up retrieval
retriever = ChromadbRM(
    collection_name="knowledge_base",
    persist_directory="./chroma_db"
)

# Create RAG module
class RAGQA(dspy.Module):
    """Question answering with retrieval."""

    def __init__(self, num_passages=3):
        super().__init__()
        self.retrieve = retriever
        self.generate_answer = dspy.ChainOfThought(
            "context, question -> reasoning -> answer"
        )

    def forward(self, question):
        passages = self.retrieve(question, k=num_passages)
        context = "\n\n".join([p.text for p in passages])
        return self.generate_answer(context=context, question=question)

# Use the system
rag = RAGQA()
result = rag(question="What is DSPy?")
print(result.answer)
```

---

## Next Steps

- Add more sophisticated retrieval strategies
- Implement multi-hop reasoning
- Optimize with GEPA
- Deploy to production

---

**For more details, see [Optimization](../guide/optimization.md)**
