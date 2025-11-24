# Optimization with GEPA

Learn how to optimize your DSPy programs using GEPA (Genetic Prompt Evolution Algorithm) for better performance.

## Quick Start with Natural Language

DSPy Code supports **natural language for optimization**! You don't need to remember command syntax - just describe what you want:

**Examples:**
- "optimize my program with GEPA"
- "improve performance of my_module.py"
- "run GEPA optimization with training_data.jsonl"
- "optimize the code"

DSPy Code automatically understands your intent and routes to the appropriate optimization command. See the [Natural Language Commands](../guide/natural-language-commands.md) guide for more examples.

## What is GEPA?

GEPA is a powerful optimization technique that automatically improves your DSPy programs by:

- **Evolving prompts**: Generates better instructions
- **Using reflection**: Learns from failures
- **Genetic algorithm**: Combines best approaches
- **Feedback-driven**: Uses detailed error analysis

**Result**: Significantly better accuracy without manual prompt engineering!

## How GEPA Works

### The GEPA Process

```
1. Evaluate Current Program
   ↓
2. Identify Failure Cases
   ↓
3. Generate Reflection (Why did it fail?)
   ↓
4. Evolve Better Prompts
   ↓
5. Test New Versions
   ↓
6. Select Best Performers
   ↓
7. Repeat (Genetic Evolution)
   ↓
8. Return Optimized Program
```

### Key Concepts

**1. Population:**

- GEPA maintains multiple program versions
- Each has different prompts/instructions
- Breadth parameter controls population size

**2. Evolution:**

- Successful versions are kept
- Failed versions are modified
- New variations are generated
- Best performers breed new versions

**3. Reflection:**

- Analyzes why predictions failed
- Generates specific feedback
- Uses feedback to improve prompts

**4. Selection:**

- Tests all versions on training data
- Ranks by performance
- Keeps top performers
- Eliminates poor performers

## Quick Start

### Step 1: Prepare Your Program

You need a DSPy program to optimize:

```python
import dspy

class SentimentSignature(dspy.Signature):
    """Analyze sentiment of text."""
    text = dspy.InputField(desc="Text to analyze")
    sentiment = dspy.OutputField(desc="positive, negative, or neutral")

class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(SentimentSignature)

    def forward(self, text):
        return self.predictor(text=text)
```

### Step 2: Generate Training Data

Create examples for optimization:

```
/generate data 50 for sentiment analysis
/save-data sentiment_examples.jsonl
```

**Example data format:**

```json
{"text": "I love this product!", "sentiment": "positive"}
{"text": "Terrible experience", "sentiment": "negative"}
{"text": "It's okay, nothing special", "sentiment": "neutral"}
```

### Step 3: Generate GEPA Script

Use DSPy Code to create optimization code:

```
/optimize sentiment_analyzer.py sentiment_examples.jsonl
```

DSPy Code generates a complete GEPA optimization script!

### Step 4: Run Optimization

Exit DSPy Code and run:

```bash
python generated/optimize_sentiment_analyzer.py
```

Watch GEPA improve your program!

## Understanding the Generated GEPA Script

### 1. Imports and Setup

```python
import dspy
from dspy.teleprompt import GEPA
from dspy.evaluate import Evaluate
import json
from pathlib import Path
```

### 2. Load Training Data

```python
def load_training_data(filepath):
    """Load training examples from JSONL."""
    examples = []
    with open(filepath, 'r') as f:
        for line in f:
            data = json.loads(line)
            example = dspy.Example(**data).with_inputs('text')
            examples.append(example)
    return examples
```

**Key points:**

- Loads from JSONL file
- Creates `dspy.Example` objects
- Marks input fields with `.with_inputs()`

### 3. Define Metric with Feedback

This is crucial for GEPA!

