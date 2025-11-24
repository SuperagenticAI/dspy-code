# Optimize with GEPA

Learn how to optimize your DSPy programs using the Genetic Prompt Evolution Algorithm (GEPA).

---

## Overview

GEPA (Genetic Prompt Evolution Algorithm) is a powerful optimization technique that evolves prompts to improve your DSPy program's performance.

---

## Prerequisites

- A DSPy program to optimize
- Training data in JSONL format
- Connected language model

---

## Step 1: Create Your Program

First, create a DSPy program:

```bash
dspy-code
/init
/connect ollama llama3.1:8b
```

```
Create a sentiment analyzer module
```

```bash
/save sentiment_analyzer.py
```

---

## Step 2: Generate Training Data

Create training examples:

```bash
/generate data 50 for sentiment analysis
```

This creates a `training_data.jsonl` file with examples like:

```json
{"text": "I love this product!", "sentiment": "positive"}
{"text": "This is terrible.", "sentiment": "negative"}
```

---

## Step 3: Optimize with GEPA

```bash
/optimize sentiment_analyzer.py training_data.jsonl
```

---

## What Happens During Optimization

1. **Initialization** - GEPA creates an initial population of prompt variations
2. **Evaluation** - Each variation is tested on training data
3. **Selection** - Best-performing prompts are selected
4. **Evolution** - New prompts are created through mutation and crossover
5. **Iteration** - Process repeats for multiple generations
6. **Result** - Best prompt is returned

---

## Understanding the Output

```
Generation 1: Best fitness = 0.75
Generation 2: Best fitness = 0.82
Generation 3: Best fitness = 0.88
...
Final: Best fitness = 0.92
```

---

## Advanced Optimization

### Custom Metrics

Define your own metric:

```python
def my_metric(example, pred, trace=None):
    """Custom evaluation metric."""
    if pred.sentiment == example.sentiment:
        return 1.0
    return 0.0
```

### Optimization Parameters

```python
from gepa import GEPAOptimizer

optimizer = GEPAOptimizer(
    population_size=50,      # Larger population
    generations=20,          # More generations
    mutation_rate=0.15,      # Higher mutation
    crossover_rate=0.7       # Crossover probability
)
```

---

## Best Practices

1. **Quality Data** - Use high-quality training examples
2. **Sufficient Data** - At least 20-50 examples
3. **Diverse Examples** - Cover various cases
4. **Validation Set** - Keep some data for validation
5. **Patience** - Optimization takes time

---

## Example Workflow

```bash
# 1. Create program
dspy-code
> Create a sentiment analyzer

# 2. Save it
/save sentiment_analyzer.py

# 3. Generate training data
/generate data 50 for sentiment analysis

# 4. Optimize
/optimize sentiment_analyzer.py training_data.jsonl

# 5. Test optimized version
/run sentiment_analyzer_optimized.py --input text="This is great!"
```

---

## Troubleshooting

### Low Performance

- Check training data quality
- Increase number of examples
- Adjust optimization parameters
- Try different model

### Slow Optimization

- Reduce population size
- Reduce generations
- Use faster model
- Optimize on subset first

---

## Next Steps

- Evaluate on test set
- Deploy optimized program
- Monitor performance
- Iterate and improve

---

**For more details, see [Optimization](../guide/optimization.md)**
