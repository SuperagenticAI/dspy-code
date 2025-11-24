"""
Example usage of DSPy Code validation system.

This file demonstrates how to use the various validation components
to ensure safe and correct input processing.
"""

from dspy_cli.validation import (
    CodeValidationError,
    CodeValidator,
    ConfigurationError,
    ConfigValidator,
    InputValidator,
    SecurityError,
    SecurityValidator,
    ValidationError,
)


def demonstrate_input_validation():
    """Demonstrate input validation capabilities."""
    print("=== Input Validation Examples ===")

    validator = InputValidator()

    # Task description validation
    try:
        task = "Classify customer support emails into categories based on content and urgency"
        validated_task = validator.validate_task_description(task)
        print(f"✓ Valid task: {validated_task}")
    except ValidationError as e:
        print(f"✗ Invalid task: {e}")

    # Field name validation
    try:
        field_name = validator.validate_field_name("email_content")
        print(f"✓ Valid field name: {field_name}")

        # This will fail
        validator.validate_field_name("123invalid")
    except ValidationError as e:
        print(f"✗ Invalid field name: {e}")

    # Reasoning pattern validation
    try:
        pattern = validator.validate_reasoning_pattern("chain_of_thought")
        print(f"✓ Valid reasoning pattern: {pattern}")
    except ValidationError as e:
        print(f"✗ Invalid reasoning pattern: {e}")

    print()


def demonstrate_config_validation():
    """Demonstrate configuration validation capabilities."""
    print("=== Configuration Validation Examples ===")

    validator = ConfigValidator()

    # API key validation
    try:
        # Valid OpenAI API key format
        api_key = "sk-" + "a" * 48
        validated_key = validator.validate_api_key("openai", api_key)
        print(f"✓ Valid API key format (length: {len(validated_key)})")
    except ConfigurationError as e:
        print(f"✗ Invalid API key: {e}")

    # Model name validation
    try:
        model = validator.validate_model_name("openai", "gpt-4")
        print(f"✓ Valid model: {model}")

        # This will fail
        validator.validate_model_name("openai", "invalid-model")
    except ConfigurationError as e:
        print(f"✗ Invalid model: {e}")

    # Endpoint URL validation
    try:
        url = validator.validate_endpoint_url("http://localhost:11434")
        print(f"✓ Valid endpoint URL: {url}")
    except ConfigurationError as e:
        print(f"✗ Invalid endpoint URL: {e}")

    # GEPA configuration validation
    try:
        gepa_config = {
            "max_iterations": 10,
            "population_size": 20,
            "mutation_rate": 0.1,
            "evaluation_metric": "accuracy",
        }
        validated_config = validator.validate_gepa_config(gepa_config)
        print(f"✓ Valid GEPA config: {validated_config}")
    except ConfigurationError as e:
        print(f"✗ Invalid GEPA config: {e}")

    print()


def demonstrate_code_validation():
    """Demonstrate code validation capabilities."""
    print("=== Code Validation Examples ===")

    validator = CodeValidator()

    # DSPy signature validation
    signature_code = """
import dspy

class EmailClassification(dspy.Signature):
    \"\"\"Classify emails into categories.\"\"\"
    email_text = dspy.InputField(desc="The email content to classify")
    sender_info = dspy.InputField(desc="Information about the sender")
    category = dspy.OutputField(desc="The email category")
    priority = dspy.OutputField(desc="The priority level")
"""

    try:
        result = validator.validate_dspy_signature(signature_code)
        print(f"✓ Valid DSPy signature: {result['class_name']}")
        print(f"  Input fields: {result['input_fields']}")
        print(f"  Output fields: {result['output_fields']}")
    except CodeValidationError as e:
        print(f"✗ Invalid signature: {e}")

    # DSPy module validation
    module_code = """
import dspy

class EmailClassifier(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(EmailClassification)

    def forward(self, email_text, sender_info):
        result = self.predictor(email_text=email_text, sender_info=sender_info)
        return result
"""

    try:
        result = validator.validate_dspy_module(module_code)
        print(f"✓ Valid DSPy module: {result['class_name']}")
        print(f"  Has __init__: {result['has_init']}")
        print(f"  Has forward: {result['has_forward']}")
    except CodeValidationError as e:
        print(f"✗ Invalid module: {e}")

    # Field definitions validation
    try:
        fields = [
            {"name": "input_text", "type": "str", "description": "The input text to process"},
            {"name": "output_label", "type": "str", "description": "The predicted label"},
        ]
        validated_fields = validator.validate_field_definitions(fields)
        print(f"✓ Valid field definitions: {len(validated_fields)} fields")
    except CodeValidationError as e:
        print(f"✗ Invalid field definitions: {e}")

    print()


def demonstrate_security_validation():
    """Demonstrate security validation capabilities."""
    print("=== Security Validation Examples ===")

    validator = SecurityValidator()

    # Safe code validation
    safe_code = """
def classify_email(email_text):
    if "urgent" in email_text.lower():
        return "high_priority"
    elif "spam" in email_text.lower():
        return "spam"
    else:
        return "normal"
"""

    try:
        result = validator.validate_code_execution_safety(safe_code)
        print(f"✓ Safe code validated: {result['safe']}")
    except SecurityError as e:
        print(f"✗ Unsafe code: {e}")

    # Dangerous code validation
    dangerous_code = "eval('malicious_code')"

    try:
        validator.validate_code_execution_safety(dangerous_code)
    except SecurityError as e:
        print(f"✓ Dangerous code detected: {e}")

    # File access validation
    try:
        from pathlib import Path

        safe_path = Path("data/examples.json")
        result = validator.validate_file_access_safety(safe_path, "read")
        print(f"✓ Safe file access: {result}")
    except SecurityError as e:
        print(f"✗ Unsafe file access: {e}")

    # Path traversal detection
    try:
        dangerous_path = Path("../../../etc/passwd")
        validator.validate_file_access_safety(dangerous_path, "read")
    except SecurityError as e:
        print(f"✓ Path traversal detected: {e}")

    # API key security validation
    try:
        api_key = "sk-" + "a" * 48
        result = validator.validate_api_key_security(api_key, "openai")
        print(f"✓ Secure API key: {result}")
    except SecurityError as e:
        print(f"✗ Insecure API key: {e}")

    # Fake API key detection
    try:
        fake_key = "test_key_here"
        validator.validate_api_key_security(fake_key, "openai")
    except SecurityError as e:
        print(f"✓ Fake API key detected: {e}")

    # User input sanitization
    try:
        user_input = "This is normal user input with some text."
        sanitized = validator.validate_user_input_safety(user_input, "general")
        print(f"✓ Safe user input: {sanitized[:50]}...")
    except SecurityError as e:
        print(f"✗ Unsafe user input: {e}")

    print()


def main():
    """Run all validation examples."""
    print("DSPy Code Validation System Examples")
    print("=" * 50)
    print()

    demonstrate_input_validation()
    demonstrate_config_validation()
    demonstrate_code_validation()
    demonstrate_security_validation()

    print("All validation examples completed!")


if __name__ == "__main__":
    main()