```python
def metric_with_feedback(gold, pred, trace=None):
    """
    Metric that provides feedback for GEPA.

    Returns:
        float: 1.0 for correct, 0.0 for incorrect
        OR
        dict: {'score': float, 'feedback': str} for detailed feedback
    """
    if gold.sentiment == pred.sentiment:
        return 1.0
    else:
        feedback = (
            f"Incorrect classification. "
            f"Expected '{gold.sentiment}' but got '{pred.sentiment}'. "
            f"Text: '{gold.text[:100]}...' "
            f"Consider the emotional tone and context more carefully."
        )
        return {'score': 0.0, 'feedback': feedback}
```

**Why feedback matters:**

- GEPA uses feedback to understand failures
- Specific feedback leads to better improvements
- Generic scores (0/1) are less effective

### 4. Configure GEPA

```python
# Load data
trainset = load_training_data('data/sentiment_examples.jsonl')

# Split into train and validation
train_size = int(0.8 * len(trainset))
train_examples = trainset[:train_size]
val_examples = trainset[train_size:]

# Configure GEPA
gepa_optimizer = GEPA(
    metric=metric_with_feedback,
    breadth=10,        # Population size
    depth=3,           # Evolution iterations
    init_temperature=1.4  # Creativity level
)
```

**Parameters explained:**

- **breadth**: How many program versions to maintain (10-20 typical)
- **depth**: How many evolution rounds (3-5 typical)
- **init_temperature**: Higher = more creative variations (1.0-2.0)

### 5. Run Optimization

```python
# Create unoptimized program
program = SentimentAnalyzer()

# Configure DSPy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-3.5-turbo"))

# Optimize!
optimized_program = gepa_optimizer.compile(
    program,
    trainset=train_examples,
    num_batches=10,
    max_bootstrapped_demos=3,
    max_labeled_demos=5
)
```

**Parameters explained:**

- **num_batches**: How many batches to process
- **max_bootstrapped_demos**: Examples to generate automatically
- **max_labeled_demos**: Your provided examples to use

### 6. Evaluate Results

```python
# Evaluate on validation set
evaluator = Evaluate(
    devset=val_examples,
    metric=metric_with_feedback,
    num_threads=4,
    display_progress=True
)

print("Evaluating unoptimized program...")
baseline_score = evaluator(program)

print("Evaluating optimized program...")
optimized_score = evaluator(optimized_program)

print(f"\nResults:")
print(f"Baseline: {baseline_score:.2%}")
print(f"Optimized: {optimized_score:.2%}")
print(f"Improvement: {(optimized_score - baseline_score):.2%}")
```

### 7. Save Optimized Program

```python
# Save the optimized program state
optimized_program.save('generated/sentiment_analyzer_optimized.json')

print("\nOptimized program saved!")
print("Load it with: program.load('generated/sentiment_analyzer_optimized.json')")
```

## Advanced GEPA Techniques

### Custom Metrics

Create task-specific metrics:

**For Classification:**

```python
def classification_metric_with_feedback(gold, pred, trace=None):
    correct = gold.category == pred.category

    if correct:
        return 1.0

    # Provide specific feedback
    feedback = f"Misclassified as '{pred.category}' instead of '{gold.category}'"

    # Add context
    if hasattr(gold, 'text'):
        feedback += f" for text: '{gold.text[:50]}...'"

    return {'score': 0.0, 'feedback': feedback}
```

**For Generation:**

```python
def generation_metric_with_feedback(gold, pred, trace=None):
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity

    # Semantic similarity
    model = SentenceTransformer('all-MiniLM-L6-v2')
    emb1 = model.encode([gold.answer])
    emb2 = model.encode([pred.answer])
    similarity = cosine_similarity(emb1, emb2)[0][0]

    if similarity > 0.85:
        return float(similarity)

    # Provide feedback for low similarity
    feedback = (
        f"Generated answer has low similarity ({similarity:.2f}). "
        f"Expected key points: {gold.answer[:100]}... "
        f"Generated: {pred.answer[:100]}... "
        f"Focus on including the main concepts."
    )

    return {'score': float(similarity), 'feedback': feedback}
```

**For Extraction:**

