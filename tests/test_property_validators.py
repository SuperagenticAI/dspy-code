"""
Property-based tests for DSPy Code validators.

These tests use hypothesis to verify that validators correctly handle
any well-formed DSPy code.
"""

import ast
import string

import pytest
from hypothesis import given, strategies as st, assume

from dspy_code.validation.validator import DSPyValidator
from dspy_code.validation.models import IssueSeverity


# Python keywords to avoid
import keyword
PYTHON_KEYWORDS = set(keyword.kwlist)

# Strategies for generating valid Python identifiers
valid_identifier_chars = string.ascii_letters + string.digits + "_"
identifier_strategy = st.text(
    alphabet=string.ascii_letters + "_",
    min_size=1,
    max_size=1
).flatmap(
    lambda first: st.text(
        alphabet=valid_identifier_chars,
        min_size=0,
        max_size=20
    ).map(lambda rest: first + rest)
).filter(lambda x: x.isidentifier() and not x.startswith("_") and x not in PYTHON_KEYWORDS)


# Strategy for generating field descriptions
description_strategy = st.text(
    alphabet=string.ascii_letters + string.digits + " ",
    min_size=1,
    max_size=50
).map(lambda s: s.strip()).filter(lambda s: len(s) > 0)


class TestSignatureValidatorProperties:
    """Property-based tests for signature validation."""

    # **Feature: dspy-code-improvements, Property 1: Signature Validator Correctness**
    @given(
        class_name=identifier_strategy.filter(lambda x: x[0].isupper()),
        input_field_name=identifier_strategy,
        output_field_name=identifier_strategy,
        input_desc=description_strategy,
        output_desc=description_strategy,
        docstring=description_strategy,
    )
    def test_valid_signature_passes_validation(
        self,
        class_name: str,
        input_field_name: str,
        output_field_name: str,
        input_desc: str,
        output_desc: str,
        docstring: str,
    ):
        """
        Property 1: Signature Validator Correctness
        
        For any well-formed DSPy signature (class inheriting from dspy.Signature
        with InputField and OutputField), the signature validator SHALL report no errors.
        
        **Validates: Requirements 2.1**
        """
        # Ensure field names are different
        assume(input_field_name != output_field_name)
        # Ensure class name doesn't conflict with Python keywords
        assume(class_name not in {"Signature", "Module", "InputField", "OutputField"})
        
        # Generate valid signature code
        code = f'''import dspy

class {class_name}(dspy.Signature):
    """{docstring}"""
    
    {input_field_name} = dspy.InputField(desc="{input_desc}")
    {output_field_name} = dspy.OutputField(desc="{output_desc}")
'''
        
        # Validate the code
        validator = DSPyValidator()
        report = validator.validate_code(code, "test_signature.py")
        
        # Should have no errors (warnings/info are acceptable)
        errors = [issue for issue in report.issues if issue.severity == IssueSeverity.ERROR]
        assert len(errors) == 0, f"Valid signature should have no errors, got: {errors}"


class TestModuleValidatorProperties:
    """Property-based tests for module validation."""

    # **Feature: dspy-code-improvements, Property 2: Module Validator Correctness**
    @given(
        module_name=identifier_strategy.filter(lambda x: x[0].isupper()),
        signature_name=identifier_strategy.filter(lambda x: x[0].isupper()),
        input_field=identifier_strategy,
        output_field=identifier_strategy,
        docstring=description_strategy,
    )
    def test_valid_module_passes_validation(
        self,
        module_name: str,
        signature_name: str,
        input_field: str,
        output_field: str,
        docstring: str,
    ):
        """
        Property 2: Module Validator Correctness
        
        For any well-formed DSPy module (class inheriting from dspy.Module
        with __init__ and forward methods), the module validator SHALL report no errors.
        
        **Validates: Requirements 2.2**
        """
        # Ensure names are different
        assume(module_name != signature_name)
        assume(input_field != output_field)
        assume(module_name not in {"Module", "Signature", "Predict"})
        assume(signature_name not in {"Module", "Signature", "Predict"})
        
        # Generate valid module code
        code = f'''import dspy

class {signature_name}(dspy.Signature):
    """{docstring}"""
    {input_field} = dspy.InputField()
    {output_field} = dspy.OutputField()

class {module_name}(dspy.Module):
    """{docstring}"""
    
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict({signature_name})
    
    def forward(self, {input_field}):
        """Execute the task."""
        return self.predictor({input_field}={input_field})
'''
        
        # Validate the code
        validator = DSPyValidator()
        report = validator.validate_code(code, "test_module.py")
        
        # Should have no errors
        errors = [issue for issue in report.issues if issue.severity == IssueSeverity.ERROR]
        assert len(errors) == 0, f"Valid module should have no errors, got: {errors}"


