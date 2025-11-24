# DSPy Evaluation Guide

Comprehensive evaluation framework for measuring and improving your DSPy programs. This guide covers all available metrics, evaluation strategies, and best practices.

## Quick Start with Natural Language

DSPy Code supports **natural language for evaluation**! You don't need to remember command syntax - just describe what you want:

**Examples:**
- "evaluate my program"
- "test performance with accuracy"
- "measure F1 score of my_module.py"
- "run evaluation on test_data.jsonl"
- "calculate metrics"

DSPy Code automatically understands your intent and routes to the appropriate evaluation command. See the [Natural Language Commands](../guide/natural-language-commands.md) guide for more examples.

## What is Evaluation?

Evaluation measures how well your DSPy program performs on your task. It helps you:

- **Measure Performance** - Understand current accuracy and quality
- **Compare Approaches** - Test different predictors, optimizers, or configurations
- **Track Progress** - Monitor improvements during optimization
- **Quality Assurance** - Ensure production readiness

## Available Metrics

DSPy Code supports a comprehensive set of evaluation metrics:

### Basic Metrics

#### Accuracy

Simple accuracy metric for classification tasks.

```python
def accuracy_metric(example, pred, trace=None):
    """Calculate accuracy."""
    predicted = pred.output.strip().lower()
    expected = example.output.strip().lower()
    return 1.0 if predicted == expected else 0.0
```

**When to use:**
- Classification tasks
- Exact match requirements
- Simple correctness checks

#### F1 Score

F1 score for classification tasks (harmonic mean of precision and recall).

```python
def f1_metric(example, pred, trace=None):
    """Calculate F1 score."""
    predicted = pred.output.strip().lower()
    expected = example.output.strip().lower()

    if predicted == expected:
        return 1.0  # Perfect precision and recall
    else:
        return 0.0  # Simplified - implement proper F1 for your task
```

**When to use:**
- Classification with multiple classes
- Need to balance precision and recall
- Imbalanced datasets

#### Precision & Recall

Precision and recall metrics for classification.

```python
def precision_metric(example, pred, trace=None):
    """Calculate precision."""
    # Implement based on your task
    pass

def recall_metric(example, pred, trace=None):
    """Calculate recall."""
    # Implement based on your task
    pass
```

**When to use:**
- Binary classification
- Need separate precision/recall scores
- Understanding false positives/negatives

#### Exact Match

Exact match metric for question answering tasks.

```python
def exact_match_metric(example, pred, trace=None):
    """Exact match metric for QA."""
    predicted = pred.output.strip()
    expected = example.output.strip()
    return 1.0 if predicted == expected else 0.0
```

**When to use:**
- Question answering
- Factual extraction
- Short answer tasks

### Advanced Metrics

#### Answer Correctness

Answer correctness for QA tasks with partial credit.

```python
def answer_correctness_metric(example, pred, trace=None):
    """Answer correctness for QA tasks."""
    predicted = pred.answer.strip().lower() if hasattr(pred, 'answer') else pred.output.strip().lower()
    expected = example.answer.strip().lower() if hasattr(example, 'answer') else example.output.strip().lower()

    # Check exact match
    if predicted == expected:
        return 1.0

    # Check if answer contains expected key terms
    expected_terms = set(expected.split())
    predicted_terms = set(predicted.split())
    overlap = len(expected_terms & predicted_terms)

    if len(expected_terms) > 0:
        return overlap / len(expected_terms)
    return 0.0
```

**When to use:**
- Question answering with partial credit
- Flexible answer formats
- Key term matching

#### Context Relevance

Context relevance for RAG tasks.

```python
def context_relevance_metric(example, pred, trace=None):
    """Context relevance for RAG tasks."""
    question = example.question if hasattr(example, 'question') else example.input_text
    context = pred.context if hasattr(pred, 'context') else ""

    if not context:
        return 0.0

    # Simple relevance: check keyword overlap
    question_words = set(question.lower().split())
    context_words = set(context.lower().split())
    overlap = len(question_words & context_words)

    if len(question_words) > 0:
        return min(overlap / len(question_words), 1.0)
    return 0.0
```

