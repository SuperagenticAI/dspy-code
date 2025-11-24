"""
Package builder for DSPy Code.

Creates distributable Python packages from generated code.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ..core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PackageMetadata:
    """Metadata for Python package."""

    name: str
    version: str
    description: str
    author: str
    dependencies: list[str]
    python_requires: str = ">=3.10"
    license: str = "MIT"


class PackageBuilder:
    """Builds distributable Python packages."""

    def __init__(self, config_manager=None):
        """
        Initialize package builder.

        Args:
            config_manager: Optional configuration manager
        """
        self.config_manager = config_manager

    def build_package(
        self, code: str, package_name: str, metadata: PackageMetadata, output_dir: Path
    ) -> Path:
        """
        Build a complete Python package.

        Args:
            code: Generated code
            package_name: Package name
            metadata: Package metadata
            output_dir: Output directory

        Returns:
            Path to package directory
        """
        # Create package directory
        package_dir = output_dir / package_name
        package_dir.mkdir(parents=True, exist_ok=True)

        # Create package structure
        src_dir = package_dir / package_name
        src_dir.mkdir(exist_ok=True)

        # Write main module
        module_file = src_dir / "module.py"
        module_file.write_text(code)

        # Write __init__.py
        init_file = src_dir / "__init__.py"
        init_file.write_text(self._generate_init(package_name))

        # Write setup.py
        setup_file = package_dir / "setup.py"
        setup_file.write_text(self.generate_setup_py(metadata))

        # Write requirements.txt
        req_file = package_dir / "requirements.txt"
        req_file.write_text("\n".join(metadata.dependencies))

        # Write README.md
        readme_file = package_dir / "README.md"
        readme_file.write_text(self.generate_readme(code, metadata))

        # Create examples directory
        examples_dir = package_dir / "examples"
        examples_dir.mkdir(exist_ok=True)

        # Write example scripts
        examples = self.create_examples(code, package_name)
        for name, content in examples.items():
            (examples_dir / name).write_text(content)

        # Create tests directory
        tests_dir = package_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        (tests_dir / "__init__.py").write_text("")
        (tests_dir / "test_module.py").write_text(self._generate_test_template(package_name))

        logger.info(f"Built package at {package_dir}")
        return package_dir

    def generate_setup_py(self, metadata: PackageMetadata) -> str:
        """
        Generate setup.py with dependencies.

        Args:
            metadata: Package metadata

        Returns:
            setup.py content
        """
        deps_str = ",\n        ".join([f'"{dep}"' for dep in metadata.dependencies])

        return f'''"""
{metadata.description}
"""

from setuptools import setup, find_packages

setup(
    name="{metadata.name}",
    version="{metadata.version}",
    description="{metadata.description}",
    author="{metadata.author}",
    license="{metadata.license}",
    packages=find_packages(),
    python_requires="{metadata.python_requires}",
    install_requires=[
        {deps_str}
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
'''

    def generate_readme(self, code: str, metadata: PackageMetadata) -> str:
        """
        Generate README with usage instructions.

        Args:
            code: Generated code
            metadata: Package metadata

        Returns:
            README content
        """
        return f"""# {metadata.name}

{metadata.description}

## Installation

```bash
pip install {metadata.name}
```

Or install from source:

```bash
git clone <repository-url>
cd {metadata.name}
pip install -e .
```

## Requirements

- Python {metadata.python_requires}
- Dependencies: {", ".join(metadata.dependencies)}

## Usage

```python
from {metadata.name} import module

# Configure DSPy
import dspy
lm = dspy.LM(model='openai/gpt-4')
dspy.configure(lm=lm)

# Use the module
# See examples/ directory for more usage examples
```

## Examples

Check the `examples/` directory for complete usage examples:

- `basic_usage.py` - Basic usage example
- `advanced_usage.py` - Advanced usage with configuration

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black {metadata.name}/
```

## License

{metadata.license}

## Generated

This package was generated using DSPy Code on {datetime.now().strftime("%Y-%m-%d")}.
"""

    def create_examples(self, code: str, package_name: str) -> dict[str, str]:
        """
        Generate example usage scripts.

        Args:
            code: Generated code
            package_name: Package name

        Returns:
            Dictionary of example filename to content
        """
        basic_example = f'''"""
Basic usage example for {package_name}.
"""

import dspy
from {package_name} import module

# Configure DSPy with your language model
lm = dspy.LM(model='openai/gpt-4')
dspy.configure(lm=lm)

# Create an instance of the module
my_module = module.YourModule()

# Use the module
result = my_module(input_text="Your input here")
print(f"Result: {{result}}")
'''

        advanced_example = f'''"""
Advanced usage example for {package_name}.
"""

import dspy
from {package_name} import module

# Configure DSPy with custom settings
lm = dspy.LM(
    model='openai/gpt-4',
    temperature=0.7,
    max_tokens=1000
)
dspy.configure(lm=lm)

# Create module instance
my_module = module.YourModule()

# Process multiple inputs
inputs = [
    "First input",
    "Second input",
    "Third input"
]

results = []
for inp in inputs:
    result = my_module(input_text=inp)
    results.append(result)
    print(f"Input: {{inp}}")
    print(f"Result: {{result}}\\n")

# Summary
print(f"Processed {{len(results)}} inputs")
'''

        return {"basic_usage.py": basic_example, "advanced_usage.py": advanced_example}

    def _generate_init(self, package_name: str) -> str:
        """Generate __init__.py content."""
        return f'''"""
{package_name} - DSPy module package.
"""

from .module import *

__version__ = "0.1.0"
'''

    def _generate_test_template(self, package_name: str) -> str:
        """Generate test template."""
        return f'''"""
Tests for {package_name}.
"""

import pytest
import dspy
from {package_name} import module


def test_module_exists():
    """Test that module can be imported."""
    assert hasattr(module, 'YourModule')


def test_module_initialization():
    """Test module initialization."""
    # Configure DSPy for testing
    lm = dspy.LM(model='openai/gpt-4')
    dspy.configure(lm=lm)

    # Create module instance
    my_module = module.YourModule()
    assert my_module is not None


# Add more tests as needed
'''
