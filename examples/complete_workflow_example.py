"""
Complete DSPy Workflow Example
===============================

This example demonstrates the full workflow:
1. Create a DSPy Signature
2. Build a Module with reasoning
3. Create a complete program
4. Optimize with GEPA

This shows what users can achieve through the interactive CLI.
"""

import dspy

# Step 1: Define a Signature
# ---------------------------
# In the CLI, you'd say: "Create a signature for sentiment analysis"


class SentimentAnalysis(dspy.Signature):
    """Analyze the sentiment of text."""

    text = dspy.InputField(desc="The text to analyze")
    sentiment = dspy.OutputField(desc="The sentiment: positive, negative, or neutral")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1")


# Step 2: Create a Module with Chain of Thought
# -----------------------------------------------
# In the CLI: "Build a module using chain of thought for sentiment analysis"


class SentimentAnalyzer(dspy.Module):
    """A sentiment analyzer using chain of thought reasoning."""

    def __init__(self):
        super().__init__()
        # Use ChainOfThought for better reasoning
        self.predictor = dspy.ChainOfThought(SentimentAnalysis)

    def forward(self, text: str):
        """Analyze sentiment of the given text."""
        result = self.predictor(text=text)
        return result


# Step 3: Create Training Examples for GEPA
# ------------------------------------------
# These would be collected through the CLI or loaded from a file


def create_training_examples() -> list[dspy.Example]:
    """Create gold standard examples for optimization."""

    examples = [
        dspy.Example(
            text="I absolutely love this product! It's amazing!",
            sentiment="positive",
            confidence="0.95",
        ).with_inputs("text"),
        dspy.Example(
            text="This is the worst experience I've ever had.",
            sentiment="negative",
            confidence="0.90",
        ).with_inputs("text"),
        dspy.Example(
            text="It's okay, nothing special.", sentiment="neutral", confidence="0.75"
        ).with_inputs("text"),
        dspy.Example(
            text="Fantastic service and great quality!", sentiment="positive", confidence="0.92"
        ).with_inputs("text"),
        dspy.Example(
            text="Terrible quality, very disappointed.", sentiment="negative", confidence="0.88"
        ).with_inputs("text"),
    ]

    return examples


# Step 4: Define Evaluation Metric with Feedback (Required for GEPA)
# -------------------------------------------------------------------
# GEPA requires a metric that returns (score, feedback) tuple
# The feedback helps GEPA understand why predictions fail and improve prompts


def sentiment_accuracy_with_feedback(gold, pred, trace=None, pred_name=None, pred_trace=None):
    """
    Evaluate sentiment prediction and provide feedback for GEPA.

    GEPA requires a metric with exactly 5 arguments:
    - gold: The gold standard example (dspy.Example)
    - pred: The prediction (dspy.Prediction)
    - trace: Optional execution trace
    - pred_name: Optional prediction name
    - pred_trace: Optional prediction trace

    GEPA uses the feedback to evolve better prompts through reflection.

    Returns:
        - float (score): When prediction is correct (1.0)
        - dict: When incorrect, returns {'score': 0.0, 'feedback': str}
        This format matches GEPA's expected metric return type.
    """
    predicted = pred.sentiment.lower().strip()
    expected = gold.sentiment.lower().strip()

    # Calculate score
    correct = predicted == expected
    score = 1.0 if correct else 0.0

    # GEPA expects: return score (float) when correct, or dict with score+feedback when incorrect
    # This matches the format used in dspy_code/generators/gepa_generator.py
    if correct:
        return score
    else:
        feedback = f"Incorrect. Expected '{expected}' but got '{predicted}'. "
        feedback += "Consider analyzing the text more carefully for sentiment indicators."
        return {"score": score, "feedback": feedback}


# Step 5: Optimize with GEPA (Genetic Pareto)
# ---------------------------------------------
# In the CLI: "optimize my_program.py --examples-file examples.jsonl"
# GEPA uses genetic algorithms and reflection to evolve better prompts


