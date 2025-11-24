# Tutorial: Build a Sentiment Analyzer

In this tutorial, you'll build a complete sentiment analysis system using DSPy Code. Perfect for beginners!

**What you'll learn:**

- Creating DSPy Signatures
- Building Modules
- Validating code
- Running and testing
- Optimizing with GEPA

**Time:** 15 minutes

## Prerequisites

- DSPy Code installed ([Installation Guide](../getting-started/installation.md))
- Basic understanding of Python
- (Optional) Ollama or OpenAI API key for better results

## Step 1: Start DSPy Code

Open your terminal and start the CLI:

```bash
dspy-code
```

You'll see the welcome screen with the DSPy version.

## Step 2: Initialize Your Project

Let's set up a new project:

```
/init
```

This will:

- Create project configuration
- Index your DSPy installation
- Set up directories

!!! tip "Watch the Jokes!"
    During indexing, you'll see entertaining messages. This is normal and makes the wait fun!

## Step 3: Connect a Model (Optional)

For better code generation, connect to a model:

**If you have Ollama:**

```
/connect ollama llama3.1:8b
```

**If you have OpenAI:**

```
/connect openai gpt-3.5-turbo
```

!!! info "Without a Model?"
    No problem! DSPy Code can still generate code using templates. The code will be more generic but still functional.

## Step 4: Generate the Sentiment Analyzer

Now, just describe what you want in plain English:

```
Create a sentiment analyzer that takes text input and outputs whether it's positive or negative
```

DSPy Code will generate complete code for you!

!!! success "What You'll Get"
    A complete DSPy program with:
    - Signature definition
    - Module implementation
    - Example usage
    - Configuration

## Step 5: Review the Generated Code

The CLI will show you the code with syntax highlighting. Let's understand what was generated:

### The Signature

```python
class SentimentSignature(dspy.Signature):
    """Analyze the sentiment of text."""
    text: str = dspy.InputField(desc="Text to analyze")
    sentiment: str = dspy.OutputField(desc="positive or negative")
```

**What this does:**

- Defines the input (text) and output (sentiment)
- Provides descriptions for the LLM
- Sets up the task specification

### The Module

```python
class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentSignature)

    def forward(self, text):
        return self.predictor(text=text)
```

**What this does:**

- Creates a DSPy Module
- Uses ChainOfThought for reasoning
- Implements the forward method

### Example Usage

```python
# Configure DSPy
dspy.settings.configure(lm=dspy.OpenAI(model="gpt-3.5-turbo"))

# Create analyzer
analyzer = SentimentAnalyzer()

# Analyze text
result = analyzer(text="I love this product!")
print(result.sentiment)  # Output: positive
```

## Step 6: Save Your Code

Save the generated code:

```
/save sentiment_analyzer.py
```

The file will be saved to `generated/sentiment_analyzer.py`.

!!! success "Saved!"
    ```
    ✓ Code saved to: generated/sentiment_analyzer.py
    ```

## Step 7: Validate the Code

Check if the code follows best practices:

```
/validate
```

The validator will check:

- ✅ Signature has proper InputField and OutputField
- ✅ Module inherits from dspy.Module
- ✅ Forward method is implemented correctly
- ✅ No common mistakes

!!! tip "Fix Any Issues"
    If the validator finds issues, it will tell you exactly what to fix and how.

## Step 8: Test the Analyzer

Run your sentiment analyzer:

```
/run
```

DSPy Code will execute your code in a safe sandbox and show the results.

!!! example "Example Output"
    ```
    Running: generated/sentiment_analyzer.py

    Input: "I love this product!"
    Output: positive

    Input: "This is terrible"
    Output: negative

    ✓ Program executed successfully
    ```

## Step 9: Generate Training Data

To optimize your analyzer, you need training data. Let's generate some:

```
Generate 20 examples for sentiment analysis with diverse text samples
```

DSPy Code will create training examples for you!

!!! info "What You'll Get"
    ```json
    {"text": "This movie was amazing!", "sentiment": "positive"}
    {"text": "Worst experience ever", "sentiment": "negative"}
    {"text": "I'm so happy with this purchase", "sentiment": "positive"}
    ...
    ```

Save the training data:

```
/save-data sentiment_training.jsonl
```

## Step 10: Optimize with GEPA

Now let's optimize your analyzer using GEPA:

```
/optimize
```

This generates a complete GEPA optimization script!

**What the script includes:**

- Metric with feedback for GEPA
- Training data loader
- GEPA configuration
- Optimization execution code

Save the optimization script:

```
/save gepa_optimize.py
```

## Step 11: Run the Optimization

Exit DSPy Code and run the optimization:

```bash
python generated/gepa_optimize.py
```

GEPA will:

1. Load your training data
2. Evaluate your current program
3. Use reflection to improve prompts
4. Evolve better instructions
5. Save the optimized version

!!! success "Real Optimization"
    This is REAL GEPA optimization, not a simulation! It uses reflection to evolve your prompts.

## Step 12: Test the Optimized Version

The optimized program will be saved. Test it:

```bash
python generated/sentiment_analyzer_optimized.py
```

Compare the results with your original version!

## What You Built

Congratulations! You just built:

- ✅ A complete sentiment analysis system
- ✅ Training data for optimization
- ✅ GEPA optimization pipeline
- ✅ Validated, production-ready code

## Customization Ideas

Now that you have a working analyzer, try these enhancements:

### Add More Sentiment Categories

```
Modify the sentiment analyzer to output positive, negative, or neutral
```

### Add Confidence Scores

```
Add a confidence score to the sentiment output
```

### Handle Multiple Languages

```
Make the sentiment analyzer work with English, Spanish, and French
```

### Add Aspect-Based Sentiment

```
Analyze sentiment for specific aspects like quality, price, and service
```

## Common Issues

### Model Not Connected

If you see "No model connected":

```
/connect ollama llama3.1:8b
```

Or work without a model using templates.

### Code Not Saving

Check if code was generated:

```
/status
```

If no code is shown, try generating again.

### Validation Errors

Read the error messages carefully. They tell you exactly what to fix:

```
/validate
```

Follow the suggestions to fix issues.

### Optimization Fails

Make sure you have:

- Training data saved
- DSPy configured with a model
- GEPA available in your DSPy version

## Next Steps

Now that you've built a sentiment analyzer, try:

<div class="grid cards" markdown>

-   **🔍 Build a RAG System**

    Create a question-answering system with retrieval

    [RAG Tutorial →](rag-system.md)

-   **❓ Question Answering**

    Build a QA system that answers questions from context

    [QA Tutorial →](question-answering.md)

-   **⚡ Advanced Optimization**

    Learn advanced GEPA techniques

    [GEPA Guide →](gepa-optimization.md)

-   **📦 Deploy Your Analyzer**

    Package and deploy your sentiment analyzer

    [Deployment Guide →](../advanced/deployment.md)

</div>

## Summary

In this tutorial, you learned:

- ✅ How to use DSPy Code interactively
- ✅ Generating DSPy code from natural language
- ✅ Validating and testing your code
- ✅ Creating training data
- ✅ Optimizing with GEPA
- ✅ Building a complete, production-ready system

**Time to build something amazing!** 🚀

---

**Questions?** Check the [FAQ](../reference/faq.md), [Troubleshooting Guide](../reference/troubleshooting.md), or [open an issue](https://github.com/superagentic-ai/dspy-code/issues).
