"""
DSPy Predictor Validator

Validates DSPy predictor usage and suggests better alternatives.
"""

import ast

from .models import IssueCategory, IssueSeverity, ValidationIssue


class PredictorValidator:
    """Validates DSPy predictor usage."""

    # Predictor information for recommendations
    PREDICTORS = {
        "Predict": {
            "description": "Direct prediction without reasoning",
            "best_for": ["simple tasks", "fast responses"],
            "upgrade_to": "ChainOfThought",
            "complexity": "simple",
        },
        "ChainOfThought": {
            "description": "Step-by-step reasoning",
            "best_for": ["complex reasoning", "explainability"],
            "complexity": "moderate",
        },
        "ReAct": {
            "description": "Reasoning + Acting with tools",
            "best_for": ["tool usage", "multi-step actions"],
            "complexity": "complex",
        },
        "ProgramOfThought": {
            "description": "Generates and executes code",
            "best_for": ["mathematical tasks", "computational problems"],
            "complexity": "complex",
        },
        "CodeAct": {
            "description": "Code-based actions",
            "best_for": ["programming tasks", "code generation"],
            "complexity": "complex",
        },
        "MultiChainComparison": {
            "description": "Multiple reasoning chains",
            "best_for": ["high accuracy needs", "quality over speed"],
            "complexity": "complex",
        },
        "BestOfN": {
            "description": "Generate N outputs, select best",
            "best_for": ["quality optimization", "have evaluation metric"],
            "complexity": "moderate",
        },
        "Refine": {
            "description": "Iteratively refine output",
            "best_for": ["polished output", "iterative improvement"],
            "complexity": "moderate",
        },
        "KNN": {
            "description": "K-nearest neighbors",
            "best_for": ["have labeled examples", "similarity-based"],
            "complexity": "moderate",
        },
        "Parallel": {
            "description": "Run multiple predictors",
            "best_for": ["multiple perspectives", "ensemble"],
            "complexity": "complex",
        },
    }

    def __init__(self):
        """Initialize the predictor validator."""

    def validate(self, tree: ast.AST, code_lines: list[str]) -> list[ValidationIssue]:
        """
        Validate predictor usage in code.

        Args:
            tree: AST of the code
            code_lines: Lines of source code

        Returns:
            List of validation issues
        """
        issues = []

        # Find all predictor usages
        predictors = self._find_predictors(tree)

        for predictor_info in predictors:
            # Check if signature is passed
            if not predictor_info["has_signature"]:
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.ERROR,
                        category=IssueCategory.PREDICTOR,
                        line=predictor_info["line"],
                        message=f"{predictor_info['type']} must be initialized with a signature",
                        suggestion="Pass a signature class to the predictor",
                        example=f"{predictor_info['type']}(MySignature)",
                        docs_link="https://dspy-docs.vercel.app/docs/building-blocks/predictors",
                    )
                )

            # Suggest better predictor if using Predict for complex tasks
            if predictor_info["type"] == "Predict":
                issues.append(
                    ValidationIssue(
                        severity=IssueSeverity.INFO,
                        category=IssueCategory.PREDICTOR,
                        line=predictor_info["line"],
                        message="Consider using ChainOfThought instead of Predict for better accuracy",
                        suggestion="ChainOfThought provides step-by-step reasoning which typically improves accuracy by 15-20%",
                        example=f"self.predictor = dspy.ChainOfThought({predictor_info.get('signature', 'Signature')})",
                    )
                )

        # Check for dspy.configure() call
        has_configure = self._has_configure_call(tree)
        if not has_configure and predictors:
            issues.append(
                ValidationIssue(
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.PREDICTOR,
                    line=1,
                    message="No dspy.configure() call found",
                    suggestion="Configure DSPy with a language model before using predictors",
                    example="lm = dspy.LM(model='ollama/llama3.2')\ndspy.configure(lm=lm)",
                    docs_link="https://dspy-docs.vercel.app/docs/quick-start/installation",
                )
            )

        return issues

    def _find_predictors(self, tree: ast.AST) -> list[dict]:
        """Find all predictor usages in the code."""
        predictors = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                predictor_info = self._analyze_predictor_call(node)
                if predictor_info:
                    predictors.append(predictor_info)

        return predictors

    def _analyze_predictor_call(self, call_node: ast.Call) -> dict | None:
        """Analyze a function call to see if it's a predictor."""
        func = call_node.func
        predictor_type = None

        # Check if it's a predictor call
        if isinstance(func, ast.Attribute):
            if func.attr in self.PREDICTORS:
                predictor_type = func.attr
        elif isinstance(func, ast.Name):
            if func.id in self.PREDICTORS:
                predictor_type = func.id

        if not predictor_type:
            return None

        # Check if signature is passed
        has_signature = len(call_node.args) > 0 or any(
            kw.arg == "signature" for kw in call_node.keywords
        )

        # Try to extract signature name
        signature_name = None
        if call_node.args:
            if isinstance(call_node.args[0], ast.Name):
                signature_name = call_node.args[0].id

        return {
            "type": predictor_type,
            "line": call_node.lineno,
            "has_signature": has_signature,
            "signature": signature_name,
        }

    def _has_configure_call(self, tree: ast.AST) -> bool:
        """Check if dspy.configure() is called."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func

                # Check for dspy.configure()
                if isinstance(func, ast.Attribute):
                    if func.attr == "configure":
                        if isinstance(func.value, ast.Name):
                            if func.value.id == "dspy":
                                return True
                # Check for configure() (imported directly)
                elif isinstance(func, ast.Name):
                    if func.id == "configure":
                        return True

        return False

    def suggest_predictor(self, task_description: str) -> str:
        """
        Suggest best predictor for a task.

        Args:
            task_description: Description of the task

        Returns:
            Suggested predictor name
        """
        task_lower = task_description.lower()

        # Simple keyword-based suggestions
        if any(word in task_lower for word in ["tool", "api", "action", "search"]):
            return "ReAct"
        elif any(word in task_lower for word in ["math", "calculate", "compute"]):
            return "ProgramOfThought"
        elif any(word in task_lower for word in ["code", "program", "implement"]):
            return "CodeAct"
        elif any(word in task_lower for word in ["reason", "explain", "analyze", "complex"]):
            return "ChainOfThought"
        elif any(word in task_lower for word in ["refine", "improve", "polish"]):
            return "Refine"
        elif any(word in task_lower for word in ["ensemble", "multiple", "combine"]):
            return "Parallel"
        else:
            # Default to ChainOfThought for most tasks
            return "ChainOfThought"

    def get_predictor_info(self, predictor_name: str) -> dict | None:
        """Get information about a predictor."""
        return self.PREDICTORS.get(predictor_name)

    def compare_predictors(self, predictor1: str, predictor2: str) -> dict:
        """
        Compare two predictors.

        Returns:
            Dict with comparison information
        """
        info1 = self.PREDICTORS.get(predictor1, {})
        info2 = self.PREDICTORS.get(predictor2, {})

        return {
            "predictor1": {
                "name": predictor1,
                "description": info1.get("description", "Unknown"),
                "best_for": info1.get("best_for", []),
                "complexity": info1.get("complexity", "unknown"),
            },
            "predictor2": {
                "name": predictor2,
                "description": info2.get("description", "Unknown"),
                "best_for": info2.get("best_for", []),
                "complexity": info2.get("complexity", "unknown"),
            },
        }
