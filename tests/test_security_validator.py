"""
Tests for security validator.
"""

import pytest
from hypothesis import given, strategies as st

from dspy_code.validation.security import SecurityValidator
from dspy_code.validation.models import IssueSeverity


class TestEvalDetection:
    """Tests for eval() detection."""

    # **Feature: dspy-code-improvements, Property 11: Eval Detection**
    @given(
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz \n", min_size=0, max_size=50),
        arg=st.text(alphabet="abcdefghijklmnopqrstuvwxyz_\"'", min_size=1, max_size=20),
    )
    def test_detects_eval_calls(self, prefix: str, arg: str):
        """
        Property 11: Eval Detection

        For any Python code containing an eval() call, the security validator
        SHALL produce a warning.

        **Validates: Requirements 8.1**
        """
        code = f"{prefix}\nresult = eval({arg})\n"
        validator = SecurityValidator()

        assert validator.has_eval(code), f"Should detect eval in: {code}"

    def test_detects_eval_with_whitespace(self):
        """Test detection of eval with various whitespace."""
        validator = SecurityValidator()

        assert validator.has_eval("eval('x')")
        assert validator.has_eval("eval ('x')")
        assert validator.has_eval("eval  ('x')")
        assert validator.has_eval("result = eval(expr)")

    def test_does_not_detect_eval_in_comments(self):
        """Test that eval in comments is not flagged."""
        validator = SecurityValidator()
        code = "# Don't use eval(x)\nprint('hello')"

        issues = validator.validate(code)
        assert len(issues) == 0

    def test_does_not_detect_evaluate_function(self):
        """Test that 'evaluate' is not flagged as eval."""
        validator = SecurityValidator()

        assert not validator.has_eval("evaluate(x)")
        assert not validator.has_eval("self.evaluate()")


class TestExecDetection:
    """Tests for exec() detection."""

    # **Feature: dspy-code-improvements, Property 12: Exec Detection**
    @given(
        prefix=st.text(alphabet="abcdefghijklmnopqrstuvwxyz \n", min_size=0, max_size=50),
        arg=st.text(alphabet="abcdefghijklmnopqrstuvwxyz_\"'", min_size=1, max_size=20),
    )
    def test_detects_exec_calls(self, prefix: str, arg: str):
        """
        Property 12: Exec Detection

        For any Python code containing an exec() call, the security validator
        SHALL produce a warning.

        **Validates: Requirements 8.2**
        """
        code = f"{prefix}\nexec({arg})\n"
        validator = SecurityValidator()

        assert validator.has_exec(code), f"Should detect exec in: {code}"

    def test_detects_exec_with_whitespace(self):
        """Test detection of exec with various whitespace."""
        validator = SecurityValidator()

        assert validator.has_exec("exec('x')")
        assert validator.has_exec("exec ('x')")
        assert validator.has_exec("exec  ('x')")

    def test_does_not_detect_execute_function(self):
        """Test that 'execute' is not flagged as exec."""
        validator = SecurityValidator()

        assert not validator.has_exec("execute(x)")
        assert not validator.has_exec("self.execute()")


class TestSecurityValidatorIntegration:
    """Integration tests for security validator."""

    def test_validate_returns_issues_for_dangerous_code(self):
        """Test that validate returns issues for dangerous patterns."""
        validator = SecurityValidator()
        code = """
def dangerous_function(user_input):
    result = eval(user_input)
    exec(user_input)
    return result
"""
        issues = validator.validate(code)

        # Should find both eval and exec
        assert len(issues) >= 2

        messages = [issue.message for issue in issues]
        assert any("eval" in msg.lower() for msg in messages)
        assert any("exec" in msg.lower() for msg in messages)

    def test_validate_returns_empty_for_safe_code(self):
        """Test that validate returns no issues for safe code."""
        validator = SecurityValidator()
        code = """
import ast

def safe_function(user_input):
    # Use ast.literal_eval instead of eval
    result = ast.literal_eval(user_input)
    return result
"""
        issues = validator.validate(code)
        assert len(issues) == 0

    def test_detects_os_system(self):
        """Test detection of os.system calls."""
        validator = SecurityValidator()
        code = "import os\nos.system('ls')"

        issues = validator.validate(code)
        assert len(issues) == 1
        assert "os.system" in issues[0].message

    def test_detects_subprocess_shell_true(self):
        """Test detection of subprocess with shell=True."""
        validator = SecurityValidator()
        code = "import subprocess\nsubprocess.run('ls', shell=True)"

        issues = validator.validate(code)
        assert len(issues) == 1
        assert "shell" in issues[0].message.lower()

    def test_issues_have_correct_line_numbers(self):
        """Test that issues have correct line numbers."""
        validator = SecurityValidator()
        code = """line 1
line 2
result = eval(x)
line 4
"""
        issues = validator.validate(code)
        assert len(issues) == 1
        assert issues[0].line == 3



class TestGeneratedCodeSafety:
    """Tests for generated code safety."""

    # **Feature: dspy-code-improvements, Property 13: Generated Code Safety**
    def test_generated_react_code_does_not_contain_eval(self):
        """
        Property 13: Generated Code Safety

        For any generated example code, the code SHALL NOT contain eval() calls.

        **Validates: Requirements 8.3**
        """
        from dspy_code.models.code_generator import CodeGenerator
        from dspy_code.models.task_collector import (
            FieldDefinition,
            ReasoningPattern,
            TaskDefinition,
        )

        # Create a mock model manager
        class MockModelManager:
            class MockConfigManager:
                class MockConfig:
                    default_model = None

                config = MockConfig()

            config_manager = MockConfigManager()

        # Create task definition that triggers ReAct pattern
        task_def = TaskDefinition(
            description="Answer questions using tools",
            input_fields=[
                FieldDefinition(name="question", type="str", description="The question")
            ],
            output_fields=[
                FieldDefinition(name="answer", type="str", description="The answer")
            ],
            complexity="complex",
            domain="qa",
        )

        # Generate with ReAct pattern
        generator = CodeGenerator(MockModelManager())
        pattern = ReasoningPattern(type="react", config={})

        program = generator.generate_from_task(task_def, [], pattern, use_cache=False)

        # Check that generated code doesn't contain eval()
        from dspy_code.validation.security import SecurityValidator

        validator = SecurityValidator()

        # Check module code (where calculator_tool is defined)
        assert not validator.has_eval(
            program.module_code
        ), f"Generated module code should not contain eval():\n{program.module_code}"
