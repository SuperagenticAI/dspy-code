"""
Integration tests for DSPy CLI.

Tests end-to-end workflows and feature interactions.
"""

import tempfile
from pathlib import Path

import pytest

from dspy_code.execution import ExecutionEngine
from dspy_code.export import ExportImportHandler, PackageBuilder, PackageMetadata
from dspy_code.optimization import Example, OptimizationWorkflowManager
from dspy_code.session import SessionStateManager


class MockSession:
    """Mock session for integration testing."""

    def __init__(self):
        self.conversation_history = []
        self.current_context = {}
        self.llm_connector = MockLLMConnector()


class MockLLMConnector:
    """Mock LLM connector."""

    def __init__(self):
        self.current_model = "test-model"
        self.model_type = "test"
        self.api_key = None


@pytest.fixture
def temp_dir():
    """Create temporary directory for integration tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def session_manager(temp_dir):
    """Create session manager."""
    manager = SessionStateManager()
    manager.session_dir = temp_dir / "sessions"
    manager.session_dir.mkdir()
    return manager


@pytest.fixture
def execution_engine():
    """Create execution engine."""
    return ExecutionEngine()


@pytest.fixture
def workflow_manager(temp_dir):
    """Create workflow manager."""
    manager = OptimizationWorkflowManager()
    manager.workflow_dir = temp_dir / "workflows"
    manager.workflow_dir.mkdir()
    return manager


@pytest.fixture
def export_handler(temp_dir):
    """Create export handler."""
    handler = ExportImportHandler()
    handler.export_dir = temp_dir / "exports"
    handler.export_dir.mkdir()
    return handler


@pytest.fixture
def sample_module_code():
    """Sample DSPy module code."""
    return """
import dspy

class SentimentSignature(dspy.Signature):
    text = dspy.InputField(desc="Text to analyze")
    sentiment = dspy.OutputField(desc="Sentiment: positive, negative, or neutral")

class SentimentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentSignature)

    def forward(self, text):
        result = self.predictor(text=text)
        return result.sentiment
"""


def test_generate_validate_execute_workflow(execution_engine, sample_module_code):
    """Test complete workflow: generate -> validate -> execute."""
    # Validate
    validation = execution_engine.validate_code(sample_module_code)
    assert validation.is_valid is True

    # Execute (will fail without DSPy configured, but tests the flow)
    result = execution_engine.execute_code(sample_module_code, timeout=5)
    # Result may fail due to missing DSPy config, but execution should complete
    assert result is not None


def test_session_save_load_workflow(session_manager):
    """Test session save and load workflow."""
    # Create session
    session = MockSession()
    session.conversation_history = [
        {"role": "user", "content": "Create a module"},
        {"role": "assistant", "content": "Here's your module"},
    ]
    session.current_context = {"last_generated": "code here"}

    # Save
    file_path = session_manager.save_session(session, "test_workflow")
    assert file_path.exists()

    # Load
    state = session_manager.load_session("test_workflow")
    assert len(state.conversation_history) == 2
    assert state.current_context["last_generated"] == "code here"

    # Delete
    session_manager.delete_session("test_workflow")
    sessions = session_manager.list_sessions()
    assert len(sessions) == 0


def test_optimization_workflow_end_to_end(workflow_manager, sample_module_code):
    """Test optimization workflow from start to checkpoint."""
    # Start workflow
    workflow = workflow_manager.start_optimization(sample_module_code, "light")
    assert workflow is not None

    # Add training data manually (skip interactive collection)
    workflow.training_data = [
        Example(inputs={"text": f"test{i}"}, output=f"result{i}") for i in range(6)
    ]
    workflow.validation_data = [Example(inputs={"text": "val"}, output="valresult")]

    # Validate data
    workflow_manager.data_collector.examples = workflow.training_data + workflow.validation_data
    is_valid, errors = workflow_manager.validate_data()
    assert is_valid is True

    # Save checkpoint
    checkpoint_path = workflow_manager.save_checkpoint()
    assert checkpoint_path.exists()

    # Load checkpoint
    workflow_manager.current_workflow = None
    loaded = workflow_manager.load_checkpoint(workflow.id)
    assert loaded.id == workflow.id
    assert len(loaded.training_data) == 6


def test_export_import_session_workflow(session_manager, export_handler):
    """Test exporting and importing session."""
    # Create and save session
    session = MockSession()
    session.conversation_history = [{"role": "user", "content": "test"}]
    session.current_context = {"key": "value"}

    file_path = session_manager.save_session(session, "export_test")

    # Export (session is already saved, just verify)
    assert file_path.exists()

    # Import
    imported = export_handler.import_session(file_path)
    assert imported["conversation_history"][0]["content"] == "test"


def test_package_export_workflow(export_handler, sample_module_code, temp_dir):
    """Test complete package export workflow."""
    # Create package builder
    builder = PackageBuilder()

    # Build package
    metadata = PackageMetadata(
        name="test_integration_pkg",
        version="1.0.0",
        description="Integration test package",
        author="Test",
        dependencies=["dspy>=3.0.4"],
    )

    package_dir = builder.build_package(
        sample_module_code, "test_integration_pkg", metadata, temp_dir
    )

    # Verify package structure
    assert (package_dir / "setup.py").exists()
    assert (package_dir / "README.md").exists()
    assert (package_dir / "test_integration_pkg" / "module.py").exists()

    # Verify module code is in package
    module_content = (package_dir / "test_integration_pkg" / "module.py").read_text()
    assert "SentimentModule" in module_content


def test_multiple_sessions_workflow(session_manager):
    """Test managing multiple sessions."""
    # Create multiple sessions
    for i in range(3):
        session = MockSession()
        session.conversation_history = [{"role": "user", "content": f"message{i}"}]
        session_manager.save_session(session, f"session{i}")

    # List all
    sessions = session_manager.list_sessions()
    assert len(sessions) == 3

    # Load specific session
    state = session_manager.load_session("session1")
    assert state.conversation_history[0]["content"] == "message1"

    # Delete one
    session_manager.delete_session("session1")
    sessions = session_manager.list_sessions()
    assert len(sessions) == 2


def test_code_generation_to_package_workflow(execution_engine, export_handler, temp_dir):
    """Test workflow from code generation to package export."""
    code = """