**When to use:**
- RAG systems
- Measuring retrieval quality
- Context quality assessment

#### Faithfulness

Faithfulness: answer is grounded in context.

```python
def faithfulness_metric(example, pred, trace=None):
    """Faithfulness: answer is grounded in context."""
    answer = pred.answer if hasattr(pred, 'answer') else pred.output
    context = pred.context if hasattr(pred, 'context') else ""

    if not context or not answer:
        return 0.0

    # Check if answer terms appear in context
    answer_words = set(answer.lower().split())
    context_words = set(context.lower().split())
    overlap = len(answer_words & context_words)

    if len(answer_words) > 0:
        return overlap / len(answer_words)
    return 0.0
```

**When to use:**
- RAG systems
- Measuring hallucination
- Grounding verification

#### ROUGE Score

ROUGE score for summarization tasks.

```python
def rouge_metric(example, pred, trace=None):
    """ROUGE score for summarization tasks."""
    try:
        from rouge_score import rouge_scorer
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

        predicted = pred.output if hasattr(pred, 'output') else str(pred)
        expected = example.output if hasattr(example, 'output') else str(example)

        scores = scorer.score(expected, predicted)
        # Return average of ROUGE-1, ROUGE-2, ROUGE-L F1 scores
        return (scores['rouge1'].fmeasure + scores['rouge2'].fmeasure + scores['rougeL'].fmeasure) / 3.0
    except ImportError:
        print("⚠️  rouge-score not installed: pip install rouge-score")
        return 0.0
```

**When to use:**
- Summarization tasks
- Text generation
- Content overlap measurement

#### BLEU Score

BLEU score for generation tasks.

```python
def bleu_metric(example, pred, trace=None):
    """BLEU score for generation tasks."""
    try:
        from nltk.translate.bleu_score import sentence_bleu

        predicted = pred.output.split() if hasattr(pred, 'output') else str(pred).split()
        expected = example.output.split() if hasattr(example, 'output') else str(example).split()

        return sentence_bleu([expected], predicted)
    except ImportError:
        print("⚠️  nltk not installed: pip install nltk")
        return 0.0
```

**When to use:**
- Text generation
- Machine translation
- Sequence-to-sequence tasks

#### Semantic Similarity

Semantic similarity using embeddings.

```python
def semantic_similarity_metric(example, pred, trace=None):
    """Semantic similarity using embeddings."""
    try:
        from sentence_transformers import SentenceTransformer
        import numpy as np

        model = SentenceTransformer('all-MiniLM-L6-v2')

        predicted = pred.output if hasattr(pred, 'output') else str(pred)
        expected = example.output if hasattr(example, 'output') else str(example)

        embeddings = model.encode([predicted, expected])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
    except ImportError:
        print("⚠️  sentence-transformers not installed: pip install sentence-transformers")
        return 0.0
```

**When to use:**
- Semantic similarity tasks
- Flexible answer formats
- Meaning-based evaluation

## Running Evaluation

### Basic Evaluation

```python
import dspy
from dspy.evaluate import Evaluate

# Your program
program = YourModule()

# Test dataset
testset = [
    dspy.Example(input="...", output="...").with_inputs("input"),
    # ... more examples
]

# Metric function
def accuracy_metric(example, pred, trace=None):
    return 1.0 if pred.output == example.output else 0.0

# Run evaluation
evaluator = Evaluate(
    devset=testset,
    metric=accuracy_metric,
    num_threads=4,
    display_progress=True
)

score = evaluator(program)
print(f"Accuracy: {score:.2%}")
```

### Multiple Metrics

