"""
Tests for Project Scanner
"""

import tempfile
from pathlib import Path

import pytest

from dspy_code.project.scanner import ProjectScanner, ProjectType


@pytest.fixture
def scanner():
    """Create a project scanner instance."""
    return ProjectScanner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestProjectScanner:
    """Test project scanner initialization."""

    def test_scanner_initialization(self, scanner):
        """Should initialize with proper configuration."""
        assert scanner.dspy_imports is not None
        assert scanner.component_bases is not None
        assert scanner.predictor_types is not None


class TestEmptyDirectory:
    """Test scanning empty directories."""

    def test_detects_empty_directory(self, scanner, temp_dir):
        """Should detect empty directory."""
        state = scanner.scan_directory(str(temp_dir))

        assert state.project_type == ProjectType.EMPTY
        assert len(state.python_files) == 0
        assert len(state.dspy_files) == 0
        assert not state.has_config

    def test_empty_directory_summary(self, scanner, temp_dir):
        """Should provide summary for empty directory."""
        state = scanner.scan_directory(str(temp_dir))
        summary = scanner.get_summary(state)

        assert "Empty directory" in summary


class TestPythonProject:
    """Test scanning Python projects without DSPy."""

    def test_detects_python_project(self, scanner, temp_dir):
        """Should detect Python project without DSPy."""
        # Create a Python file without DSPy
        py_file = temp_dir / "main.py"
        py_file.write_text("print('Hello World')")

        state = scanner.scan_directory(str(temp_dir))

        assert state.project_type == ProjectType.PYTHON_PROJECT
        assert len(state.python_files) == 1
        assert len(state.dspy_files) == 0

    def test_python_project_summary(self, scanner, temp_dir):
        """Should provide summary for Python project."""
        py_file = temp_dir / "main.py"
        py_file.write_text("print('Hello')")

        state = scanner.scan_directory(str(temp_dir))
        summary = scanner.get_summary(state)

        assert "Python project" in summary
        assert "no DSPy" in summary


class TestDSPyProject:
    """Test scanning existing DSPy projects."""

    def test_detects_dspy_file(self, scanner, temp_dir):
        """Should detect file with DSPy import."""
        py_file = temp_dir / "module.py"
        py_file.write_text("import dspy\n\nclass MyModule(dspy.Module):\n    pass")

        state = scanner.scan_directory(str(temp_dir))

        assert state.project_type == ProjectType.EXISTING_DSPY
        assert len(state.dspy_files) == 1
        assert "module.py" in state.dspy_files

    def test_detects_config_file(self, scanner, temp_dir):
        """Should detect dspy_config.yaml."""
        config_file = temp_dir / "dspy_config.yaml"
        config_file.write_text("model: gpt-4")

        state = scanner.scan_directory(str(temp_dir))

        assert state.has_config
        assert state.config_path is not None

    def test_detects_dspy_md(self, scanner, temp_dir):
        """Should detect DSPy.md file."""
        md_file = temp_dir / "DSPy.md"
        md_file.write_text("# My DSPy Project")

        state = scanner.scan_directory(str(temp_dir))

        assert state.has_dspy_md


class TestComponentDetection:
    """Test detection of DSPy components."""

    def test_detects_signature(self, scanner, temp_dir):
        """Should detect DSPy signature."""
        py_file = temp_dir / "signatures.py"
        py_file.write_text("""
import dspy

class EmailClassifier(dspy.Signature):
    email: str = dspy.InputField()
    category: str = dspy.OutputField()
""")

        state = scanner.scan_directory(str(temp_dir))

        assert len(state.components["signatures"]) == 1
        assert state.components["signatures"][0].name == "EmailClassifier"

    def test_detects_module(self, scanner, temp_dir):
        """Should detect DSPy module."""
        py_file = temp_dir / "modules.py"
        py_file.write_text("""
import dspy

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):
        return x
""")

        state = scanner.scan_directory(str(temp_dir))

        assert len(state.components["modules"]) == 1
        assert state.components["modules"][0].name == "MyModule"

    def test_detects_multiple_components(self, scanner, temp_dir):
        """Should detect multiple components."""
        py_file = temp_dir / "app.py"
        py_file.write_text("""
import dspy

class MySignature(dspy.Signature):
    input: str = dspy.InputField()
    output: str = dspy.OutputField()

class MyModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(MySignature)

    def forward(self, input):
        return self.predictor(input=input)
""")

        state = scanner.scan_directory(str(temp_dir))

        assert len(state.components["signatures"]) == 1
        assert len(state.components["modules"]) == 1