class TestCodeGeneratorProperties:
    """Property-based tests for code generation."""

    # Strategy for multi-word task descriptions
    task_description_strategy = st.lists(
        st.text(alphabet=string.ascii_letters, min_size=3, max_size=10),
        min_size=3,
        max_size=6
    ).map(lambda words: " ".join(words))

    # **Feature: dspy-code-improvements, Property 3: Code Generator Syntax Validity**
    @given(
        task_description=task_description_strategy,
        input_field_name=identifier_strategy,
        output_field_name=identifier_strategy,
        input_desc=description_strategy,
        output_desc=description_strategy,
    )
    def test_generated_code_is_syntactically_valid(
        self,
        task_description: str,
        input_field_name: str,
        output_field_name: str,
        input_desc: str,
        output_desc: str,
    ):
        """
        Property 3: Code Generator Syntax Validity
        
        For any valid TaskDefinition with non-empty input and output fields,
        the code generator SHALL produce Python code that parses without SyntaxError.
        
        **Validates: Requirements 2.3**
        """
        from dspy_code.models.task_collector import TaskDefinition, FieldDefinition, ReasoningPattern
        from dspy_code.models.code_generator import CodeGenerator
        
        # Ensure field names are different
        assume(input_field_name != output_field_name)
        
        # Create task definition
        task_def = TaskDefinition(
            description=task_description,
            input_fields=[
                FieldDefinition(
                    name=input_field_name,
                    type="str",
                    description=input_desc
                )
            ],
            output_fields=[
                FieldDefinition(
                    name=output_field_name,
                    type="str",
                    description=output_desc
                )
            ],
            complexity="simple",
            domain="general"
        )
        
        # Create a mock model manager
        class MockModelManager:
            class MockConfigManager:
                class MockConfig:
                    default_model = None
                config = MockConfig()
            config_manager = MockConfigManager()
        
        # Generate code
        generator = CodeGenerator(MockModelManager())
        pattern = ReasoningPattern(type="predict")
        
        program = generator.generate_from_task(task_def, [], pattern)
        
        # Test individual components parse correctly
        # Signature code
        sig_code = "import dspy\n\n" + program.signature_code
        try:
            ast.parse(sig_code)
        except SyntaxError as e:
            pytest.fail(f"Signature code has syntax error: {e}\n\nCode:\n{sig_code}")
        
        # Module code (needs signature)
        module_code = sig_code + "\n\n" + program.module_code
        try:
            ast.parse(module_code)
        except SyntaxError as e:
            pytest.fail(f"Module code has syntax error: {e}\n\nCode:\n{module_code}")


class TestConfigurationProperties:
    """Property-based tests for configuration handling."""

    # **Feature: dspy-code-improvements, Property 4: Configuration Round-Trip**
    @given(
        project_name=identifier_strategy,
        version=st.from_regex(r"[0-9]+\.[0-9]+\.[0-9]+", fullmatch=True),
        output_dir=identifier_strategy,
    )
    def test_configuration_round_trip(
        self,
        project_name: str,
        version: str,
        output_dir: str,
    ):
        """
        Property 4: Configuration Round-Trip
        
        For any valid ProjectConfig, serializing to YAML and deserializing
        SHALL produce an equivalent configuration.
        
        **Validates: Requirements 2.4**
        """
        import tempfile
        from pathlib import Path
        from dspy_code.core.config import ProjectConfig, ModelConfig, GepaConfig
        
        # Create a configuration
        config = ProjectConfig(
            name=project_name,
            version=version,
            output_directory=output_dir,
            models=ModelConfig(),
            gepa_config=GepaConfig(),
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            config.save_to_file(temp_path)
            
            # Load back
            loaded_config = ProjectConfig.load_from_file(temp_path)
            
            # Verify key fields match
            assert loaded_config.name == config.name
            assert loaded_config.version == config.version
            assert loaded_config.output_directory == config.output_directory
            assert loaded_config.gepa_config.max_iterations == config.gepa_config.max_iterations
            assert loaded_config.gepa_config.population_size == config.gepa_config.population_size
        finally:
            temp_path.unlink(missing_ok=True)


class TestDocumentationProperties:
    """Property-based tests for documentation coverage."""

    # **Feature: dspy-code-improvements, Property 14: Public Method Documentation**
    @given(st.sampled_from([
        # Core modules
        "dspy_code.core.config",
        "dspy_code.core.debug_logger",
        # MCP modules
        "dspy_code.mcp.utils",
        "dspy_code.mcp.retry",
        "dspy_code.mcp.client_manager",
        # Model modules
        "dspy_code.models.cache",
        "dspy_code.models.streaming",
        "dspy_code.models.code_generator",
        "dspy_code.models.model_manager",
        # Validation modules
        "dspy_code.validation.validator",
        "dspy_code.validation.security",
        "dspy_code.validation.signature_validator",
        "dspy_code.validation.module_validator",
        # Execution modules
        "dspy_code.execution.engine",
        # RAG modules
        "dspy_code.rag.codebase_rag",
    ]))
    def test_public_methods_have_docstrings(self, module_name: str):
        """
        Property 14: Public Method Documentation
        
        For any public method in the dspy_code package, the method SHALL have
        a non-empty docstring.
        
        **Validates: Requirements 9.2**
        """
        import importlib
        import inspect
        
        # Import the module
        module = importlib.import_module(module_name)
        
        # Get all classes in the module
        classes = inspect.getmembers(module, inspect.isclass)
        
        missing_docstrings = []
        
        for class_name, cls in classes:
            # Skip imported classes (only check classes defined in this module)
            if cls.__module__ != module_name:
                continue
            
            # Skip private classes
            if class_name.startswith("_"):
                continue
            
            # Check class docstring
            if not cls.__doc__ or not cls.__doc__.strip():
                missing_docstrings.append(f"{class_name} (class)")
            
            # Check public methods
            for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
                # Skip private methods
                if method_name.startswith("_"):
                    continue
                
                # Check method docstring
                if not method.__doc__ or not method.__doc__.strip():
                    missing_docstrings.append(f"{class_name}.{method_name}")
        
        # Also check module-level functions
        functions = inspect.getmembers(module, inspect.isfunction)
        for func_name, func in functions:
            # Skip imported functions
            if func.__module__ != module_name:
                continue
            
            # Skip private functions
            if func_name.startswith("_"):
                continue
            
            if not func.__doc__ or not func.__doc__.strip():
                missing_docstrings.append(f"{func_name} (function)")
        
        assert len(missing_docstrings) == 0, (
            f"Module {module_name} has public methods/classes without docstrings: "
            f"{missing_docstrings}"
        )