```python
def extraction_metric_with_feedback(gold, pred, trace=None):
    gold_entities = set(gold.entities)
    pred_entities = set(pred.entities)

    # F1 score
    if len(pred_entities) == 0:
        precision = 0
        recall = 0
    else:
        precision = len(gold_entities & pred_entities) / len(pred_entities)
        recall = len(gold_entities & pred_entities) / len(gold_entities)

    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * (precision * recall) / (precision + recall)

    if f1 > 0.8:
        return f1

    # Detailed feedback
    missed = gold_entities - pred_entities
    extra = pred_entities - gold_entities

    feedback = f"F1: {f1:.2f}. "
    if missed:
        feedback += f"Missed entities: {missed}. "
    if extra:
        feedback += f"Extra entities: {extra}. "

    return {'score': f1, 'feedback': feedback}
```

### Tuning GEPA Parameters

**For Small Datasets (<50 examples):**

```python
gepa_optimizer = GEPA(
    metric=metric_with_feedback,
    breadth=5,          # Smaller population
    depth=2,            # Fewer iterations
    init_temperature=1.2
)
```

**For Large Datasets (>500 examples):**

```python
gepa_optimizer = GEPA(
    metric=metric_with_feedback,
    breadth=20,         # Larger population
    depth=5,            # More iterations
    init_temperature=1.6
)
```

**For Complex Tasks:**

```python
gepa_optimizer = GEPA(
    metric=metric_with_feedback,
    breadth=15,
    depth=4,
    init_temperature=1.8,  # More creativity
    max_bootstrapped_demos=5,
    max_labeled_demos=10
)
```

### Multi-Stage Optimization

Optimize different parts separately:

```python
# Stage 1: Optimize retrieval
retrieval_optimizer = GEPA(
    metric=retrieval_metric,
    breadth=10,
    depth=3
)
optimized_retrieval = retrieval_optimizer.compile(
    retrieval_module,
    trainset=retrieval_examples
)

# Stage 2: Optimize generation
generation_optimizer = GEPA(
    metric=generation_metric,
    breadth=10,
    depth=3
)
optimized_generation = generation_optimizer.compile(
    generation_module,
    trainset=generation_examples
)

# Combine optimized components
class OptimizedRAG(dspy.Module):
    def __init__(self):
        self.retrieval = optimized_retrieval
        self.generation = optimized_generation

    def forward(self, question):
        context = self.retrieval(question=question)
        answer = self.generation(question=question, context=context)
        return answer
```

## GEPA Best Practices

### 1. Quality Training Data

**Good examples:**

- Diverse inputs
- Clear outputs
- Representative of real use
- Balanced across categories

**Bad examples:**

- All similar inputs
- Ambiguous outputs
- Edge cases only
- Imbalanced data

### 2. Informative Metrics

**Good feedback:**

```python
feedback = (
    f"Classified as '{pred.category}' instead of '{gold.category}'. "
    f"The text '{gold.text}' contains keywords like '{keywords}' "
    f"which strongly indicate '{gold.category}'. "
    f"Pay more attention to domain-specific terms."
)
```

**Bad feedback:**

```python
feedback = "Wrong answer"
```

### 3. Appropriate Parameters

**Start conservative:**

```python
breadth=10, depth=3
```

**Scale up if needed:**

```python
breadth=20, depth=5
```

**Don't over-optimize:**

- More iterations != better results
- Risk of overfitting
- Diminishing returns

### 4. Validation Split

Always keep validation data separate:

```python
# 80/20 split
train_size = int(0.8 * len(data))
train_data = data[:train_size]
val_data = data[train_size:]

# Optimize on train
optimized = gepa.compile(program, trainset=train_data)

# Evaluate on validation
score = evaluator(optimized, devset=val_data)
```

### 5. Monitor Progress

Track optimization progress:

