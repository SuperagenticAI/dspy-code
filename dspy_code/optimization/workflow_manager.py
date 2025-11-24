"""
Optimization workflow manager for DSPy Code.

Orchestrates GEPA optimization from data collection to result analysis.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..core.exceptions import (
    InsufficientDataError,
)
from ..core.logging import get_logger
from .data_collector import DataCollector, Example

logger = get_logger(__name__)


class WorkflowState(Enum):
    """States of optimization workflow."""

    INITIALIZED = "initialized"
    COLLECTING_DATA = "collecting_data"
    VALIDATING = "validating"
    READY = "ready"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class OptimizationResult:
    """Result of optimization."""

    success: bool
    optimized_code: str | None = None
    original_score: float | None = None
    optimized_score: float | None = None
    improvement: float | None = None
    execution_time: float = 0.0
    error: str | None = None


@dataclass
class OptimizationWorkflow:
    """Represents an optimization workflow."""

    id: str
    module_code: str
    budget: str  # "light", "medium", "heavy"
    state: WorkflowState
    training_data: list[Example] = field(default_factory=list)
    validation_data: list[Example] = field(default_factory=list)
    gepa_config: dict[str, Any] = field(default_factory=dict)
    results: OptimizationResult | None = None
    created_at: datetime = field(default_factory=datetime.now)
    checkpoint_path: Path | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "module_code": self.module_code,
            "budget": self.budget,
            "state": self.state.value,
            "training_data": [ex.to_dict() for ex in self.training_data],
            "validation_data": [ex.to_dict() for ex in self.validation_data],
            "gepa_config": self.gepa_config,
            "created_at": self.created_at.isoformat(),
            "checkpoint_path": str(self.checkpoint_path) if self.checkpoint_path else None,
        }


class OptimizationWorkflowManager:
    """Manages optimization workflows."""

    def __init__(self, code_generator=None, config_manager=None):
        """
        Initialize workflow manager.

        Args:
            code_generator: Code generator instance
            config_manager: Configuration manager
        """
        self.code_generator = code_generator
        self.config_manager = config_manager
        self.current_workflow: OptimizationWorkflow | None = None
        self.data_collector = DataCollector()

        # Workflow storage
        self.workflow_dir = Path.home() / ".dspy_cli" / "optimization"
        self.workflow_dir.mkdir(parents=True, exist_ok=True)

    def start_optimization(self, module_code: str, budget: str = "medium") -> OptimizationWorkflow:
        """
        Start a new optimization workflow.

        Args:
            module_code: Code to optimize
            budget: Optimization budget (light/medium/heavy)

        Returns:
            OptimizationWorkflow instance
        """
        # Validate budget
        if budget not in ["light", "medium", "heavy"]:
            raise ValueError(f"Invalid budget: {budget}. Must be light, medium, or heavy")

        # Create workflow
        workflow = OptimizationWorkflow(
            id=str(uuid.uuid4())[:8],
            module_code=module_code,
            budget=budget,
            state=WorkflowState.INITIALIZED,
        )

        # Set GEPA config based on budget
        workflow.gepa_config = self._get_gepa_config(budget)

        self.current_workflow = workflow
        logger.info(f"Started optimization workflow {workflow.id} with {budget} budget")

        return workflow

    def collect_training_data(
        self, interactive: bool = True, file_path: Path | None = None
    ) -> list[Example]:
        """
        Collect training examples.

        Args:
            interactive: Whether to collect interactively
            file_path: Optional file to load examples from

        Returns:
            List of training examples
        """
        if not self.current_workflow:
            raise ValueError("No active workflow. Call start_optimization() first")

        self.current_workflow.state = WorkflowState.COLLECTING_DATA

        # Determine minimum examples based on budget
        min_examples = {"light": 6, "medium": 12, "heavy": 18}[self.current_workflow.budget]

        if file_path:
            # Load from file
            examples = self.data_collector.load_from_file(file_path)
        elif interactive:
            # Collect interactively
            examples = self.data_collector.collect_interactive(
                min_examples=min_examples, max_examples=min_examples * 3
            )
        else:
            raise ValueError("Must specify either interactive=True or file_path")

        if len(examples) < min_examples:
            raise InsufficientDataError(min_examples, len(examples))

        # Split into training and validation (80/20)
        split_idx = int(len(examples) * 0.8)
        self.current_workflow.training_data = examples[:split_idx]
        self.current_workflow.validation_data = examples[split_idx:]

        logger.info(
            f"Collected {len(examples)} examples "
            f"({len(self.current_workflow.training_data)} train, "
            f"{len(self.current_workflow.validation_data)} val)"
        )

        return examples

    def validate_data(self) -> tuple[bool, list[str]]:
        """
        Validate collected training data.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        if not self.current_workflow:
            return False, ["No active workflow"]

        self.current_workflow.state = WorkflowState.VALIDATING

        # Validate training data
        is_valid, errors = self.data_collector.validate_examples()

        if is_valid:
            self.current_workflow.state = WorkflowState.READY
            logger.info("Data validation passed")
        else:
            self.current_workflow.state = WorkflowState.FAILED
            logger.error(f"Data validation failed: {errors}")

        return is_valid, errors

    def generate_gepa_script(self) -> str:
        """
        Generate GEPA optimization script.

        Returns:
            Python code for GEPA optimization
        """
        if not self.current_workflow:
            raise ValueError("No active workflow")

        if self.current_workflow.state != WorkflowState.READY:
            raise ValueError(f"Workflow not ready (state: {self.current_workflow.state})")

        # Generate GEPA script using existing generator
        from ..generators.gepa_generator import generate_gepa_for_program

        gepa_code = generate_gepa_for_program(
            self.current_workflow.module_code, self.current_workflow.budget
        )

        logger.info("Generated GEPA optimization script")
        return gepa_code

    def save_checkpoint(self) -> Path:
        """
        Save workflow checkpoint.

        Returns:
            Path to checkpoint file
        """
        if not self.current_workflow:
            raise ValueError("No active workflow")

        checkpoint_file = self.workflow_dir / f"workflow_{self.current_workflow.id}.json"

        import json

        with open(checkpoint_file, "w") as f:
            json.dump(self.current_workflow.to_dict(), f, indent=2)

        self.current_workflow.checkpoint_path = checkpoint_file
        logger.info(f"Saved checkpoint to {checkpoint_file}")

        return checkpoint_file

    def load_checkpoint(self, workflow_id: str) -> OptimizationWorkflow:
        """
        Load workflow from checkpoint.

        Args:
            workflow_id: Workflow ID to load

        Returns:
            OptimizationWorkflow instance
        """
        checkpoint_file = self.workflow_dir / f"workflow_{workflow_id}.json"

        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_file}")

        import json

        with open(checkpoint_file) as f:
            data = json.load(f)

        # Reconstruct workflow
        workflow = OptimizationWorkflow(
            id=data["id"],
            module_code=data["module_code"],
            budget=data["budget"],
            state=WorkflowState(data["state"]),
            training_data=[Example.from_dict(ex) for ex in data["training_data"]],
            validation_data=[Example.from_dict(ex) for ex in data["validation_data"]],
            gepa_config=data["gepa_config"],
            created_at=datetime.fromisoformat(data["created_at"]),
            checkpoint_path=Path(data["checkpoint_path"]) if data["checkpoint_path"] else None,
        )

        self.current_workflow = workflow
        logger.info(f"Loaded checkpoint for workflow {workflow_id}")

        return workflow

    def _get_gepa_config(self, budget: str) -> dict[str, Any]:
        """
        Get GEPA configuration for budget.

        Args:
            budget: Budget level

        Returns:
            GEPA configuration dictionary
        """
        configs = {
            "light": {
                "max_candidates": 6,
                "max_iterations": 2,
                "description": "Quick experimentation (~6 candidates, 5-10 minutes)",
            },
            "medium": {
                "max_candidates": 12,
                "max_iterations": 3,
                "description": "Balanced optimization (~12 candidates, 20-30 minutes)",
            },
            "heavy": {
                "max_candidates": 18,
                "max_iterations": 4,
                "description": "Thorough optimization (~18 candidates, 1-2 hours)",
            },
        }

        return configs[budget]

    def execute_optimization(self, timeout: int | None = None) -> OptimizationResult:
        """
        Execute the optimization workflow.

        Args:
            timeout: Optional timeout in seconds

        Returns:
            OptimizationResult
        """
        if not self.current_workflow:
            raise ValueError("No active workflow")

        if self.current_workflow.state != WorkflowState.READY:
            raise ValueError(f"Workflow not ready (state: {self.current_workflow.state})")

        # Generate GEPA script
        gepa_code = self.generate_gepa_script()

        # Save script to file
        script_path = self.workflow_dir / f"optimize_{self.current_workflow.id}.py"
        script_path.write_text(gepa_code)

        # Save training data
        data_path = self.workflow_dir / f"data_{self.current_workflow.id}.json"
        self.data_collector.save_to_file(data_path)

        # Execute optimization
        from .executor import OptimizationExecutor

        executor = OptimizationExecutor()
        result = executor.execute_optimization(self.current_workflow, script_path, timeout=timeout)

        # Save checkpoint
        self.save_checkpoint()

        return result

    def compare_results(self, original_code: str, optimized_code: str) -> dict:
        """
        Compare original and optimized code.

        Args:
            original_code: Original code
            optimized_code: Optimized code

        Returns:
            Comparison dictionary
        """
        if not self.current_workflow or not self.current_workflow.results:
            raise ValueError("No optimization results available")

        from .executor import ResultComparator

        return ResultComparator.compare_results(
            original_code,
            optimized_code,
            self.current_workflow.results.original_score,
            self.current_workflow.results.optimized_score,
        )
