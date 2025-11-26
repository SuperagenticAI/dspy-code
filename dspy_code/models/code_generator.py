"""
Code generator for creating DSPy components from task definitions.
"""

from dataclasses import dataclass

from rich.console import Console

from ..core.logging import get_logger
from .task_collector import GoldExample, ReasoningPattern, TaskDefinition

console = Console()
logger = get_logger(__name__)


@dataclass
class GeneratedProgram:
    """Complete generated DSPy program."""

    signature_code: str
    module_code: str
    program_code: str
    imports: list[str]
    dependencies: list[str]
    documentation: str
    examples: list[str]
    reasoning_pattern: ReasoningPattern


class CodeGenerator:
    """Generates DSPy code from task definitions."""

    def __init__(self, model_manager):
        self.model_manager = model_manager

    def generate_from_task(
        self, task_def: TaskDefinition, examples: list[GoldExample], pattern: ReasoningPattern
    ) -> GeneratedProgram:
        """
        Generate complete DSPy program from task definition.

        Args:
            task_def: Task definition
            examples: Gold examples
            pattern: Reasoning pattern

        Returns:
            Generated program
        """
        logger.info(f"Generating DSPy program for task: {task_def.description}")

        # Generate signature
        signature_code = self._generate_signature(task_def)

        # Generate module based on reasoning pattern
        module_code = self._generate_module(task_def, pattern)

        # Generate main program
        program_code = self._generate_program(task_def, examples)

        # Generate imports
        imports = self._generate_imports(pattern)

        # Generate documentation
        documentation = self._generate_documentation(task_def, pattern, examples)

        # Generate usage examples
        usage_examples = self._generate_usage_examples(task_def, examples)

        return GeneratedProgram(
            signature_code=signature_code,
            module_code=module_code,
            program_code=program_code,
            imports=imports,
            dependencies=["dspy>=3.0.4"],
            documentation=documentation,
            examples=usage_examples,
            reasoning_pattern=pattern,
        )

    def _generate_signature(self, task_def: TaskDefinition) -> str:
        """Generate DSPy signature from task definition."""

        # Create class name from task description
        class_name = self._create_class_name(task_def.description)

        # Generate input fields
        input_fields = []
        for field in task_def.input_fields:
            field_line = f'    {field.name} = dspy.InputField(desc="{field.description}")'
            input_fields.append(field_line)

        # Generate output fields
        output_fields = []
        for field in task_def.output_fields:
            field_line = f'    {field.name} = dspy.OutputField(desc="{field.description}")'
            output_fields.append(field_line)

        signature_code = f'''class {class_name}(dspy.Signature):
    """{task_def.description}"""

{chr(10).join(input_fields)}
{chr(10).join(output_fields)}'''

        return signature_code

    def _generate_module(self, task_def: TaskDefinition, pattern: ReasoningPattern) -> str:
        """Generate DSPy module based on reasoning pattern."""

        class_name = self._create_class_name(task_def.description)
        module_name = f"{class_name}Module"

        # Choose predictor based on pattern
        if pattern.type == "predict":
            predictor_type = "dspy.Predict"
        elif pattern.type == "chain_of_thought":
            predictor_type = "dspy.ChainOfThought"
        elif pattern.type == "react":
            predictor_type = "dspy.ReAct"
        else:
            predictor_type = "dspy.Predict"

        # CRITICAL: ReAct requires tools!
        if pattern.type == "react":
            module_code = f'''# Example tool functions (customize for your use case)
def search_tool(query: str) -> str:
    """Search for information."""
    # Replace with real search API
    return f"Search results for: {{query}}"

def calculator_tool(expression: str) -> str:
    """Evaluate mathematical expressions."""
    try:
        result = eval(expression, {{"__builtins__": {{}}}}, {{}})
        return f"Result: {{result}}"
    except Exception as e:
        return f"Error: {{str(e)}}"

class {module_name}(dspy.Module):
    """DSPy ReAct module for {task_def.description.lower()} with tools."""

    def __init__(self):
        super().__init__()

        # Define tools
        from dspy import Tool
        self.tools = [
            Tool(func=search_tool, name="search", desc="Search for information"),
            Tool(func=calculator_tool, name="calculator", desc="Perform calculations")
        ]

        # Create ReAct predictor with tools
        self.predictor = {predictor_type}({class_name}, tools=self.tools)

    def forward(self, {self._get_forward_params(task_def)}):
        """Execute the {task_def.description.lower()} task using ReAct reasoning."""
        result = self.predictor({self._get_predictor_call(task_def)})
        return result'''
        else:
            module_code = f'''class {module_name}(dspy.Module):
    """DSPy module for {task_def.description.lower()}"""

    def __init__(self):
        super().__init__()
        self.predictor = {predictor_type}({class_name})

    def forward(self, {self._get_forward_params(task_def)}):
        """Execute the {task_def.description.lower()} task."""
        result = self.predictor({self._get_predictor_call(task_def)})
        return result'''

        return module_code

    def _generate_program(self, task_def: TaskDefinition, examples: list[GoldExample]) -> str:
        """Generate main program code that aligns with the model you use in DSPy Code."""

        class_name = self._create_class_name(task_def.description)
        module_name = f"{class_name}Module"

        # Try to infer a default model from config (used as a hint in comments)
        try:
            default_model = self.model_manager.config_manager.config.default_model
        except Exception:  # pragma: no cover - defensive
            default_model = None

        if default_model:
            lm_comment = (
                f'# lm = dspy.LM(model="{default_model}")  # Uses your configured default model\n'
                f"# dspy.configure(lm=lm)\n"
            )
        else:
            lm_comment = (
                '# lm = dspy.LM("ollama/llama3.2:1b", api_base="http://localhost:11434")\n'
                '# or: lm = dspy.LM("openai/gpt-5-nano")\n'
                '# or: lm = dspy.LM("anthropic/claude-sonnet-4.5")\n'
                '# or: lm = dspy.LM("gemini/gemini-2.5-flash")\n'
                "# dspy.configure(lm=lm)\n"
            )

        # Generate example usage
        example_usage = ""
        if examples:
            example = examples[0]  # Use first example
            input_args = ", ".join(f'{k}="{v}"' for k, v in example.inputs.items())

            example_usage = f"""
    # Example usage
    module = {module_name}()
    result = module({input_args})

    print("Result:")
    for key, value in result.__dict__.items():
        if not key.startswith('_'):
            print(f"{{key}}: {{value}}")"""

        program_code = f'''def main():
    """Main function to demonstrate the {task_def.description.lower()} module."""
    import dspy

    # Configure DSPy with the same model you use in DSPy Code.
    # For example, if you connected via /model or /connect:
    # - Ollama:   lm = dspy.LM("ollama/llama3.2:1b", api_base="http://localhost:11434")
    # - OpenAI:   lm = dspy.LM("openai/gpt-5-nano")
    # - Claude:   lm = dspy.LM("anthropic/claude-sonnet-4.5")
    # - Gemini:   lm = dspy.LM("gemini/gemini-2.5-flash")
    # Or use the default_model from dspy_config.yaml:
    {lm_comment.rstrip()}

    {example_usage}

if __name__ == "__main__":
    main()'''

        return program_code

    def _generate_imports(self, pattern: ReasoningPattern) -> list[str]:
        """Generate necessary imports."""
        imports = ["import dspy"]

        # Add pattern-specific imports if needed
        if pattern.type == "react":
            imports.append("from dspy.tools import *")

        return imports

    def _generate_documentation(
        self, task_def: TaskDefinition, pattern: ReasoningPattern, examples: list[GoldExample]
    ) -> str:
        """Generate comprehensive documentation."""

        doc = f"""DSPy Component: {self._create_class_name(task_def.description)}

Task Description:
{task_def.description}

Reasoning Pattern: {pattern.type.replace("_", " ").title()}

Input Fields:
{chr(10).join(f"- {f.name} ({f.type}): {f.description}" for f in task_def.input_fields)}

Output Fields:
{chr(10).join(f"- {f.name} ({f.type}): {f.description}" for f in task_def.output_fields)}

Complexity: {task_def.complexity}
Domain: {task_def.domain or "General"}

Examples Provided: {len(examples)}

Usage:
1. Configure your language model with dspy.configure()
2. Instantiate the module
3. Call with appropriate inputs
4. Process the results

This component was generated by DSPy Code."""

        return doc

    def _generate_usage_examples(
        self, task_def: TaskDefinition, examples: list[GoldExample]
    ) -> list[str]:
        """Generate usage example code."""

        module_name = f"{self._create_class_name(task_def.description)}Module"
        usage_examples = []

        # Basic usage
        usage_examples.append("# Basic usage")
        usage_examples.append(f"module = {module_name}()")

        if examples:
            # Use first example for demonstration
            example = examples[0]
            input_args = ", ".join(f'{k}="{v}"' for k, v in example.inputs.items())
            usage_examples.append(f"result = module({input_args})")
            usage_examples.append("print(result)")
        else:
            # Generic example
            input_params = ", ".join(f'{f.name}="example_{f.name}"' for f in task_def.input_fields)
            usage_examples.append(f"result = module({input_params})")
            usage_examples.append("print(result)")

        return usage_examples

    def _create_class_name(self, description: str) -> str:
        """Create a valid Python class name from task description."""
        # Extract key words and create PascalCase name
        words = description.replace(",", "").replace(".", "").split()
        key_words = [
            w
            for w in words
            if len(w) > 2
            and w.lower() not in {"the", "and", "or", "but", "for", "with", "from", "into", "to"}
        ]

        # Take first 3-4 meaningful words
        class_words = key_words[:3] if len(key_words) >= 3 else key_words

        # Convert to PascalCase
        class_name = "".join(word.capitalize() for word in class_words)

        # Ensure it's a valid identifier
        if not class_name or not class_name[0].isalpha():
            class_name = "Task" + class_name

        return class_name

    def _get_forward_params(self, task_def: TaskDefinition) -> str:
        """Get forward method parameters."""
        return ", ".join(field.name for field in task_def.input_fields)

    def _get_predictor_call(self, task_def: TaskDefinition) -> str:
        """Get predictor call arguments."""
        return ", ".join(f"{field.name}={field.name}" for field in task_def.input_fields)
