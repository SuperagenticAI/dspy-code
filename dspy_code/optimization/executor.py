"""
Optimization execution engine.

Handles GEPA optimization execution with progress tracking and cancellation.
"""

import subprocess
import sys
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from ..core.exceptions import OptimizationTimeoutError
from ..core.logging import get_logger
from .workflow_manager import OptimizationResult, OptimizationWorkflow, WorkflowState

console = Console()
logger = get_logger(__name__)


@dataclass
class OptimizationProgress:
    """Progress information for optimization."""

    current_iteration: int = 0
    total_iterations: int = 0
    current_candidate: int = 0
    total_candidates: int = 0
    best_score: float = 0.0
    elapsed_time: float = 0.0
    status_message: str = ""


class OptimizationExecutor:
    """Executes GEPA optimization with monitoring."""

    def __init__(self):
        self.process: subprocess.Popen | None = None
        self.cancelled = False
        self.progress = OptimizationProgress()
        self.output_lines = []

    def execute_optimization(
        self,
        workflow: OptimizationWorkflow,
        gepa_script_path: Path,
        progress_callback: Callable[[OptimizationProgress], None] | None = None,
        timeout: int | None = None,
    ) -> OptimizationResult:
        """
        Execute GEPA optimization.

        Args:
            workflow: Optimization workflow
            gepa_script_path: Path to GEPA script
            progress_callback: Optional callback for progress updates
            timeout: Optional timeout in seconds

        Returns:
            OptimizationResult
        """
        workflow.state = WorkflowState.OPTIMIZING
        start_time = time.time()

        try:
            # Start subprocess
            self.process = subprocess.Popen(
                [sys.executable, str(gepa_script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Monitor progress in separate thread
            monitor_thread = threading.Thread(
                target=self._monitor_progress, args=(progress_callback,)
            )
            monitor_thread.daemon = True
            monitor_thread.start()

            # Wait for completion or timeout
            try:
                stdout, stderr = self.process.communicate(timeout=timeout)
                return_code = self.process.returncode
            except subprocess.TimeoutExpired:
                self.cancel()
                raise OptimizationTimeoutError(timeout)

            execution_time = time.time() - start_time

            # Check if cancelled
            if self.cancelled:
                workflow.state = WorkflowState.CANCELLED
                return OptimizationResult(
                    success=False, execution_time=execution_time, error="Optimization was cancelled"
                )

            # Check return code
            if return_code != 0:
                workflow.state = WorkflowState.FAILED
                return OptimizationResult(
                    success=False,
                    execution_time=execution_time,
                    error=stderr or "Optimization failed",
                )

            # Parse results
            result = self._parse_results(stdout, stderr, execution_time)

            if result.success:
                workflow.state = WorkflowState.COMPLETED
                workflow.results = result
            else:
                workflow.state = WorkflowState.FAILED

            return result

        except Exception as e:
            workflow.state = WorkflowState.FAILED
            logger.error(f"Optimization execution failed: {e}")

            return OptimizationResult(
                success=False, execution_time=time.time() - start_time, error=str(e)
            )

    def cancel(self) -> None:
        """Cancel running optimization."""
        self.cancelled = True

        if self.process and self.process.poll() is None:
            logger.info("Cancelling optimization...")
            self.process.terminate()

            # Wait a bit for graceful termination
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if needed
                self.process.kill()
                self.process.wait()

            logger.info("Optimization cancelled")

    def _monitor_progress(self, callback: Callable[[OptimizationProgress], None] | None) -> None:
        """
        Monitor optimization progress from stdout.

        Args:
            callback: Optional callback for progress updates
        """
        if not self.process:
            return

        while self.process.poll() is None and not self.cancelled:
            try:
                line = self.process.stdout.readline()
                if line:
                    self.output_lines.append(line.strip())
                    self._parse_progress_line(line)

                    if callback:
                        callback(self.progress)

                time.sleep(0.1)
            except Exception as e:
                logger.debug(f"Progress monitoring error: {e}")
                break

    def _parse_progress_line(self, line: str) -> None:
        """
        Parse progress information from output line.

        Args:
            line: Output line from GEPA
        """
        line = line.strip().lower()

        # Look for iteration info
        if "iteration" in line:
            try:
                # Extract iteration number
                parts = line.split()
                for i, part in enumerate(parts):
                    if "iteration" in part and i + 1 < len(parts):
                        self.progress.current_iteration = int(parts[i + 1].strip(":/"))
            except (ValueError, IndexError):
                pass

        # Look for candidate info
        if "candidate" in line:
            try:
                parts = line.split()
                for i, part in enumerate(parts):
                    if "candidate" in part and i + 1 < len(parts):
                        self.progress.current_candidate = int(parts[i + 1].strip(":/"))
            except (ValueError, IndexError):
                pass

        # Look for score info
        if "score" in line or "accuracy" in line:
            try:
                # Extract score value
                parts = line.split()
                for part in parts:
                    try:
                        score = float(part.strip("%:,"))
                        if 0 <= score <= 100:
                            self.progress.best_score = score
                            break
                    except ValueError:
                        continue
            except Exception:
                pass

        # Update status message
        self.progress.status_message = line[:100]

    def _parse_results(self, stdout: str, stderr: str, execution_time: float) -> OptimizationResult:
        """
        Parse optimization results from output.

        Args:
            stdout: Standard output
            stderr: Standard error
            execution_time: Execution time in seconds

        Returns:
            OptimizationResult
        """
        # Try to extract scores from output
        original_score = None
        optimized_score = None

        lines = stdout.split("\n")
        for line in lines:
            line_lower = line.lower()

            if "original" in line_lower and ("score" in line_lower or "accuracy" in line_lower):
                try:
                    # Extract number
                    parts = line.split()
                    for part in parts:
                        try:
                            score = float(part.strip("%:,"))
                            if 0 <= score <= 100:
                                original_score = score
                                break
                        except ValueError:
                            continue
                except Exception:
                    pass

            if "optimized" in line_lower and ("score" in line_lower or "accuracy" in line_lower):
                try:
                    parts = line.split()
                    for part in parts:
                        try:
                            score = float(part.strip("%:,"))
                            if 0 <= score <= 100:
                                optimized_score = score
                                break
                        except ValueError:
                            continue
                except Exception:
                    pass

        # Calculate improvement
        improvement = None
        if original_score is not None and optimized_score is not None:
            improvement = optimized_score - original_score

        # Extract optimized code (would be saved to file by GEPA script)
        optimized_code = None

        return OptimizationResult(
            success=True,
            optimized_code=optimized_code,
            original_score=original_score,
            optimized_score=optimized_score,
            improvement=improvement,
            execution_time=execution_time,
        )

    def get_status(self) -> dict:
        """
        Get current optimization status.

        Returns:
            Status dictionary
        """
        is_running = self.process is not None and self.process.poll() is None

        return {
            "running": is_running,
            "cancelled": self.cancelled,
            "progress": {
                "iteration": self.progress.current_iteration,
                "candidate": self.progress.current_candidate,
                "best_score": self.progress.best_score,
                "status": self.progress.status_message,
            },
        }


class ResultComparator:
    """Compares original and optimized results."""

    @staticmethod
    def compare_results(
        original_code: str,
        optimized_code: str,
        original_score: float | None,
        optimized_score: float | None,
    ) -> dict:
        """
        Compare original and optimized results.

        Args:
            original_code: Original code
            optimized_code: Optimized code
            original_score: Original performance score
            optimized_score: Optimized performance score

        Returns:
            Comparison dictionary
        """
        comparison = {
            "code_length": {
                "original": len(original_code),
                "optimized": len(optimized_code) if optimized_code else 0,
                "change": len(optimized_code) - len(original_code) if optimized_code else 0,
            }
        }

        if original_score is not None and optimized_score is not None:
            improvement = optimized_score - original_score
            improvement_pct = (improvement / original_score * 100) if original_score > 0 else 0

            comparison["performance"] = {
                "original_score": original_score,
                "optimized_score": optimized_score,
                "improvement": improvement,
                "improvement_pct": improvement_pct,
                "better": optimized_score > original_score,
            }

        return comparison

    @staticmethod
    def format_comparison(comparison: dict) -> str:
        """
        Format comparison for display.

        Args:
            comparison: Comparison dictionary

        Returns:
            Formatted string
        """
        lines = []
        lines.append("Optimization Comparison")
        lines.append("=" * 50)

        # Code length
        code_len = comparison["code_length"]
        lines.append("\nCode Length:")
        lines.append(f"  Original:  {code_len['original']} chars")
        lines.append(f"  Optimized: {code_len['optimized']} chars")
        lines.append(f"  Change:    {code_len['change']:+d} chars")

        # Performance
        if "performance" in comparison:
            perf = comparison["performance"]
            lines.append("\nPerformance:")
            lines.append(f"  Original:  {perf['original_score']:.1f}%")
            lines.append(f"  Optimized: {perf['optimized_score']:.1f}%")
            lines.append(
                f"  Improvement: {perf['improvement']:+.1f}% ({perf['improvement_pct']:+.1f}%)"
            )

            if perf["better"]:
                lines.append("\n✓ Optimization improved performance!")
            else:
                lines.append("\n✗ Optimization did not improve performance")

        return "\n".join(lines)
