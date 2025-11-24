"""
DSPy Anti-Pattern Detector

Detects common DSPy mistakes and anti-patterns.
"""

import ast

from .models import IssueCategory, IssueSeverity, ValidationIssue


class FixExampleGenerator:
    """Generates fix examples for anti-patterns."""

    @staticmethod
    def generate_module_inheritance_fix(class_name: str) -> tuple[str, str]:
        """Generate fix example for missing module inheritance."""
        example = f"""# Correct pattern:
import dspy

class {class_name}(dspy.Module):
    def __init__(self):
        super().__init__()
        # Initialize your predictors here
        self.predictor = dspy.Predict(YourSignature)

    def forward(self, **kwargs):
        # Your logic here
        return self.predictor(**kwargs)
"""
        docs_link = "https://dspy-docs.vercel.app/docs/building-blocks/modules"
        return example, docs_link

    @staticmethod
    def generate_field_type_fix(field_name: str, field_type: str = "str") -> tuple[str, str]:
        """Generate fix example for incorrect field types."""
        example = f"""# Correct pattern:
import dspy

class YourSignature(dspy.Signature):
    # Use InputField for inputs
    {field_name}: {field_type} = dspy.InputField(
        desc="Clear description of what this field represents"
    )

    # Use OutputField for outputs
    result: {field_type} = dspy.OutputField(
        desc="Clear description of the expected output"
    )
"""
        docs_link = "https://dspy-docs.vercel.app/docs/building-blocks/signatures"
        return example, docs_link

    @staticmethod
    def generate_signature_instead_of_prompt_fix() -> tuple[str, str]:
        """Generate fix example for hardcoded prompts."""
        example = """# Instead of hardcoded prompts:
# prompt = "You are a classifier. Classify the text..."

# Use DSPy signatures:
import dspy

class ClassifySignature(dspy.Signature):
    '''Classify text into categories.'''

    text: str = dspy.InputField(desc="Text to classify")
    category: str = dspy.OutputField(desc="Category label")

# Then use with a predictor:
classifier = dspy.ChainOfThought(ClassifySignature)
result = classifier(text="Your text here")
"""
        docs_link = "https://dspy-docs.vercel.app/docs/building-blocks/signatures"
        return example, docs_link

    @staticmethod
    def generate_configure_fix() -> tuple[str, str]:
        """Generate fix example for missing dspy.configure()."""
        example = """# Always configure DSPy before using predictors:
import dspy

# Option 1: Using OpenAI
lm = dspy.LM('openai/gpt-4o-mini', api_key='your-key')
dspy.configure(lm=lm)

# Option 2: Using local models
lm = dspy.LM('ollama/llama3', api_base='http://localhost:11434')
dspy.configure(lm=lm)

# Now you can use predictors
predictor = dspy.Predict(YourSignature)
result = predictor(input="Your input")
"""
        docs_link = "https://dspy-docs.vercel.app/docs/quick-start/installation"
        return example, docs_link

    @staticmethod
    def generate_forward_method_fix(class_name: str) -> tuple[str, str]:
        """Generate fix example for missing forward() method."""
        example = f"""# Correct pattern:
import dspy

class {class_name}(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(YourSignature)

    def forward(self, input_text: str):
        '''
        The forward method is required for all DSPy modules.
        It defines how the module processes inputs.
        '''
        result = self.predictor(input=input_text)
        return result
"""
        docs_link = "https://dspy-docs.vercel.app/docs/building-blocks/modules"
        return example, docs_link


