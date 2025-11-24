"""
DSPy Learning Integration

Provides educational content and learning resources for DSPy users.
"""

from dataclasses import dataclass

from .models import IssueCategory, ValidationIssue


@dataclass
class LearningResource:
    """Represents a learning resource."""

    title: str
    description: str
    link: str
    category: str


class LearningIntegration:
    """Integrates learning resources into validation feedback."""

    def __init__(self):
        """Initialize learning integration."""
        self.resources = self._initialize_resources()
        self.educational_comments = self._initialize_educational_comments()

    def _initialize_resources(self) -> dict[str, list[LearningResource]]:
        """Initialize learning resources by category."""
        return {
            "signatures": [
                LearningResource(
                    title="DSPy Signatures Guide",
                    description="Learn how to define and use DSPy signatures effectively",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/signatures",
                    category="signatures",
                ),
                LearningResource(
                    title="Field Types in DSPy",
                    description="Understanding InputField and OutputField",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/signatures#fields",
                    category="signatures",
                ),
            ],
            "modules": [
                LearningResource(
                    title="DSPy Modules Guide",
                    description="Learn how to create custom DSPy modules",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/modules",
                    category="modules",
                ),
                LearningResource(
                    title="Module Composition",
                    description="Composing modules for complex workflows",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/modules#composition",
                    category="modules",
                ),
            ],
            "predictors": [
                LearningResource(
                    title="DSPy Predictors Overview",
                    description="Understanding different predictor types",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/predictors",
                    category="predictors",
                ),
                LearningResource(
                    title="ChainOfThought vs Predict",
                    description="When to use ChainOfThought over Predict",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/predictors#chainofthought",
                    category="predictors",
                ),
            ],
            "optimization": [
                LearningResource(
                    title="DSPy Optimization Guide",
                    description="Learn how to optimize your DSPy programs",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/optimizers",
                    category="optimization",
                ),
                LearningResource(
                    title="Writing Metric Functions",
                    description="Creating effective metrics for optimization",
                    link="https://dspy-docs.vercel.app/docs/building-blocks/metrics",
                    category="optimization",
                ),
            ],
            "best_practices": [
                LearningResource(
                    title="DSPy Best Practices",
                    description="Tips and patterns for production DSPy code",
                    link="https://dspy-docs.vercel.app/docs/guides/best-practices",
                    category="best_practices",
                ),
                LearningResource(
                    title="Error Handling in DSPy",
                    description="Robust error handling patterns",
                    link="https://dspy-docs.vercel.app/docs/guides/error-handling",
                    category="best_practices",
                ),
            ],
        }

    def _initialize_educational_comments(self) -> dict[str, str]:
        """Initialize educational comments for common patterns."""
        return {
            "signature_definition": """
# DSPy Signature: Defines the input/output interface for your task
# - Use InputField() for inputs with clear descriptions
# - Use OutputField() for expected outputs
# - Type hints help with validation and IDE support
# - Good descriptions improve LM understanding
""",
            "module_definition": """
# DSPy Module: Encapsulates your program logic
# - Inherit from dspy.Module for proper initialization
# - Define predictors in __init__() for reusability
# - Implement forward() to define your program flow
# - Call super().__init__() to initialize the base class
""",
            "predictor_usage": """
# DSPy Predictors: Execute your signatures with LMs
# - Predict: Basic prediction without reasoning
# - ChainOfThought: Adds reasoning steps (better for complex tasks)
# - ReAct: For tasks requiring tool use and reasoning
# - Choose based on task complexity and accuracy needs
""",
            "configuration": """
# DSPy Configuration: Set up your language model
# - Always call dspy.configure() before using predictors
# - Configure once at the start of your program
# - Supports OpenAI, Anthropic, local models, and more
# - Example: dspy.configure(lm=dspy.LM('openai/gpt-4o-mini'))
""",
            "optimization": """
# DSPy Optimization: Improve your program automatically
# - Define a metric function to measure quality
# - Use optimizers like GEPA or BootstrapFewShot
# - Provide training examples for best results
# - Optimization can significantly improve accuracy
""",
        }

    def get_educational_comment(self, category: str) -> str | None:
        """
        Get educational comment for a category.

        Args:
            category: Category of the comment

        Returns:
            Educational comment string or None
        """
        return self.educational_comments.get(category)

    def get_resources_for_issue(self, issue: ValidationIssue) -> list[LearningResource]:
        """
        Get relevant learning resources for an issue.

        Args:
            issue: ValidationIssue to get resources for

        Returns:
            List of relevant learning resources
        """
        resources = []

        # Map issue categories to resource categories
        if issue.category == IssueCategory.SIGNATURE:
            resources.extend(self.resources.get("signatures", []))
        elif issue.category == IssueCategory.MODULE:
            resources.extend(self.resources.get("modules", []))
        elif issue.category == IssueCategory.PREDICTOR:
            resources.extend(self.resources.get("predictors", []))
        elif issue.category == IssueCategory.BEST_PRACTICE:
            # Check message for specific topics
            if "metric" in issue.message.lower() or "optimization" in issue.message.lower():
                resources.extend(self.resources.get("optimization", []))
            else:
                resources.extend(self.resources.get("best_practices", []))

        return resources

    def get_next_learning_steps(self, issues: list[ValidationIssue]) -> list[str]:
        """
        Suggest next learning steps based on issues.

        Args:
            issues: List of validation issues

        Returns:
            List of suggested learning steps
        """
        steps = []

        # Analyze issues to suggest learning path
        has_signature_issues = any(i.category == IssueCategory.SIGNATURE for i in issues)
        has_module_issues = any(i.category == IssueCategory.MODULE for i in issues)
        has_predictor_issues = any(i.category == IssueCategory.PREDICTOR for i in issues)
        has_optimization_issues = any("metric" in i.message.lower() for i in issues)

        if has_signature_issues:
            steps.append("Learn about DSPy Signatures: /explain signatures")
            steps.append("Practice: Create a signature for your use case")

        if has_module_issues:
            steps.append("Learn about DSPy Modules: /explain modules")
            steps.append("Practice: Build a simple module with your signature")

        if has_predictor_issues:
            steps.append("Learn about Predictors: /explain predictors")
            steps.append("Try: Experiment with ChainOfThought vs Predict")

        if has_optimization_issues:
            steps.append("Learn about Optimization: /explain optimization")
            steps.append("Practice: Write a metric function for your task")

        # Always suggest general best practices
        if not steps:
            steps.append("Explore DSPy patterns: /patterns")
            steps.append("Review best practices: /explain best-practices")

        return steps

    def generate_code_comments(self, code: str, issues: list[ValidationIssue]) -> str:
        """
        Add educational comments to code based on issues.

        Args:
            code: Source code
            issues: List of validation issues

        Returns:
            Code with educational comments added
        """
        lines = code.split("\n")
        commented_lines = []

        # Add header comment
        commented_lines.append("# DSPy Code with Educational Comments")
        commented_lines.append("# Generated by DSPy Code Validator")
        commented_lines.append("")

        # Track which educational comments we've added
        added_comments = set()

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check if any issues are on this line
            line_issues = [issue for issue in issues if issue.line == line_num]

            # Add educational comments before the line if needed
            for issue in line_issues:
                comment_key = self._get_comment_key_for_issue(issue)
                if comment_key and comment_key not in added_comments:
                    comment = self.get_educational_comment(comment_key)
                    if comment:
                        commented_lines.append(comment)
                        added_comments.add(comment_key)

            # Add the original line
            commented_lines.append(line)

        return "\n".join(commented_lines)

    def _get_comment_key_for_issue(self, issue: ValidationIssue) -> str | None:
        """Get the educational comment key for an issue."""
        if issue.category == IssueCategory.SIGNATURE:
            return "signature_definition"
        elif issue.category == IssueCategory.MODULE:
            return "module_definition"
        elif issue.category == IssueCategory.PREDICTOR:
            return "predictor_usage"
        elif "configure" in issue.message.lower():
            return "configuration"
        elif "metric" in issue.message.lower() or "optimization" in issue.message.lower():
            return "optimization"
        return None

    def format_learning_resources(self, resources: list[LearningResource]) -> str:
        """
        Format learning resources for display.

        Args:
            resources: List of learning resources

        Returns:
            Formatted string
        """
        if not resources:
            return "No specific resources available."

        lines = []
        for resource in resources:
            lines.append(f"• {resource.title}")
            lines.append(f"  {resource.description}")
            lines.append(f"  {resource.link}")
            lines.append("")

        return "\n".join(lines)

    def get_cli_commands_for_learning(self, issues: list[ValidationIssue]) -> list[str]:
        """
        Get relevant CLI commands for learning based on issues.

        Args:
            issues: List of validation issues

        Returns:
            List of CLI commands
        """
        commands = []

        # Map issues to CLI commands
        categories = {issue.category for issue in issues}

        if IssueCategory.SIGNATURE in categories:
            commands.append("/generate signature - Generate a signature template")
            commands.append("/explain signatures - Learn about signatures")

        if IssueCategory.MODULE in categories:
            commands.append("/generate module - Generate a module template")
            commands.append("/explain modules - Learn about modules")

        if IssueCategory.PREDICTOR in categories:
            commands.append("/explain predictors - Learn about predictors")

        # Always include validation command
        commands.append("/validate - Validate your code")

        return commands