```python
# Define multiple metrics
def accuracy_metric(example, pred, trace=None):
    return 1.0 if pred.output == example.output else 0.0

def semantic_similarity_metric(example, pred, trace=None):
    # ... implementation
    return similarity_score

# Evaluate with each metric
accuracy = Evaluate(devset=testset, metric=accuracy_metric)(program)
similarity = Evaluate(devset=testset, metric=semantic_similarity_metric)(program)

print(f"Accuracy: {accuracy:.2%}")
print(f"Semantic Similarity: {similarity:.2%}")
```

### Using DSPy Code CLI

Generate evaluation code:

```bash
/eval                    # Generate evaluation with accuracy metric
/eval list               # List all available metrics
/eval accuracy f1        # Use multiple metrics
/eval context_relevance  # Use RAG-specific metrics
```

## Evaluation Best Practices

### 1. Test Dataset

- **Size**: Use 20-50 examples minimum for reliable results
- **Distribution**: Match real-world data distribution
- **Quality**: Ensure high-quality ground truth labels
- **Diversity**: Cover different cases and edge cases

### 2. Metric Selection

- **Task-appropriate**: Choose metrics that match your task
- **Multiple metrics**: Use 2-3 metrics to avoid overfitting
- **Baseline comparison**: Compare against baseline or previous versions
- **Domain-specific**: Consider custom metrics for your domain

### 3. Evaluation Workflow

1. **Initial evaluation** - Establish baseline performance
2. **Optimization** - Improve program with optimizers
3. **Re-evaluation** - Measure improvements
4. **Iteration** - Repeat until performance is acceptable

### 4. Interpreting Results

- **Score ranges**: Understand what scores mean for your task
- **Error analysis**: Analyze failures to identify patterns
- **Confidence intervals**: Consider statistical significance
- **Trade-offs**: Balance different metrics (e.g., accuracy vs. speed)

## Evaluation Report

DSPy Code generates comprehensive evaluation reports:

```
Evaluation Results
======================================================================

Metric                    Score           Status
----------------------------------------------------------------------
accuracy                  85.00%          ✓ Pass
f1                        82.50%          ✓ Pass
context_relevance         75.00%          ⚠️  Needs Improvement
faithfulness              90.00%          ✓ Pass
----------------------------------------------------------------------
Average                   83.13%

Analysis
======================================================================
Total examples evaluated: 50
Metrics computed: 4

Best performing metric: faithfulness (90.00%)
Worst performing metric: context_relevance (75.00%)
```

## Custom Metrics

Create custom metrics for your specific needs:

```python
def custom_metric(example, pred, trace=None):
    """Custom metric - implement your own logic."""
    predicted = pred.output
    expected = example.output

    # Your custom scoring logic
    score = 0.0

    # Example: Check if key terms are present
    key_terms = expected.split()
    found_terms = sum(1 for term in key_terms if term in predicted)

    if len(key_terms) > 0:
        score = found_terms / len(key_terms)

    return score
```

## Troubleshooting

### Low Scores

- **Check data quality**: Ensure test data is correct
- **Review metric**: Verify metric implementation
- **Analyze failures**: Look at specific failure cases
- **Baseline comparison**: Compare against simple baseline

### Inconsistent Results

- **Larger test set**: Use more examples
- **Multiple runs**: Average over multiple runs
- **Stability**: Check for non-deterministic behavior
- **Data distribution**: Ensure representative test set

### Metric Issues

- **Import errors**: Install required packages (rouge-score, nltk, sentence-transformers)
- **Type errors**: Ensure metric returns float (0.0-1.0)
- **Attribute errors**: Check field names match your signature

## Next Steps

- Learn about [Optimization](optimization.md) to improve performance
- Explore [RAG Systems](../tutorials/rag-system.md) for RAG-specific metrics
- Check [Validation](validation.md) for code quality checks
- See [Complete Programs](../tutorials/sentiment-analyzer.md) for full examples

## Additional Resources

- [DSPy Evaluation Documentation](https://dspy-docs.vercel.app/docs/building-blocks/metrics)
- Use `/eval list` in the CLI to see all available metrics
- Use `/eval <metric>` to generate evaluation code
