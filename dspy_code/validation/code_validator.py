"""
Code validation for generated DSPy components.

This module provides syntax and semantic validation for generated DSPy signatures,
modules, and complete programs.
"""

import ast
from typing import Any

from .exceptions import CodeValidationError


class CodeValidator:
    """Validates generated DSPy code for syntax and semantic correctness."""

    # Required imports for DSPy components
    REQUIRED_DSPY_IMPORTS = {
        "dspy",
        "dspy.Signature",
        "dspy.InputField",
        "dspy.OutputField",
        "dspy.Predict",
        "dspy.ChainOfThought",
        "dspy.ReAct",
    }

    # Allowed built-in functions in generated code
    ALLOWED_BUILTINS = {
        "len",
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "tuple",
        "set",
        "min",
        "max",
        "sum",
        "abs",
        "round",
        "sorted",
        "reversed",
        "enumerate",
        "zip",
        "range",
        "isinstance",
        "hasattr",
        "getattr",
        "type",
        "print",
    }

    # Dangerous functions that should not appear in generated code
    DANGEROUS_FUNCTIONS = {
        "eval",
        "exec",
        "compile",
        "__import__",
        "open",
        "file",
        "input",
        "raw_input",
        "reload",
        "vars",
        "globals",
        "locals",
        "dir",
        "delattr",
        "setattr",
        "getattr",
    }

    def __init__(self):
        pass

    def validate_python_syntax(self, code: str, filename: str = "<generated>") -> ast.AST:
        """
        Validate Python syntax of generated code.

        Args:
            code: The Python code to validate
            filename: Optional filename for error reporting

        Returns:
            Parsed AST tree

        Raises:
            CodeValidationError: If syntax validation fails
        """
        if not code or not code.strip():
            raise CodeValidationError("Code cannot be empty")

        try:
            tree = ast.parse(code, filename=filename)
            return tree
        except SyntaxError as e:
            raise CodeValidationError(
                f"Syntax error in generated code: {e.msg}",
                code_snippet=self._get_code_snippet(code, e.lineno),
                line_number=e.lineno,
            )
        except Exception as e:
            raise CodeValidationError(f"Failed to parse code: {e}")

    def validate_dspy_signature(self, code: str) -> dict[str, Any]:
        """
        Validate DSPy signature code.

        Args:
            code: The signature code to validate

        Returns:
            Dictionary with validation results and extracted information

        Raises:
            CodeValidationError: If validation fails
        """
        tree = self.validate_python_syntax(code, "<signature>")

        # Check for required DSPy imports
        imports = self._extract_imports(tree)
        if "dspy" not in imports and "dspy.Signature" not in imports:
            raise CodeValidationError("DSPy signature must import dspy or dspy.Signature")

        # Find signature class definition
        signature_classes = self._find_signature_classes(tree)
        if not signature_classes:
            raise CodeValidationError("No DSPy signature class found")

        if len(signature_classes) > 1:
            raise CodeValidationError("Multiple signature classes found, expected one")

        signature_class = signature_classes[0]

        # Validate signature structure
        validation_result = self._validate_signature_structure(signature_class, code)

        return validation_result

    def validate_dspy_module(self, code: str) -> dict[str, Any]:
        """
        Validate DSPy module code.

        Args:
            code: The module code to validate

        Returns:
            Dictionary with validation results and extracted information

        Raises:
            CodeValidationError: If validation fails
        """
        tree = self.validate_python_syntax(code, "<module>")

        # Check for required DSPy imports
        imports = self._extract_imports(tree)
        required_imports = {"dspy"}

        if not any(imp in imports for imp in required_imports):
            raise CodeValidationError("DSPy module must import dspy")

        # Find module class definition
        module_classes = self._find_module_classes(tree)
        if not module_classes:
            raise CodeValidationError("No DSPy module class found")

        if len(module_classes) > 1:
            raise CodeValidationError("Multiple module classes found, expected one")

        module_class = module_classes[0]

        # Validate module structure
        validation_result = self._validate_module_structure(module_class, code)

        return validation_result

    def validate_complete_program(self, code: str) -> dict[str, Any]:
        """
        Validate complete DSPy program.

        Args:
            code: The complete program code to validate

        Returns:
            Dictionary with validation results and extracted information

        Raises:
            CodeValidationError: If validation fails
        """
        tree = self.validate_python_syntax(code, "<program>")

        # Check for dangerous functions
        self._check_dangerous_functions(tree)

        # Validate imports
        imports = self._extract_imports(tree)
        self._validate_imports(imports)

        # Extract and validate components
        signature_classes = self._find_signature_classes(tree)
        module_classes = self._find_module_classes(tree)

        validation_result = {
            "syntax_valid": True,
            "imports": imports,
            "signature_classes": len(signature_classes),
            "module_classes": len(module_classes),
            "has_main_function": self._has_main_function(tree),
            "security_issues": [],
        }

        # Validate each signature
        for sig_class in signature_classes:
            try:
                self._validate_signature_structure(sig_class, code)
            except CodeValidationError as e:
                validation_result["security_issues"].append(f"Signature validation: {e}")

        # Validate each module
        for mod_class in module_classes:
            try:
                self._validate_module_structure(mod_class, code)
            except CodeValidationError as e:
                validation_result["security_issues"].append(f"Module validation: {e}")

        return validation_result

    def validate_field_definitions(self, fields: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Validate field definitions for DSPy signatures.

        Args:
            fields: List of field definitions with name, type, description

        Returns:
            Validated field definitions

        Raises:
            CodeValidationError: If validation fails
        """
        if not isinstance(fields, list):
            raise CodeValidationError("Field definitions must be a list")

        if not fields:
            raise CodeValidationError("At least one field must be defined")

        validated_fields = []
        field_names = set()

        for i, field in enumerate(fields):
            if not isinstance(field, dict):
                raise CodeValidationError(f"Field {i} must be a dictionary")

            required_keys = {"name", "type", "description"}
            if not all(key in field for key in required_keys):
                raise CodeValidationError(f"Field {i} must have keys: {', '.join(required_keys)}")

            field_name = field["name"]
            if field_name in field_names:
                raise CodeValidationError(f"Duplicate field name: {field_name}")
            field_names.add(field_name)

            # Validate field name as Python identifier
            if not field_name.isidentifier():
                raise CodeValidationError(
                    f"Field name '{field_name}' is not a valid Python identifier"
                )

            validated_fields.append(field)

        return validated_fields

    def _extract_imports(self, tree: ast.AST) -> set[str]:
        """Extract all imports from AST."""
        imports = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.add(f"{node.module}.{alias.name}")
                        imports.add(node.module)

        return imports

    def _find_signature_classes(self, tree: ast.AST) -> list[ast.ClassDef]:
        """Find DSPy signature classes in AST."""
        signature_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from dspy.Signature
                for base in node.bases:
                    if (
                        isinstance(base, ast.Attribute)
                        and isinstance(base.value, ast.Name)
                        and base.value.id == "dspy"
                        and base.attr == "Signature"
                    ) or (isinstance(base, ast.Name) and base.id == "Signature"):
                        signature_classes.append(node)

        return signature_classes

    def _find_module_classes(self, tree: ast.AST) -> list[ast.ClassDef]:
        """Find DSPy module classes in AST."""
        module_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if class inherits from dspy.Module
                for base in node.bases:
                    if (
                        isinstance(base, ast.Attribute)
                        and isinstance(base.value, ast.Name)
                        and base.value.id == "dspy"
                        and base.attr == "Module"
                    ) or (isinstance(base, ast.Name) and base.id == "Module"):
                        module_classes.append(node)

        return module_classes

    def _validate_signature_structure(self, class_node: ast.ClassDef, code: str) -> dict[str, Any]:
        """Validate the structure of a DSPy signature class."""
        result = {
            "class_name": class_node.name,
            "input_fields": [],
            "output_fields": [],
            "docstring": None,
        }

        # Extract docstring
        if (
            class_node.body
            and isinstance(class_node.body[0], ast.Expr)
            and isinstance(class_node.body[0].value, ast.Constant)
        ):
            result["docstring"] = class_node.body[0].value.value

        # Find field definitions
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        field_name = target.id

                        # Check if it's an InputField or OutputField
                        if isinstance(node.value, ast.Call):
                            if (
                                isinstance(node.value.func, ast.Attribute)
                                and isinstance(node.value.func.value, ast.Name)
                                and node.value.func.value.id == "dspy"
                            ):
                                if node.value.func.attr == "InputField":
                                    result["input_fields"].append(field_name)
                                elif node.value.func.attr == "OutputField":
                                    result["output_fields"].append(field_name)

        # Validate that we have at least one input and one output field
        if not result["input_fields"]:
            raise CodeValidationError("Signature must have at least one InputField")

        if not result["output_fields"]:
            raise CodeValidationError("Signature must have at least one OutputField")

        return result

    def _validate_module_structure(self, class_node: ast.ClassDef, code: str) -> dict[str, Any]:
        """Validate the structure of a DSPy module class."""
        result = {
            "class_name": class_node.name,
            "has_init": False,
            "has_forward": False,
            "predictor_types": [],
        }

        # Check for required methods
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                if node.name == "__init__":
                    result["has_init"] = True
                elif node.name == "forward":
                    result["has_forward"] = True

        # Find predictor assignments in __init__
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                for stmt in node.body:
                    if isinstance(stmt, ast.Assign):
                        for target in stmt.targets:
                            if (
                                isinstance(target, ast.Attribute)
                                and isinstance(target.value, ast.Name)
                                and target.value.id == "self"
                            ):
                                if isinstance(stmt.value, ast.Call):
                                    if (
                                        isinstance(stmt.value.func, ast.Attribute)
                                        and isinstance(stmt.value.func.value, ast.Name)
                                        and stmt.value.func.value.id == "dspy"
                                    ):
                                        result["predictor_types"].append(stmt.value.func.attr)

        # Validate required methods
        if not result["has_init"]:
            raise CodeValidationError("Module must have __init__ method")

        if not result["has_forward"]:
            raise CodeValidationError("Module must have forward method")

        return result

    def _check_dangerous_functions(self, tree: ast.AST):
        """Check for dangerous function calls in the code."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = None

                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name in self.DANGEROUS_FUNCTIONS:
                    raise CodeValidationError(
                        f"Dangerous function '{func_name}' not allowed in generated code"
                    )

    def _validate_imports(self, imports: set[str]):
        """Validate that imports are safe and appropriate."""
        dangerous_modules = {
            "os",
            "sys",
            "subprocess",
            "importlib",
            "__builtin__",
            "builtins",
            "eval",
            "exec",
            "compile",
            "file",
            "input",
            "raw_input",
        }

        for imp in imports:
            base_module = imp.split(".")[0]
            if base_module in dangerous_modules:
                raise CodeValidationError(
                    f"Import of potentially dangerous module '{base_module}' not allowed"
                )

    def _has_main_function(self, tree: ast.AST) -> bool:
        """Check if the code has a main function or if __name__ == '__main__' block."""
        for node in ast.walk(tree):
            if (isinstance(node, ast.FunctionDef) and node.name == "main") or (
                isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and isinstance(node.test.left, ast.Name)
                and node.test.left.id == "__name__"
            ):
                return True
        return False

    def _get_code_snippet(self, code: str, line_number: int | None = None) -> str:
        """Get a snippet of code around the specified line number."""
        if not line_number:
            return code[:200] + "..." if len(code) > 200 else code

        lines = code.split("\n")
        start = max(0, line_number - 3)
        end = min(len(lines), line_number + 2)

        snippet_lines = []
        for i in range(start, end):
            marker = ">>> " if i == line_number - 1 else "    "
            snippet_lines.append(f"{marker}{i + 1}: {lines[i]}")

        return "\n".join(snippet_lines)
