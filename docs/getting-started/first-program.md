# Your First DSPy Program

Build a complete DSPy program from scratch in this detailed tutorial.

## What You'll Build

A **text classifier** that categorizes customer feedback into categories: bug report, feature request, or question.

**Time**: 20 minutes

## Prerequisites

- DSPy Code installed
- Basic Python knowledge
- (Optional) Ollama or OpenAI API key

## Step 1: Start DSPy Code

Open your terminal:

```bash
dspy-code
```

You'll see the welcome screen with your DSPy version.

## Step 2: Initialize Your Project

Create a new project:

```
/init
```

**What happens:**

- Creates `dspy_config.yaml`
- Sets up project directories
- Indexes your DSPy installation
- Shows entertaining messages!

!!! tip "Project Structure Created"
    ```
    my-project/
    ├── dspy_config.yaml
    ├── generated/
    ├── data/
    └── .cache/
    ```

## Step 3: Connect to a Model

For better results, connect to a model:

```
/connect ollama llama3.1:8b
```

!!! info "Without a Model?"
    You can still use DSPy Code with templates. The code will be more generic but functional.

## Step 4: Describe Your Program

Use natural language to describe what you want:

```
Create a text classifier that takes customer feedback and categorizes it as bug report, feature request, or question
```

DSPy Code will generate complete code!

## Step 5: Understanding the Generated Code

Let's break down what was created:

### The Signature

```python
import dspy

class FeedbackClassifier(dspy.Signature):
    """Classify customer feedback into categories."""

    feedback: str = dspy.InputField(
        desc="Customer feedback text"
    )
    category: str = dspy.OutputField(
        desc="bug_report, feature_request, or question"
    )
```

**What this does:**

- **InputField**: Defines what goes into the model
- **OutputField**: Defines what comes out
- **Descriptions**: Help the LLM understand the task

### The Module

```python
class FeedbackClassifierModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.classifier = dspy.ChainOfThought(FeedbackClassifier)

    def forward(self, feedback):
        result = self.classifier(feedback=feedback)
        return result
```

**What this does:**

- **dspy.Module**: Base class for all DSPy programs
- **ChainOfThought**: Uses reasoning to improve accuracy
- **forward()**: The main execution method

### Configuration and Usage

```python
# Configure DSPy
import dspy
dspy.settings.configure(
    lm=dspy.OpenAI(model="gpt-3.5-turbo")
)

# Create and use the classifier
classifier = FeedbackClassifierModule()

# Test it
result = classifier(feedback="The app crashes when I click save")
print(result.category)  # Output: bug_report

result = classifier(feedback="Can you add dark mode?")
print(result.category)  # Output: feature_request

result = classifier(feedback="How do I export my data?")
print(result.category)  # Output: question
```

## Step 6: Save Your Program

Save the generated code:

```
/save feedback_classifier.py
```

File saved to `generated/feedback_classifier.py`

## Step 7: Validate the Code

Check for issues:

```
/validate
```

**The validator checks:**

- ✅ Signature structure
- ✅ InputField and OutputField usage
- ✅ Module inheritance
- ✅ forward() method implementation
- ✅ Best practices

!!! success "Validation Passed"
    ```
    ✓ Signature is correctly defined
    ✓ Module inherits from dspy.Module
    ✓ forward() method is implemented
    ✓ No issues found

    Quality Score: 95/100
    ```

## Step 8: Test Your Program

Run it in the sandbox:

```
/run
```

DSPy Code executes your code safely and shows results.

## Step 9: Create Test Data

Generate test examples:

```
Generate 10 examples for feedback classification with diverse customer messages
```

**Generated examples:**

```json
{"feedback": "App crashes on startup", "category": "bug_report"}
{"feedback": "Please add export to PDF", "category": "feature_request"}
{"feedback": "How do I reset my password?", "category": "question"}
...
```

Save the data:

```
/save-data feedback_examples.jsonl
```

