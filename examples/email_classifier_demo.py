"""
Email Classifier Demo - Complete DSPy Workflow
===============================================

This example shows a realistic use case: building an email classifier
that categorizes emails as urgent, normal, or low priority.

What this demonstrates:
1. Creating a DSPy Signature
2. Building a Module with Chain of Thought
3. Testing the module
4. Preparing training data
5. Optimizing with GEPA
6. Evaluating improvements

This is what you can build through the interactive CLI!
"""

import dspy

# ============================================================================
# PART 1: SIGNATURE DEFINITION
# ============================================================================
# In CLI: "Create a signature for email classification"


class EmailClassification(dspy.Signature):
    """Classify emails by priority level."""

    subject = dspy.InputField(desc="Email subject line")
    body = dspy.InputField(desc="Email body content")
    sender = dspy.InputField(desc="Sender email address")

    priority = dspy.OutputField(desc="Priority: urgent, normal, or low")
    reason = dspy.OutputField(desc="Brief explanation for the classification")


# ============================================================================
# PART 2: MODULE IMPLEMENTATION
# ============================================================================
# In CLI: "Build a module using chain of thought for email classification"


class EmailClassifier(dspy.Module):
    """Email classifier using chain of thought reasoning."""

    def __init__(self):
        super().__init__()
        # Chain of Thought provides step-by-step reasoning
        self.classifier = dspy.ChainOfThought(EmailClassification)

    def forward(self, subject: str, body: str, sender: str = "unknown@example.com"):
        """
        Classify an email's priority.

        Args:
            subject: Email subject line
            body: Email body content
            sender: Sender email address

        Returns:
            Classification result with priority and reason
        """
        result = self.classifier(subject=subject, body=body, sender=sender)
        return result


# ============================================================================
# PART 3: TRAINING DATA
# ============================================================================
# In CLI: Collected interactively or loaded from file


def get_training_examples() -> list[dspy.Example]:
    """
    Create training examples for optimization.

    In production, these would come from:
    - Historical data
    - User feedback
    - Manual labeling
    """

    examples = [
        # Urgent emails
        dspy.Example(
            subject="URGENT: Server down",
            body="Production server is not responding. Need immediate attention.",
            sender="ops@company.com",
            priority="urgent",
        ).with_inputs("subject", "body", "sender"),
        dspy.Example(
            subject="Critical bug in payment system",
            body="Users cannot complete purchases. Revenue impact is significant.",
            sender="support@company.com",
            priority="urgent",
        ).with_inputs("subject", "body", "sender"),
        dspy.Example(
            subject="Security breach detected",
            body="Unusual activity detected in user accounts. Immediate action required.",
            sender="security@company.com",
            priority="urgent",
        ).with_inputs("subject", "body", "sender"),
        # Normal priority emails
        dspy.Example(
            subject="Weekly team meeting",
            body="Reminder about our weekly sync on Friday at 2pm.",
            sender="manager@company.com",
            priority="normal",
        ).with_inputs("subject", "body", "sender"),
        dspy.Example(
            subject="Code review request",
            body="Please review my pull request when you have a chance.",
            sender="developer@company.com",
            priority="normal",
        ).with_inputs("subject", "body", "sender"),
        dspy.Example(
            subject="Question about API documentation",
            body="Could you clarify the authentication flow in the docs?",
            sender="partner@external.com",
            priority="normal",
        ).with_inputs("subject", "body", "sender"),
        # Low priority emails
        dspy.Example(
            subject="Office lunch options",
            body="What should we order for lunch next week?",
            sender="admin@company.com",
            priority="low",
        ).with_inputs("subject", "body", "sender"),
        dspy.Example(
            subject="Newsletter: Tech trends 2024",
            body="Check out the latest technology trends and insights.",
            sender="newsletter@techblog.com",
            priority="low",
        ).with_inputs("subject", "body", "sender"),
        dspy.Example(
            subject="Company social event",
            body="Join us for happy hour this Friday!",
            sender="hr@company.com",
            priority="low",
        ).with_inputs("subject", "body", "sender"),
    ]

    return examples


# ============================================================================
# PART 4: EVALUATION METRIC
# ============================================================================


def classification_accuracy(example, prediction, trace=None) -> float:
    """
    Evaluate if the predicted priority matches the gold standard.

    Returns:
        1.0 if correct, 0.0 if incorrect
    """
    predicted_priority = prediction.priority.lower().strip()
    expected_priority = example.priority.lower().strip()

    return float(predicted_priority == expected_priority)


# ============================================================================
# PART 5: OPTIMIZATION
# ============================================================================
# In CLI: "dspy-code optimize email_classifier.py"