```python
scores = []

def tracking_metric(gold, pred, trace=None):
    score = base_metric(gold, pred, trace)
    scores.append(score)
    return score

# After optimization
import matplotlib.pyplot as plt
plt.plot(scores)
plt.title('GEPA Optimization Progress')
plt.xlabel('Example')
plt.ylabel('Score')
plt.savefig('optimization_progress.png')
```

## Common Issues

### Low Improvement

**Possible causes:**

1. **Insufficient training data**
   - Solution: Generate more examples (50-100 minimum)

2. **Poor feedback in metric**
   - Solution: Add more specific feedback messages

3. **Task too simple**
   - Solution: Program may already be near-optimal

4. **Wrong predictor type**
   - Solution: Try ChainOfThought or ReAct

### Overfitting

**Symptoms:**

- High training score
- Low validation score
- Large gap between them

**Solutions:**

```python
# Reduce optimization intensity
gepa_optimizer = GEPA(
    breadth=5,   # Smaller
    depth=2      # Fewer iterations
)

# Use more training data
# Add regularization
# Simplify the task
```

### Slow Optimization

**Speed up GEPA:**

```python
# Reduce population and iterations
gepa_optimizer = GEPA(
    breadth=5,
    depth=2
)

# Use fewer examples per batch
optimized = gepa.compile(
    program,
    trainset=train_data,
    num_batches=5  # Fewer batches
)

# Use faster model for optimization
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-3.5-turbo"))
```

### Out of Memory

**Reduce memory usage:**

```python
# Smaller batches
optimized = gepa.compile(
    program,
    trainset=train_data,
    num_batches=20,  # More, smaller batches
    batch_size=5     # Smaller batch size
)

# Reduce population
gepa_optimizer = GEPA(breadth=5)

# Use fewer threads
evaluator = Evaluate(num_threads=1)
```

## Real-World Example

Complete optimization workflow:

```python
import dspy
from dspy.teleprompt import GEPA
from dspy.evaluate import Evaluate
import json

# 1. Define program
class EmailClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classify = dspy.ChainOfThought("email -> category")

    def forward(self, email):
        return self.classify(email=email)

# 2. Load data
def load_data(filepath):
    examples = []
    with open(filepath) as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(**data).with_inputs('email'))
    return examples

trainset = load_data('email_train.jsonl')
valset = load_data('email_val.jsonl')

# 3. Define metric
def email_metric(gold, pred, trace=None):
    if gold.category == pred.category:
        return 1.0

    feedback = (
        f"Misclassified email as '{pred.category}' instead of '{gold.category}'. "
        f"Email content: '{gold.email[:100]}...' "
        f"Look for keywords and patterns specific to '{gold.category}' category."
    )
    return {'score': 0.0, 'feedback': feedback}

# 4. Configure DSPy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-3.5-turbo"))

# 5. Optimize
gepa = GEPA(
    metric=email_metric,
    breadth=10,
    depth=3,
    init_temperature=1.4
)

program = EmailClassifier()
optimized_program = gepa.compile(
    program,
    trainset=trainset,
    num_batches=10
)

# 6. Evaluate
evaluator = Evaluate(devset=valset, metric=email_metric, num_threads=4)

baseline = evaluator(program)
optimized = evaluator(optimized_program)

print(f"Baseline: {baseline:.2%}")
print(f"Optimized: {optimized:.2%}")
print(f"Improvement: {(optimized - baseline):.2%}")

# 7. Save
optimized_program.save('email_classifier_optimized.json')
```

## Summary

GEPA optimization:

- ✅ Automatically improves DSPy programs
- ✅ Uses genetic evolution and reflection
- ✅ Requires training data and metrics
- ✅ Provides significant accuracy gains
- ✅ Works with any DSPy program

**Key takeaways:**

1. Prepare quality training data
2. Write informative metrics with feedback
3. Start with conservative parameters
4. Monitor and validate results
5. Save optimized programs

[Learn About Evaluation →](../tutorials/gepa-optimization.md){ .md-button .md-button--primary }
[See Complete Example →](../tutorials/gepa-optimization.md){ .md-button }