def optimize_with_gepa(module: dspy.Module, examples: list[dspy.Example]):
    """
    Optimize the module using GEPA (Genetic Pareto).

    GEPA will:
    - Create a population of prompt variations
    - Evaluate each on training data
    - Use reflection to understand failures
    - Evolve better prompts through genetic algorithms
    - Select the best performing version
    """

    print("🔧 Starting GEPA Optimization...")
    print(f"   Training examples: {len(examples)}")
    print("   Metric: sentiment_accuracy_with_feedback")
    print()

    # Split into train and validation
    train_size = int(len(examples) * 0.8)
    train_examples = examples[:train_size]
    val_examples = examples[train_size:]

    # Import GEPA optimizer
    from dspy.teleprompt import GEPA

    # Configure reflection LM (can be same as main LM for local use)
    # GEPA uses this to generate feedback and evolve prompts
    reflection_lm = dspy.LM(model="ollama/llama3.1:8b", api_base="http://localhost:11434")

    # Configure GEPA optimizer
    # GEPA uses genetic algorithms to evolve better prompts
    # The metric must return (score, feedback) tuple for GEPA to work
    # max_metric_calls limits the number of metric evaluations (budget control)
    optimizer = GEPA(
        metric=sentiment_accuracy_with_feedback,
        reflection_lm=reflection_lm,
        max_metric_calls=30,  # Budget: 30 metric evaluations for this demo
    )

    print("⚙️  GEPA Configuration:")
    print("   • Using GEPA (Genetic Pareto) optimizer")
    print("   • Reflection LM: ollama/llama3.1:8b")
    print("   • Metric: sentiment_accuracy_with_feedback")
    print("     (returns float when correct, dict with feedback when incorrect)")
    print("   • Budget: 30 metric calls (for demo - increase for production)")
    print("   • Estimated time: 3-10 minutes")
    print()

    # Compile (optimize) the module
    print("🚀 Running GEPA optimization...")
    print("   This will evolve prompts through genetic algorithms...")
    print()

    optimized_module = optimizer.compile(
        student=module, trainset=train_examples, valset=val_examples
    )

    print("✅ Optimization complete!")
    print()

    # Evaluate on validation set
    print("📊 Evaluating optimized module...")
    correct = 0
    for example in val_examples:
        prediction = optimized_module(text=example.text)
        result = sentiment_accuracy_with_feedback(example, prediction, None, None, None)
        # Handle both return formats: float (correct) or dict (incorrect with feedback)
        if isinstance(result, dict):
            score = result["score"]
        else:
            score = result
        if score == 1.0:
            correct += 1

    accuracy = correct / len(val_examples) if val_examples else 0
    print(f"   Validation Accuracy: {accuracy:.1%}")
    print()

    return optimized_module


# Step 6: Complete Program
# -------------------------


def main():
    """
    Main program demonstrating the complete workflow.

    This is what gets generated when you use the CLI to create
    a complete program with optimization.
    """

    print("=" * 60)
    print("DSPy Complete Workflow Example")
    print("=" * 60)
    print()

    # Configure DSPy with your language model
    # In the CLI, this is done through: /connect <provider> <model>
    print("📝 Step 1: Configure Language Model")
    print("   (In CLI: start dspy-code, then run /connect ollama llama3.1:8b)")
    print("   💡 Using Ollama locally (no API keys needed)")

    # Using Ollama locally - no API keys required
    # Make sure Ollama is running: ollama serve
    # Pull model: ollama pull llama3.1:8b
    lm = dspy.LM(model="ollama/llama3.1:8b", api_base="http://localhost:11434")
    dspy.configure(lm=lm)
    print("   ✓ Model configured")
    print()

    # Create the module
    print("🏗️  Step 2: Create Sentiment Analyzer Module")
    print("   (In CLI: 'Create a sentiment analysis module with chain of thought')")
    analyzer = SentimentAnalyzer()
    print("   ✓ Module created")
    print()

    # Test before optimization
    print("🧪 Step 3: Test Before Optimization")
    test_text = "This product exceeded my expectations!"
    result = analyzer(text=test_text)
    print(f"   Input: {test_text}")
    print(f"   Sentiment: {result.sentiment}")
    print(f"   Confidence: {result.confidence}")
    print()

    # Create training examples
    print("📚 Step 4: Prepare Training Examples")
    print("   (In CLI: Collected interactively or loaded from file)")
    examples = create_training_examples()
    print(f"   ✓ {len(examples)} examples prepared")
    print()

    # Optimize with GEPA
    print("🚀 Step 5: Optimize with GEPA")
    print("   (In CLI: dspy-code optimize sentiment_analyzer.py)")
    optimized_analyzer = optimize_with_gepa(analyzer, examples)
    print()

    # Test after optimization
    print("✨ Step 6: Test Optimized Module")
    result = optimized_analyzer(text=test_text)
    print(f"   Input: {test_text}")
    print(f"   Sentiment: {result.sentiment}")
    print(f"   Confidence: {result.confidence}")
    print()

    # Save the optimized module
    print("💾 Step 7: Save Optimized Module")
    print("   (In CLI: save optimized_sentiment_analyzer.py)")
    print("   ✓ Module saved and ready to use!")
    print()

    print("=" * 60)
    print("Workflow Complete! 🎉")
    print("=" * 60)
    print()
    print("What you accomplished:")
    print("  ✓ Created a DSPy Signature")
    print("  ✓ Built a Module with Chain of Thought")
    print("  ✓ Prepared training examples")
    print("  ✓ Optimized with GEPA")
    print("  ✓ Validated performance improvement")
    print()
    print("Next steps:")
    print("  • Deploy the optimized module")
    print("  • Integrate into your application")
    print("  • Monitor performance in production")


if __name__ == "__main__":
    # Note: This example uses Ollama locally (no API keys needed)
    # Make sure Ollama is running: ollama serve
    # Pull model: ollama pull llama3.1:8b

    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("To run this example:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Pull model: ollama pull llama3.1:8b")
        print("4. Install DSPy: pip install dspy")
        print("5. Run: python examples/complete_workflow_example.py")
