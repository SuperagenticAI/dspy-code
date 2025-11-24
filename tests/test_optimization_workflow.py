"""
Unit tests for optimization workflow.
"""

import tempfile
from pathlib import Path

import pytest

from dspy_code.core.exceptions import InsufficientDataError
from dspy_code.optimization import (
    DataCollector,
    Example,
    OptimizationWorkflowManager,
    WorkflowState,
)


@pytest.fixture
def temp_workflow_dir():
    """Create temporary workflow directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def workflow_manager(temp_workflow_dir):
    """Create workflow manager with temp directory."""
    manager = OptimizationWorkflowManager()
    manager.workflow_dir = temp_workflow_dir
    return manager


@pytest.fixture
def sample_code():
    """Sample code for testing."""
    return """
import dspy

class SentimentSignature(dspy.Signature):
    text = dspy.InputField()
    sentiment = dspy.OutputField()

class SentimentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(SentimentSignature)

    def forward(self, text):
        return self.predictor(text=text).sentiment
"""


def test_start_optimization(workflow_manager, sample_code):
    """Test starting optimization workflow."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")

    assert workflow is not None
    assert workflow.module_code == sample_code
    assert workflow.budget == "medium"
    assert workflow.state == WorkflowState.INITIALIZED
    assert workflow_manager.current_workflow == workflow


def test_start_optimization_invalid_budget(workflow_manager, sample_code):
    """Test starting optimization with invalid budget."""
    with pytest.raises(ValueError):
        workflow_manager.start_optimization(sample_code, "invalid")


def test_gepa_config_light(workflow_manager, sample_code):
    """Test GEPA config for light budget."""
    workflow = workflow_manager.start_optimization(sample_code, "light")

    assert workflow.gepa_config["max_candidates"] == 6
    assert workflow.gepa_config["max_iterations"] == 2


def test_gepa_config_medium(workflow_manager, sample_code):
    """Test GEPA config for medium budget."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")

    assert workflow.gepa_config["max_candidates"] == 12
    assert workflow.gepa_config["max_iterations"] == 3


def test_gepa_config_heavy(workflow_manager, sample_code):
    """Test GEPA config for heavy budget."""
    workflow = workflow_manager.start_optimization(sample_code, "heavy")

    assert workflow.gepa_config["max_candidates"] == 18
    assert workflow.gepa_config["max_iterations"] == 4


def test_data_collector_example():
    """Test Example dataclass."""
    example = Example(inputs={"text": "I love this!"}, output="positive")

    assert example.inputs["text"] == "I love this!"
    assert example.output == "positive"


def test_data_collector_to_dict():
    """Test Example serialization."""
    example = Example(inputs={"text": "test"}, output="result")

    data = example.to_dict()

    assert data["inputs"]["text"] == "test"
    assert data["output"] == "result"


def test_data_collector_from_dict():
    """Test Example deserialization."""
    data = {"inputs": {"text": "test"}, "output": "result", "metadata": None}

    example = Example.from_dict(data)

    assert example.inputs["text"] == "test"
    assert example.output == "result"


def test_data_collector_validation_empty():
    """Test validation with no examples."""
    collector = DataCollector()

    is_valid, errors = collector.validate_examples()

    assert is_valid is False
    assert len(errors) > 0


def test_data_collector_validation_valid():
    """Test validation with valid examples."""
    collector = DataCollector()
    collector.examples = [
        Example(inputs={"text": "test1"}, output="result1"),
        Example(inputs={"text": "test2"}, output="result2"),
    ]

    is_valid, errors = collector.validate_examples()

    assert is_valid is True
    assert len(errors) == 0


def test_data_collector_validation_inconsistent_fields():
    """Test validation catches inconsistent input fields."""
    collector = DataCollector()
    collector.examples = [
        Example(inputs={"text": "test1"}, output="result1"),
        Example(inputs={"different": "test2"}, output="result2"),
    ]

    is_valid, errors = collector.validate_examples()

    assert is_valid is False
    assert len(errors) > 0


def test_save_checkpoint(workflow_manager, sample_code):
    """Test saving workflow checkpoint."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")

    checkpoint_path = workflow_manager.save_checkpoint()

    assert checkpoint_path.exists()
    assert checkpoint_path.name.startswith("workflow_")


def test_load_checkpoint(workflow_manager, sample_code):
    """Test loading workflow checkpoint."""
    # Create and save workflow
    workflow = workflow_manager.start_optimization(sample_code, "medium")
    workflow_id = workflow.id
    workflow_manager.save_checkpoint()

    # Clear current workflow
    workflow_manager.current_workflow = None

    # Load checkpoint
    loaded_workflow = workflow_manager.load_checkpoint(workflow_id)

    assert loaded_workflow.id == workflow_id
    assert loaded_workflow.budget == "medium"
    assert loaded_workflow.module_code == sample_code


def test_workflow_state_transitions(workflow_manager, sample_code):
    """Test workflow state transitions."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")

    assert workflow.state == WorkflowState.INITIALIZED

    # Simulate state transitions
    workflow.state = WorkflowState.COLLECTING_DATA
    assert workflow.state == WorkflowState.COLLECTING_DATA

    workflow.state = WorkflowState.VALIDATING
    assert workflow.state == WorkflowState.VALIDATING

    workflow.state = WorkflowState.READY
    assert workflow.state == WorkflowState.READY


def test_workflow_to_dict(workflow_manager, sample_code):
    """Test workflow serialization."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")

    data = workflow.to_dict()

    assert data["id"] == workflow.id
    assert data["budget"] == "medium"
    assert data["state"] == WorkflowState.INITIALIZED.value
    assert "created_at" in data


def test_generate_gepa_script(workflow_manager, sample_code):
    """Test GEPA script generation."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")
    workflow.state = WorkflowState.READY

    script = workflow_manager.generate_gepa_script()

    assert script is not None
    assert len(script) > 0
    assert "import dspy" in script or "GEPA" in script


def test_data_collector_save_load(temp_workflow_dir):
    """Test saving and loading training data."""
    collector = DataCollector()
    collector.examples = [
        Example(inputs={"text": "test1"}, output="result1"),
        Example(inputs={"text": "test2"}, output="result2"),
    ]

    file_path = temp_workflow_dir / "test_data.json"
    collector.save_to_file(file_path)

    assert file_path.exists()

    # Load
    new_collector = DataCollector()
    examples = new_collector.load_from_file(file_path)

    assert len(examples) == 2
    assert examples[0].inputs["text"] == "test1"


def test_workflow_with_training_data(workflow_manager, sample_code):
    """Test workflow with training data."""
    workflow = workflow_manager.start_optimization(sample_code, "light")

    # Add training data manually
    workflow.training_data = [
        Example(inputs={"text": f"test{i}"}, output=f"result{i}") for i in range(6)
    ]
    workflow.validation_data = [Example(inputs={"text": "val1"}, output="valresult1")]

    assert len(workflow.training_data) == 6
    assert len(workflow.validation_data) == 1


def test_insufficient_data_error(workflow_manager, sample_code):
    """Test insufficient data raises error."""
    workflow = workflow_manager.start_optimization(sample_code, "medium")

    # Try to validate with insufficient data
    workflow_manager.data_collector.examples = [Example(inputs={"text": "test"}, output="result")]

    with pytest.raises((InsufficientDataError, ValueError)):
        workflow_manager.collect_training_data(interactive=False, file_path=None)