class TestLMProviderDetection:
    """Test detection of LM providers."""

    def test_detects_openai(self, scanner, temp_dir):
        """Should detect OpenAI provider."""
        py_file = temp_dir / "config.py"
        py_file.write_text("""
import dspy

lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)
""")

        state = scanner.scan_directory(str(temp_dir))

        assert "openai" in state.lm_providers

    def test_detects_anthropic(self, scanner, temp_dir):
        """Should detect Anthropic provider."""
        py_file = temp_dir / "config.py"
        py_file.write_text("""
import dspy

lm = dspy.LM('anthropic/claude-3-sonnet')
dspy.configure(lm=lm)
""")

        state = scanner.scan_directory(str(temp_dir))

        assert "anthropic" in state.lm_providers

    def test_detects_multiple_providers(self, scanner, temp_dir):
        """Should detect multiple providers."""
        py_file1 = temp_dir / "config1.py"
        py_file1.write_text("lm = dspy.LM('openai/gpt-4')")

        py_file2 = temp_dir / "config2.py"
        py_file2.write_text("lm = dspy.LM('anthropic/claude-3')")

        state = scanner.scan_directory(str(temp_dir))

        assert "openai" in state.lm_providers
        assert "anthropic" in state.lm_providers


class TestSummaryGeneration:
    """Test summary generation."""

    def test_generates_summary_for_dspy_project(self, scanner, temp_dir):
        """Should generate comprehensive summary for DSPy project."""
        # Create DSPy project
        py_file = temp_dir / "app.py"
        py_file.write_text("""
import dspy

class MySignature(dspy.Signature):
    pass

class MyModule(dspy.Module):
    pass
""")

        config_file = temp_dir / "dspy_config.yaml"
        config_file.write_text("model: gpt-4")

        state = scanner.scan_directory(str(temp_dir))
        summary = scanner.get_summary(state)

        assert "Existing DSPy project" in summary
        assert "signatures" in summary
        assert "modules" in summary

    def test_summary_includes_file_counts(self, scanner, temp_dir):
        """Should include file counts in summary."""
        py_file = temp_dir / "app.py"
        py_file.write_text("import dspy")

        state = scanner.scan_directory(str(temp_dir))
        summary = scanner.get_summary(state)

        assert "1 DSPy files" in summary or "1 DSPy file" in summary


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_handles_invalid_python_files(self, scanner, temp_dir):
        """Should handle files with syntax errors."""
        py_file = temp_dir / "broken.py"
        py_file.write_text("import dspy\n\nclass Broken(")  # Syntax error

        # Should not crash
        state = scanner.scan_directory(str(temp_dir))

        assert state.project_type == ProjectType.EXISTING_DSPY

    def test_handles_binary_files(self, scanner, temp_dir):
        """Should handle binary files gracefully."""
        bin_file = temp_dir / "data.bin"
        bin_file.write_bytes(b"\x00\x01\x02\x03")

        # Should not crash
        state = scanner.scan_directory(str(temp_dir))

        assert state is not None

    def test_ignores_pycache(self, scanner, temp_dir):
        """Should ignore __pycache__ directories."""
        pycache = temp_dir / "__pycache__"
        pycache.mkdir()
        (pycache / "module.pyc").write_bytes(b"compiled")

        state = scanner.scan_directory(str(temp_dir))

        # Should not include pycache files
        assert not any("__pycache__" in f for f in state.python_files)

    def test_handles_nested_directories(self, scanner, temp_dir):
        """Should scan nested directories."""
        subdir = temp_dir / "src" / "modules"
        subdir.mkdir(parents=True)

        py_file = subdir / "module.py"
        py_file.write_text("import dspy\n\nclass MyModule(dspy.Module):\n    pass")

        state = scanner.scan_directory(str(temp_dir))

        assert len(state.dspy_files) == 1
        assert len(state.components["modules"]) == 1