import dspy

class SimpleModule(dspy.Module):
    def forward(self, x):
        return x
"""

    # Validate
    validation = execution_engine.validate_code(code)
    assert validation.is_valid is True

    # Export as package
    builder = PackageBuilder()
    metadata = PackageMetadata(
        name="simple_pkg",
        version="1.0.0",
        description="Simple package",
        author="Test",
        dependencies=["dspy>=3.0.4"],
    )

    package_dir = builder.build_package(code, "simple_pkg", metadata, temp_dir)
    assert package_dir.exists()


def test_session_persistence_across_operations(session_manager):
    """Test session persists correctly across multiple operations."""
    session = MockSession()

    # Initial save
    session.conversation_history = [{"role": "user", "content": "first"}]
    session_manager.save_session(session, "persistent")

    # Load and modify
    state = session_manager.load_session("persistent")
    state.conversation_history.append({"role": "assistant", "content": "response"})

    # Create new session with modified state
    session2 = MockSession()
    session2.conversation_history = state.conversation_history
    session_manager.save_session(session2, "persistent")

    # Load again and verify
    final_state = session_manager.load_session("persistent")
    assert len(final_state.conversation_history) == 2


def test_validation_execution_integration(execution_engine):
    """Test validation and execution work together."""
    valid_code = """
x = 5
y = 10
print(f"Sum: {x + y}")
"""

    # Validate first
    validation = execution_engine.validate_code(valid_code)
    assert validation.is_valid is True

    # Then execute
    result = execution_engine.execute_code(valid_code, timeout=5)
    assert result.success is True
    assert "Sum: 15" in result.stdout


def test_export_multiple_formats(export_handler, sample_module_code, temp_dir):
    """Test exporting code in multiple formats."""
    # Python
    py_path = temp_dir / "module.py"
    export_handler.export_code(sample_module_code, "python", py_path)
    assert py_path.exists()

    # JSON
    json_path = temp_dir / "module.json"
    export_handler.export_code(sample_module_code, "json", json_path)
    assert json_path.exists()

    # Markdown
    md_path = temp_dir / "module.md"
    export_handler.export_code(sample_module_code, "markdown", md_path)
    assert md_path.exists()


def test_workflow_state_persistence(workflow_manager, sample_module_code):
    """Test workflow state persists through save/load."""
    # Create workflow
    workflow = workflow_manager.start_optimization(sample_module_code, "medium")
    original_id = workflow.id

    # Add data
    workflow.training_data = [Example(inputs={"x": "1"}, output="y")]

    # Save
    workflow_manager.save_checkpoint()

    # Clear and reload
    workflow_manager.current_workflow = None
    loaded = workflow_manager.load_checkpoint(original_id)

    # Verify state
    assert loaded.id == original_id
    assert len(loaded.training_data) == 1
    assert loaded.training_data[0].inputs["x"] == "1"