def optimize_classifier(classifier: EmailClassifier, examples: list[dspy.Example]):
    """
    Optimize the classifier using GEPA or BootstrapFewShot.

    This improves performance by:
    - Finding better prompts
    - Selecting good examples for few-shot learning
    - Tuning the reasoning process
    """

    print("🔧 Optimizing Email Classifier...")
    print(f"   Training examples: {len(examples)}")
    print()

    # Split data
    train_size = int(len(examples) * 0.7)
    train_set = examples[:train_size]
    val_set = examples[train_size:]

    # Use BootstrapFewShot optimizer
    # (In production, you'd use GEPA for better results)
    from dspy.teleprompt import BootstrapFewShot

    optimizer = BootstrapFewShot(
        metric=classification_accuracy, max_bootstrapped_demos=2, max_labeled_demos=2
    )

    print("⚙️  Compiling optimized classifier...")
    optimized = optimizer.compile(classifier, trainset=train_set)

    # Evaluate
    print("📊 Evaluating performance...")
    print()

    # Test original
    original_correct = sum(
        classification_accuracy(ex, classifier(subject=ex.subject, body=ex.body, sender=ex.sender))
        for ex in val_set
    )
    original_accuracy = original_correct / len(val_set)

    # Test optimized
    optimized_correct = sum(
        classification_accuracy(ex, optimized(subject=ex.subject, body=ex.body, sender=ex.sender))
        for ex in val_set
    )
    optimized_accuracy = optimized_correct / len(val_set)

    print(f"   Original Accuracy:  {original_accuracy:.1%}")
    print(f"   Optimized Accuracy: {optimized_accuracy:.1%}")
    print(f"   Improvement:        {(optimized_accuracy - original_accuracy):.1%}")
    print()

    return optimized


# ============================================================================
# PART 6: DEMO USAGE
# ============================================================================


def demo_classifier():
    """Demonstrate the email classifier in action."""

    print("=" * 70)
    print("Email Classifier Demo - DSPy Complete Workflow")
    print("=" * 70)
    print()

    # Test emails
    test_emails = [
        {
            "subject": "Database backup failed",
            "body": "The nightly backup job failed. Data loss risk.",
            "sender": "system@company.com",
        },
        {
            "subject": "Lunch and learn session",
            "body": "Join us for a presentation on new technologies.",
            "sender": "learning@company.com",
        },
        {
            "subject": "Customer complaint escalation",
            "body": "VIP customer is threatening to cancel their contract.",
            "sender": "sales@company.com",
        },
    ]

    print("📧 Testing Email Classifier")
    print()

    # Note: This requires a configured language model
    # In the CLI, you'd do: run `dspy-code` and then `/connect ollama llama3.1:8b`
    # 💡 Using Ollama locally (no API keys needed)

    try:
        # Configure DSPy using Ollama locally
        # Make sure Ollama is running: ollama serve
        # Pull model: ollama pull llama3.1:8b
        lm = dspy.LM(model="ollama/llama3.1:8b", api_base="http://localhost:11434")
        dspy.configure(lm=lm)

        # Create classifier
        classifier = EmailClassifier()

        # Test each email
        for i, email in enumerate(test_emails, 1):
            print(f"Email {i}:")
            print(f"  Subject: {email['subject']}")
            print(f"  From: {email['sender']}")
            print()

            result = classifier(
                subject=email["subject"], body=email["body"], sender=email["sender"]
            )

            print(f"  ✓ Priority: {result.priority.upper()}")
            print(f"  ✓ Reason: {result.reason}")
            print()

        # Demonstrate optimization
        print("=" * 70)
        print("Now let's optimize with training data...")
        print("=" * 70)
        print()

        examples = get_training_examples()
        optimized_classifier = optimize_classifier(classifier, examples)

        print("✅ Optimization complete!")
        print()
        print("The optimized classifier is now ready for production use.")

    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("To run this demo:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start Ollama: ollama serve")
        print("3. Pull model: ollama pull llama3.1:8b")
        print("4. Install DSPy: pip install dspy")
        print("5. Run: python examples/email_classifier_demo.py")
        print()
        print("Or use the CLI:")
        print("1. dspy-code init")
        print("2. Inside interactive mode run: /connect ollama llama3.1:8b")
        print("3. dspy-code")
        print("4. 'Create an email classifier with chain of thought'")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print()
    print("This example shows what you can build with DSPy Code!")
    print()
    print("Through the interactive CLI, you can:")
    print("  ✓ Create this signature by describing it in natural language")
    print("  ✓ Generate the module code automatically")
    print("  ✓ Get training examples interactively")
    print("  ✓ Optimize with a single command")
    print("  ✓ Save and deploy the optimized version")
    print()
    print("-" * 70)
    print()

    demo_classifier()