## Step 10: Evaluate Your Classifier

Create an evaluation script:

```
/eval
```

**Generated evaluation code:**

```python
import dspy
from dspy.evaluate import Evaluate

# Load test data
def load_test_data():
    examples = []
    with open('data/feedback_examples.jsonl') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(**data).with_inputs('feedback'))
    return examples

# Define metric
def accuracy_metric(example, prediction, trace=None):
    return example.category == prediction.category

# Evaluate
evaluator = Evaluate(
    devset=load_test_data(),
    metric=accuracy_metric,
    num_threads=4
)

classifier = FeedbackClassifierModule()
score = evaluator(classifier)
print(f"Accuracy: {score}")
```

Save it:

```
/save evaluate_classifier.py
```

## Step 11: Optimize with GEPA

Generate GEPA optimization code:

```
/optimize
```

This creates a complete GEPA optimization script!

**What's included:**

- Metric with feedback for GEPA
- Training data loader
- GEPA configuration
- Optimization execution

Save it:

```
/save optimize_classifier.py
```

## Step 12: Run Optimization

Exit DSPy Code and run:

```bash
python generated/optimize_classifier.py
```

GEPA will:

1. Load training examples
2. Evaluate current performance
3. Use reflection to improve prompts
4. Evolve better instructions
5. Save optimized version

!!! success "Optimization Complete"
    ```
    Initial Accuracy: 75%
    Final Accuracy: 92%
    Improvement: +17%

    Optimized program saved to:
    generated/feedback_classifier_optimized.py
    ```

## Step 13: Deploy Your Classifier

Your classifier is now ready for production!

**Package it:**

```
/export package feedback-classifier
```

This creates a distributable package with:

- Your optimized code
- Configuration
- Dependencies
- README
- Tests

## What You Learned

Congratulations! You now know how to:

- ✅ Create DSPy Signatures
- ✅ Build DSPy Modules
- ✅ Use ChainOfThought for reasoning
- ✅ Validate code quality
- ✅ Generate test data
- ✅ Evaluate performance
- ✅ Optimize with GEPA
- ✅ Package for deployment

## Next Steps

### Try Different Predictors

Modify your classifier to use different reasoning patterns:

**ReAct (Reasoning + Acting):**

```python
self.classifier = dspy.ReAct(FeedbackClassifier)
```

**ProgramOfThought:**

```python
self.classifier = dspy.ProgramOfThought(FeedbackClassifier)
```

**MultiChainComparison:**

```python
self.classifier = dspy.MultiChainComparison(FeedbackClassifier, M=3)
```

### Add More Categories

Expand your classifier:

```
Modify the classifier to include categories: bug, feature, question, complaint, praise
```

### Add Confidence Scores

```
Add a confidence score output field to the classifier
```

### Multi-Label Classification

```
Allow the classifier to assign multiple categories to one feedback
```

## Common Issues

### Model Not Responding

Check your model connection:

```
/status
```

Reconnect if needed:

```
/connect ollama llama3.1:8b
```

### Low Accuracy

Try these improvements:

1. **Better examples**: Generate more diverse training data
2. **Better predictor**: Use ChainOfThought or ReAct
3. **Optimization**: Run GEPA optimization
4. **Better prompts**: Add more detailed descriptions

### Validation Errors

Read error messages carefully:

```
/validate
```

Common fixes:

- Add missing InputField/OutputField
- Inherit from dspy.Module
- Implement forward() method
- Add type hints

## Summary

You built a complete DSPy program with:

- ✅ Signature definition
- ✅ Module implementation
- ✅ Validation
- ✅ Testing
- ✅ Evaluation
- ✅ Optimization
- ✅ Deployment package

**Time to build something more complex!**

[Build a RAG System →](../tutorials/rag-system.md){ .md-button .md-button--primary }
[Learn About Optimization →](../guide/optimization.md){ .md-button }
