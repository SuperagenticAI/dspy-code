"""
Unit tests for export/import functionality.
"""

import json
import tempfile
from pathlib import Path

import pytest

from dspy_code.core.exceptions import ExportError, ImportError
from dspy_code.export import ExportImportHandler, PackageBuilder, PackageMetadata


@pytest.fixture
def temp_export_dir():
    """Create temporary export directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def export_handler(temp_export_dir):
    """Create export handler with temp directory."""
    handler = ExportImportHandler()
    handler.export_dir = temp_export_dir
    return handler


@pytest.fixture
def package_builder():
    """Create package builder."""
    return PackageBuilder()


@pytest.fixture
def sample_code():
    """Sample code for testing."""
    return """
import dspy

class TestModule(dspy.Module):
    def __init__(self):
        super().__init__()

    def forward(self, text):
        return text
"""


def test_export_code_python(export_handler, sample_code, temp_export_dir):
    """Test exporting code as Python."""
    output_path = temp_export_dir / "test.py"

    export_handler.export_code(sample_code, "python", output_path)

    assert output_path.exists()
    assert output_path.read_text() == sample_code


def test_export_code_json(export_handler, sample_code, temp_export_dir):
    """Test exporting code as JSON."""
    output_path = temp_export_dir / "test.json"

    export_handler.export_code(sample_code, "json", output_path)

    assert output_path.exists()

    data = json.loads(output_path.read_text())
    assert data["code"] == sample_code
    assert "exported_at" in data


def test_export_code_markdown(export_handler, sample_code, temp_export_dir):
    """Test exporting code as Markdown."""
    output_path = temp_export_dir / "test.md"

    export_handler.export_code(sample_code, "markdown", output_path)

    assert output_path.exists()
    content = output_path.read_text()
    assert "```python" in content
    assert sample_code in content


def test_export_code_invalid_format(export_handler, sample_code, temp_export_dir):
    """Test exporting with invalid format raises error."""
    output_path = temp_export_dir / "test.txt"

    with pytest.raises(ExportError):
        export_handler.export_code(sample_code, "invalid", output_path)


def test_export_config(export_handler, temp_export_dir):
    """Test exporting configuration."""
    config = {"default_model": "gpt-4", "output_directory": "generated", "log_level": "INFO"}

    output_path = temp_export_dir / "config.yaml"
    export_handler.export_config(config, output_path)

    assert output_path.exists()


def test_export_conversation_markdown(export_handler):
    """Test exporting conversation as Markdown."""
    history = [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi there!"}]

    result = export_handler.export_conversation(history, "markdown")

    assert "# Conversation History" in result
    assert "## User" in result
    assert "Hello" in result


def test_export_conversation_json(export_handler):
    """Test exporting conversation as JSON."""
    history = [{"role": "user", "content": "Hello"}]

    result = export_handler.export_conversation(history, "json")

    data = json.loads(result)
    assert len(data) == 1
    assert data[0]["role"] == "user"


def test_import_session(export_handler, temp_export_dir):
    """Test importing session."""
    # Create session file
    session_data = {
        "version": "1.0.0",
        "timestamp": "2025-01-01T12:00:00",
        "conversation_history": [{"role": "user", "content": "test"}],
        "current_context": {},
        "generated_files": [],
        "model_config": {},
        "metadata": {},
    }

    session_file = temp_export_dir / "test_session.json"
    session_file.write_text(json.dumps(session_data))

    # Import
    imported = export_handler.import_session(session_file)

    assert imported["version"] == "1.0.0"
    assert len(imported["conversation_history"]) == 1


def test_import_session_missing_file(export_handler, temp_export_dir):
    """Test importing non-existent session raises error."""
    with pytest.raises(ImportError):
        export_handler.import_session(temp_export_dir / "nonexistent.json")


def test_import_session_invalid_format(export_handler, temp_export_dir):
    """Test importing invalid session format raises error."""
    # Create invalid session file
    session_file = temp_export_dir / "invalid.json"
    session_file.write_text(json.dumps({"invalid": "data"}))

    with pytest.raises(ImportError):
        export_handler.import_session(session_file)


def test_package_metadata():
    """Test PackageMetadata dataclass."""
    metadata = PackageMetadata(
        name="test-package",
        version="1.0.0",
        description="Test package",
        author="Test Author",
        dependencies=["dspy>=3.0.4"],
    )

    assert metadata.name == "test-package"
    assert metadata.python_requires == ">=3.10"
    assert metadata.license == "MIT"


def test_build_package(package_builder, sample_code, temp_export_dir):
    """Test building Python package."""
    metadata = PackageMetadata(
        name="test_package",
        version="0.1.0",
        description="Test package",
        author="Test",
        dependencies=["dspy>=3.0.4"],
    )

    package_dir = package_builder.build_package(
        sample_code, "test_package", metadata, temp_export_dir
    )

    assert package_dir.exists()
    assert (package_dir / "setup.py").exists()
    assert (package_dir / "README.md").exists()
    assert (package_dir / "requirements.txt").exists()
    assert (package_dir / "test_package" / "module.py").exists()
    assert (package_dir / "examples").exists()
    assert (package_dir / "tests").exists()


def test_generate_setup_py(package_builder):
    """Test setup.py generation."""
    metadata = PackageMetadata(
        name="test-pkg",
        version="1.0.0",
        description="Test",
        author="Author",
        dependencies=["dspy>=3.0.4", "pytest"],
    )

    setup_content = package_builder.generate_setup_py(metadata)

    assert 'name="test-pkg"' in setup_content
    assert 'version="1.0.0"' in setup_content
    assert "dspy>=3.0.4" in setup_content
    assert "pytest" in setup_content


def test_generate_readme(package_builder, sample_code):
    """Test README generation."""
    metadata = PackageMetadata(
        name="test-pkg",
        version="1.0.0",
        description="Test package",
        author="Author",
        dependencies=["dspy>=3.0.4"],
    )

    readme = package_builder.generate_readme(sample_code, metadata)

    assert "# test-pkg" in readme
    assert "Test package" in readme
    assert "Installation" in readme
    assert "Usage" in readme


def test_create_examples(package_builder, sample_code):
    """Test example script generation."""
    examples = package_builder.create_examples(sample_code, "test_pkg")

    assert "basic_usage.py" in examples
    assert "advanced_usage.py" in examples
    assert "import dspy" in examples["basic_usage.py"]
    assert "from test_pkg import module" in examples["basic_usage.py"]


def test_export_session_bundle(export_handler, temp_export_dir):
    """Test exporting complete session bundle."""
    session_data = {
        "version": "1.0.0",
        "timestamp": "2025-01-01T12:00:00",
        "conversation_history": [],
        "current_context": {},
        "generated_files": [],
        "model_config": {},
        "metadata": {},
    }

    bundle_dir = export_handler.export_session_bundle(session_data, [], temp_export_dir)

    assert bundle_dir.exists()
    assert (bundle_dir / "session.json").exists()
    assert (bundle_dir / "code").exists()
    assert (bundle_dir / "README.md").exists()


def test_package_structure_completeness(package_builder, sample_code, temp_export_dir):
    """Test that package has all required files."""
    metadata = PackageMetadata(
        name="complete_pkg",
        version="1.0.0",
        description="Complete test",
        author="Test",
        dependencies=["dspy>=3.0.4"],
    )

    package_dir = package_builder.build_package(
        sample_code, "complete_pkg", metadata, temp_export_dir
    )

    # Check all required files
    required_files = [
        "setup.py",
        "README.md",
        "requirements.txt",
        "complete_pkg/__init__.py",
        "complete_pkg/module.py",
        "examples/basic_usage.py",
        "examples/advanced_usage.py",
        "tests/__init__.py",
        "tests/test_module.py",
    ]

    for file_path in required_files:
        assert (package_dir / file_path).exists(), f"Missing: {file_path}"