class AntiPatternDetector:
    """Detects DSPy anti-patterns."""

    def detect(self, tree: ast.AST, code_lines: list[str]) -> list[ValidationIssue]:
        """Detect anti-patterns in code."""
        issues = []

        # Detect missing dspy.Module inheritance
        issues.extend(self._detect_missing_module_inheritance(tree))

        # Detect incorrect signature field types
        issues.extend(self._detect_incorrect_field_types(tree))

        # Detect hardcoded prompts
        issues.extend(self._detect_hardcoded_prompts(tree))

        # Detect missing dspy.configure() calls
        issues.extend(self._detect_missing_configure(tree, code_lines))

        return issues

    def _detect_missing_module_inheritance(self, tree: ast.AST) -> list[ValidationIssue]:
        """Detect classes that should inherit from dspy.Module but don't."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class has forward() method but doesn't inherit from dspy.Module
                has_forward = any(
                    isinstance(item, ast.FunctionDef) and item.name == "forward"
                    for item in node.body
                )

                # Check if inherits from dspy.Module
                inherits_module = any(
                    (isinstance(base, ast.Name) and base.id == "Module")
                    or (isinstance(base, ast.Attribute) and base.attr == "Module")
                    for base in node.bases
                )

                if has_forward and not inherits_module:
                    example, docs_link = FixExampleGenerator.generate_module_inheritance_fix(
                        node.name
                    )
                    issues.append(
                        ValidationIssue(
                            severity=IssueSeverity.ERROR,
                            category=IssueCategory.ANTI_PATTERN,
                            line=node.lineno,
                            message=f"Class '{node.name}' has forward() method but doesn't inherit from dspy.Module",
                            suggestion=f"Add dspy.Module inheritance: class {node.name}(dspy.Module):",
                            example=example,
                            docs_link=docs_link,
                        )
                    )

        return issues

    def _detect_incorrect_field_types(self, tree: ast.AST) -> list[ValidationIssue]:
        """Detect signature fields using incorrect types (plain attributes instead of InputField/OutputField)."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if this looks like a signature class
                inherits_signature = any(
                    (isinstance(base, ast.Name) and base.id == "Signature")
                    or (isinstance(base, ast.Attribute) and base.attr == "Signature")
                    for base in node.bases
                )

                if inherits_signature:
                    # Check for plain attribute assignments (anti-pattern)
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            # Check if value is NOT InputField or OutputField
                            is_field = False
                            if item.value:
                                if isinstance(item.value, ast.Call):
                                    if isinstance(item.value.func, ast.Attribute):
                                        is_field = item.value.func.attr in [
                                            "InputField",
                                            "OutputField",
                                        ]
                                    elif isinstance(item.value.func, ast.Name):
                                        is_field = item.value.func.id in [
                                            "InputField",
                                            "OutputField",
                                        ]

                            if not is_field and item.value:
                                field_name = item.target.id
                                # Get type hint if available
                                field_type = "str"
                                if item.annotation:
                                    if isinstance(item.annotation, ast.Name):
                                        field_type = item.annotation.id

                                example, docs_link = FixExampleGenerator.generate_field_type_fix(
                                    field_name, field_type
                                )
                                issues.append(
                                    ValidationIssue(
                                        severity=IssueSeverity.ERROR,
                                        category=IssueCategory.ANTI_PATTERN,
                                        line=item.lineno,
                                        message=f"Signature field '{field_name}' should use InputField or OutputField",
                                        suggestion="Use dspy.InputField() or dspy.OutputField() for signature fields",
                                        example=example,
                                        docs_link=docs_link,
                                    )
                                )

        return issues

    def _detect_hardcoded_prompts(self, tree: ast.AST) -> list[ValidationIssue]:
        """Detect hardcoded prompt strings (anti-pattern)."""
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                # Look for long strings that look like prompts
                prompt_indicators = [
                    "you are",
                    "please",
                    "task is to",
                    "given the following",
                    "your job",
                ]
                if len(node.value) > 100 and any(
                    indicator in node.value.lower() for indicator in prompt_indicators
                ):
                    example, docs_link = (
                        FixExampleGenerator.generate_signature_instead_of_prompt_fix()
                    )
                    issues.append(
                        ValidationIssue(
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.ANTI_PATTERN,
                            line=node.lineno,
                            message="Hardcoded prompt detected - use DSPy signatures instead",
                            suggestion="Replace hardcoded prompts with DSPy signatures for better optimization",
                            example=example,
                            docs_link=docs_link,
                        )
                    )

        return issues

    def _detect_missing_configure(
        self, tree: ast.AST, code_lines: list[str]
    ) -> list[ValidationIssue]:
        """Detect missing dspy.configure() calls when predictors are used."""
        issues = []

        # Check if code uses predictors
        has_predictor = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["Predict", "ChainOfThought", "ReAct", "ProgramOfThought"]:
                        has_predictor = True
                        break
                elif isinstance(node.func, ast.Name):
                    if node.func.id in ["Predict", "ChainOfThought", "ReAct", "ProgramOfThought"]:
                        has_predictor = True
                        break

        # Check if dspy.configure() is called
        has_configure = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == "configure":
                        has_configure = True
                        break

        if has_predictor and not has_configure:
            example, docs_link = FixExampleGenerator.generate_configure_fix()
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.ANTI_PATTERN,
                    line=1,
                    message="Predictors used but dspy.configure() not called",
                    suggestion="Add dspy.configure() to set up the language model before using predictors",
                    example=example,
                    docs_link=docs_link,
                )
            )

        return issues
