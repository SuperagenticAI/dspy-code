"""
DSPy Optimizer Templates

This module provides templates for all major DSPy optimizers including:
- GEPA (Genetic Prompt Evolution Algorithm)
- MIPROv2 (Multi-prompt Instruction Proposal Optimizer)
- BootstrapFewShot (Bootstrap few-shot examples)
- BootstrapFewShotWithRandomSearch
- COPRO (Coordinate Prompt Optimization)

Each template includes complete working code with training data examples,
metric functions, and optimization configuration.
"""

from dataclasses import dataclass


@dataclass
class OptimizerInfo:
    """Information about an optimizer."""

    name: str
    display_name: str
    description: str
    best_for: str
    requires: list[str]
    difficulty: str
    keywords: list[str]


class OptimizerTemplates:
    """Registry of DSPy optimizer templates."""

    def __init__(self):
        self.optimizers = {
            "gepa": self._gepa_info(),
            "mipro": self._mipro_info(),
            "bootstrap": self._bootstrap_info(),
            "bootstrap_rs": self._bootstrap_rs_info(),
            "copro": self._copro_info(),
            "knn_fewshot": self._knn_fewshot_info(),
            "labeled_fewshot": self._labeled_fewshot_info(),
            "bootstrap_finetune": self._bootstrap_finetune_info(),
            "avatar": self._avatar_info(),
            "simba": self._simba_info(),
            "ensemble": self._ensemble_optimizer_info(),
        }

    def list_all(self) -> list[OptimizerInfo]:
        """List all available optimizers."""
        return list(self.optimizers.values())

    def get_optimizer_code(self, name: str, task_type: str = "classification") -> str | None:
        """Get complete code for an optimizer."""
        generators = {
            "gepa": self._generate_gepa,
            "mipro": self._generate_mipro,
            "bootstrap": self._generate_bootstrap,
            "bootstrap_rs": self._generate_bootstrap_rs,
            "copro": self._generate_copro,
            "knn_fewshot": self._generate_knn_fewshot,
            "labeled_fewshot": self._generate_labeled_fewshot,
            "bootstrap_finetune": self._generate_bootstrap_finetune,
            "avatar": self._generate_avatar,
            "simba": self._generate_simba,
            "ensemble": self._generate_ensemble_optimizer,
        }

        generator = generators.get(name)
        return generator(task_type) if generator else None

    def search(self, query: str) -> list[OptimizerInfo]:
        """Search optimizers by keywords."""
        query_lower = query.lower()
        matches = []

        for optimizer in self.optimizers.values():
            if (
                any(kw in query_lower for kw in optimizer.keywords)
                or query_lower in optimizer.best_for.lower()
            ):
                matches.append(optimizer)

        return matches

    # Optimizer Info Methods

    def _gepa_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="gepa",
            display_name="GEPA (Genetic Prompt Evolution)",
            description="Uses reflection and genetic algorithms to evolve prompts automatically",
            best_for="General purpose, automatic prompt improvement, complex tasks",
            requires=["training_data", "validation_data", "metric_with_feedback"],
            difficulty="intermediate",
            keywords=["gepa", "genetic", "evolution", "reflection", "automatic"],
        )

    def _mipro_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="mipro",
            display_name="MIPROv2 (Multi-prompt Instruction Proposal)",
            description="Optimizes instructions and few-shot examples simultaneously",
            best_for="Complex tasks requiring instruction optimization, high accuracy needs",
            requires=["training_data", "validation_data", "metric"],
            difficulty="advanced",
            keywords=["mipro", "instruction", "multi-prompt", "advanced"],
        )

    def _bootstrap_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="bootstrap",
            display_name="BootstrapFewShot",
            description="Bootstrap few-shot examples from training data",
            best_for="Most common optimizer, good starting point, quick results",
            requires=["training_data", "metric"],
            difficulty="beginner",
            keywords=["bootstrap", "few-shot", "examples", "simple", "quick"],
        )

    def _bootstrap_rs_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="bootstrap_rs",
            display_name="BootstrapFewShotWithRandomSearch",
            description="Bootstrap with random search over hyperparameters",
            best_for="When you want to tune hyperparameters automatically",
            requires=["training_data", "validation_data", "metric"],
            difficulty="intermediate",
            keywords=["bootstrap", "random search", "hyperparameter", "tuning"],
        )

    def _copro_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="copro",
            display_name="COPRO (Coordinate Prompt Optimization)",
            description="Coordinate optimization of multiple prompts in a pipeline",
            best_for="Multi-stage pipelines, coordinated optimization",
            requires=["training_data", "metric"],
            difficulty="advanced",
            keywords=["copro", "coordinate", "pipeline", "multi-stage"],
        )

    def _knn_fewshot_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="knn_fewshot",
            display_name="KNNFewShot",
            description="Uses K-nearest neighbors to select few-shot examples dynamically",
            best_for="When you have large example datasets and want dynamic example selection",
            requires=["training_data", "metric", "knn_retriever"],
            difficulty="intermediate",
            keywords=["knn", "few-shot", "nearest neighbor", "dynamic", "retrieval"],
        )

    def _labeled_fewshot_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="labeled_fewshot",
            display_name="LabeledFewShot",
            description="Uses labeled examples for few-shot learning with quality filtering",
            best_for="When you have high-quality labeled examples and want to filter by quality",
            requires=["labeled_training_data", "metric", "quality_threshold"],
            difficulty="beginner",
            keywords=["labeled", "few-shot", "quality", "filtering", "examples"],
        )

    def _bootstrap_finetune_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="bootstrap_finetune",
            display_name="BootstrapFinetune",
            description="Bootstrap examples and fine-tune the language model",
            best_for="When you want to fine-tune the underlying LLM with bootstrapped examples",
            requires=["training_data", "metric", "model_finetuning_capability"],
            difficulty="advanced",
            keywords=["bootstrap", "finetune", "fine-tune", "model", "training"],
        )

    def _avatar_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="avatar",
            display_name="AvatarOptimizer",
            description="Multi-agent optimization using avatar models for reflection and improvement",
            best_for="Complex tasks requiring multi-agent collaboration and reflection",
            requires=["training_data", "validation_data", "metric", "reflection_model"],
            difficulty="advanced",
            keywords=["avatar", "multi-agent", "reflection", "collaboration", "advanced"],
        )

    def _simba_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="simba",
            display_name="SIMBA",
            description="Simple but effective optimization using iterative refinement",
            best_for="Quick optimization with minimal configuration, good for prototyping",
            requires=["training_data", "metric"],
            difficulty="beginner",
            keywords=["simba", "simple", "iterative", "refinement", "quick"],
        )

    def _ensemble_optimizer_info(self) -> OptimizerInfo:
        return OptimizerInfo(
            name="ensemble",
            display_name="Ensemble Optimizer",
            description="Optimizes multiple models/predictors and combines their outputs",
            best_for="When you want to combine multiple optimized models for better performance",
            requires=["training_data", "validation_data", "metric", "multiple_models"],
            difficulty="advanced",
            keywords=["ensemble", "multiple", "combine", "aggregate", "voting"],
        )

    # Template Generation Methods

    def _generate_gepa(self, task_type: str = "classification") -> str:
        """Generate GEPA optimization template."""
        return '''"""
GEPA Optimization Script

GEPA (Genetic Prompt Evolution Algorithm) uses reflection to automatically
evolve and improve prompts through genetic algorithms.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import GEPA
import json
from pathlib import Path

# ============================================================================
# 1. YOUR MODULE (Replace with your actual module)
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC WITH FEEDBACK (Required for GEPA)
# ============================================================================

def metric_with_feedback(example, pred, trace=None):
    """
    Metric that returns (score, feedback) for GEPA.

    GEPA uses the feedback to guide prompt evolution.
    """
    # Get predicted and expected outputs
    predicted = pred.output.strip().lower()
    expected = example.output.strip().lower()

    # Calculate score
    correct = predicted == expected
    score = 1.0 if correct else 0.0

    # Generate feedback for GEPA
    if correct:
        feedback = "Correct! The prediction matches the expected output."
    else:
        feedback = f"Incorrect. Expected '{expected}' but got '{predicted}'. "
        feedback += "Consider being more specific in the reasoning."

    return score, feedback


# ============================================================================
# 3. DATA LOADING
# ============================================================================

def load_data():
    """Load training and validation data."""

    # Example data format - replace with your actual data
    train_examples = [
        dspy.Example(input_text="example 1", output="label 1").with_inputs("input_text"),
        dspy.Example(input_text="example 2", output="label 2").with_inputs("input_text"),
        # Add 20-50 training examples
    ]

    val_examples = [
        dspy.Example(input_text="val example 1", output="label 1").with_inputs("input_text"),
        dspy.Example(input_text="val example 2", output="label 2").with_inputs("input_text"),
        # Add 10-20 validation examples
    ]

    return train_examples, val_examples


# ============================================================================
# 4. CONFIGURATION
# ============================================================================

def configure_dspy():
    """Configure DSPy with language models."""

    # Main LM for task
    lm = dspy.LM(model='ollama/gpt-oss:20b')

    # Reflection LM for GEPA (can be same or different)
    reflection_lm = dspy.LM(model='ollama/gpt-oss:20b')

    dspy.configure(lm=lm)

    return lm, reflection_lm


# ============================================================================
# 5. GEPA OPTIMIZATION
# ============================================================================

def run_gepa_optimization():
    """Run GEPA optimization."""

    print("\\n" + "="*70)
    print("GEPA Optimization")
    print("="*70 + "\\n")

    # Configure
    lm, reflection_lm = configure_dspy()
    print("✓ Configured language models\\n")

    # Load data
    trainset, valset = load_data()
    print(f"✓ Loaded {len(trainset)} training examples")
    print(f"✓ Loaded {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()
    print("✓ Created module\\n")

    # Configure GEPA
    gepa = GEPA(
        metric=metric_with_feedback,
        breadth=2,              # Number of candidates per generation
        depth=3,                # Number of generations
        init_temperature=1.4,   # Initial exploration temperature
        reflection_lm=reflection_lm,
        verbose=True
    )

    print("GEPA Configuration:")
    print(f"  • Breadth: 2 candidates per generation")
    print(f"  • Depth: 3 generations")
    print(f"  • Total candidates: ~6")
    print(f"  • Estimated time: 5-10 minutes\\n")

    # Run optimization
    print("Starting GEPA optimization...\\n")

    optimized_module = gepa.compile(
        module,
        trainset=trainset,
        valset=valset
    )

    print("\\n✓ Optimization complete!\\n")

    # Evaluate
    print("Evaluating optimized module...\\n")

    from dspy.evaluate import Evaluate
    evaluator = Evaluate(
        devset=valset,
        metric=lambda ex, pred, trace=None: metric_with_feedback(ex, pred, trace)[0],
        num_threads=1,
        display_progress=True
    )

    score = evaluator(optimized_module)

    print(f"\\nValidation Score: {score:.2%}\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)

    optimized_module.save(output_dir / "optimized_module.json")
    print(f"✓ Saved optimized module to {output_dir}/optimized_module.json\\n")

    return optimized_module


# ============================================================================
# 6. MAIN
# ============================================================================

if __name__ == "__main__":
    optimized_module = run_gepa_optimization()

    print("="*70)
    print("Next Steps:")
    print("="*70)
    print("1. Test the optimized module on new examples")
    print("2. Deploy to production")
    print("3. Monitor performance")
    print()
'''

    def _generate_bootstrap(self, task_type: str = "classification") -> str:
        """Generate BootstrapFewShot optimization template."""
        return '''"""
BootstrapFewShot Optimization Script

BootstrapFewShot is the most commonly used DSPy optimizer. It bootstraps
few-shot examples from your training data to improve performance.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import BootstrapFewShot
import json
from pathlib import Path

# ============================================================================
# 1. YOUR MODULE (Replace with your actual module)
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION
# ============================================================================

def accuracy_metric(example, pred, trace=None):
    """
    Simple accuracy metric.

    Returns 1.0 if prediction matches expected output, 0.0 otherwise.
    """
    predicted = pred.output.strip().lower()
    expected = example.output.strip().lower()
    return 1.0 if predicted == expected else 0.0


# ============================================================================
# 3. DATA LOADING
# ============================================================================

def load_data():
    """Load training data."""

    # Example data format - replace with your actual data
    train_examples = [
        dspy.Example(input_text="example 1", output="label 1").with_inputs("input_text"),
        dspy.Example(input_text="example 2", output="label 2").with_inputs("input_text"),
        # Add 20-50 training examples
    ]

    return train_examples


# ============================================================================
# 4. CONFIGURATION
# ============================================================================

def configure_dspy():
    """Configure DSPy with language model."""
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    return lm


# ============================================================================
# 5. BOOTSTRAP OPTIMIZATION
# ============================================================================

def run_bootstrap_optimization():
    """Run BootstrapFewShot optimization."""

    print("\\n" + "="*70)
    print("BootstrapFewShot Optimization")
    print("="*70 + "\\n")

    # Configure
    lm = configure_dspy()
    print("✓ Configured language model\\n")

    # Load data
    trainset = load_data()
    print(f"✓ Loaded {len(trainset)} training examples\\n")

    # Create module
    module = YourModule()
    print("✓ Created module\\n")

    # Configure BootstrapFewShot
    optimizer = BootstrapFewShot(
        metric=accuracy_metric,
        max_bootstrapped_demos=4,  # Number of examples to bootstrap
        max_labeled_demos=4,        # Max examples to use
        max_rounds=1,               # Number of bootstrap rounds
        max_errors=5                # Max errors before stopping
    )

    print("BootstrapFewShot Configuration:")
    print(f"  • Max demos: 4")
    print(f"  • Max rounds: 1")
    print(f"  • Estimated time: 2-5 minutes\\n")

    # Run optimization
    print("Starting BootstrapFewShot optimization...\\n")

    optimized_module = optimizer.compile(
        module,
        trainset=trainset
    )

    print("\\n✓ Optimization complete!\\n")

    # Evaluate
    print("Evaluating optimized module...\\n")

    from dspy.evaluate import Evaluate
    evaluator = Evaluate(
        devset=trainset[:10],  # Use subset for quick eval
        metric=accuracy_metric,
        num_threads=1,
        display_progress=True
    )

    score = evaluator(optimized_module)

    print(f"\\nTraining Score: {score:.2%}\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)

    optimized_module.save(output_dir / "optimized_module.json")
    print(f"✓ Saved optimized module to {output_dir}/optimized_module.json\\n")

    return optimized_module


# ============================================================================
# 6. MAIN
# ============================================================================

if __name__ == "__main__":
    optimized_module = run_bootstrap_optimization()

    print("="*70)
    print("Next Steps:")
    print("="*70)
    print("1. Test on validation set")
    print("2. Increase max_bootstrapped_demos for better results")
    print("3. Try BootstrapFewShotWithRandomSearch for hyperparameter tuning")
    print()
'''

    def _generate_mipro(self, task_type: str = "classification") -> str:
        """Generate MIPROv2 optimization template."""
        return '''"""
MIPROv2 Optimization Script

MIPROv2 optimizes both instructions and few-shot examples simultaneously
for maximum performance on complex tasks.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import MIPROv2
from pathlib import Path

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC
# ============================================================================

def accuracy_metric(example, pred, trace=None):
    predicted = pred.output.strip().lower()
    expected = example.output.strip().lower()
    return 1.0 if predicted == expected else 0.0


# ============================================================================
# 3. DATA
# ============================================================================

def load_data():
    train_examples = [
        dspy.Example(input_text="example 1", output="label 1").with_inputs("input_text"),
        # Add 50-100 training examples for best results
    ]

    val_examples = [
        dspy.Example(input_text="val 1", output="label 1").with_inputs("input_text"),
        # Add 20-30 validation examples
    ]

    return train_examples, val_examples


# ============================================================================
# 4. MIPRO OPTIMIZATION
# ============================================================================

def run_mipro_optimization():
    print("\\n" + "="*70)
    print("MIPROv2 Optimization")
    print("="*70 + "\\n")

    # Configure
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Load data
    trainset, valset = load_data()
    print(f"✓ Loaded {len(trainset)} training, {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()

    # Configure MIPRO
    optimizer = MIPROv2(
        metric=accuracy_metric,
        num_candidates=10,      # Number of instruction candidates
        init_temperature=1.0,
        verbose=True
    )

    print("MIPROv2 Configuration:")
    print(f"  • Instruction candidates: 10")
    print(f"  • Optimizes both instructions and examples")
    print(f"  • Estimated time: 10-20 minutes\\n")

    # Run optimization
    print("Starting MIPROv2 optimization...\\n")

    optimized_module = optimizer.compile(
        module,
        trainset=trainset,
        valset=valset,
        requires_permission_to_run=False
    )

    print("\\n✓ Optimization complete!\\n")

    # Evaluate
    from dspy.evaluate import Evaluate
    evaluator = Evaluate(devset=valset, metric=accuracy_metric, num_threads=1)
    score = evaluator(optimized_module)

    print(f"\\nValidation Score: {score:.2%}\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")
    print(f"✓ Saved to {output_dir}/optimized_module.json\\n")

    return optimized_module


if __name__ == "__main__":
    run_mipro_optimization()
'''

    def _generate_bootstrap_rs(self, task_type: str = "classification") -> str:
        """Generate BootstrapFewShotWithRandomSearch template."""
        return '''"""
BootstrapFewShotWithRandomSearch Optimization Script

Combines BootstrapFewShot with random search over hyperparameters
for automatic hyperparameter tuning.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import BootstrapFewShotWithRandomSearch
from pathlib import Path

# Module, metric, and data loading same as BootstrapFewShot...
# (Copy from BootstrapFewShot template)

def run_optimization():
    print("\\n" + "="*70)
    print("BootstrapFewShot with Random Search")
    print("="*70 + "\\n")

    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)

    # Load data
    trainset = []  # Your training data
    valset = []    # Your validation data

    module = YourModule()

    # Configure with random search
    optimizer = BootstrapFewShotWithRandomSearch(
        metric=accuracy_metric,
        max_bootstrapped_demos=4,
        num_candidate_programs=8,  # Number of hyperparameter combinations to try
        num_threads=4
    )

    print("Configuration:")
    print(f"  • Trying 8 different hyperparameter combinations")
    print(f"  • Using random search for optimization\\n")

    optimized_module = optimizer.compile(module, trainset=trainset, valset=valset)

    print("\\n✓ Optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_optimization()
'''

    def _generate_copro(self, task_type: str = "classification") -> str:
        """Generate COPRO optimization template."""
        return '''"""
COPRO Optimization Script

COPRO (Coordinate Prompt Optimization) coordinates optimization
of multiple prompts in a pipeline for end-to-end improvement.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import COPRO
from pathlib import Path

# ============================================================================
# 1. MULTI-STAGE MODULE
# ============================================================================

class Stage1Signature(dspy.Signature):
    input_text = dspy.InputField()
    intermediate = dspy.OutputField()


class Stage2Signature(dspy.Signature):
    intermediate = dspy.InputField()
    output = dspy.OutputField()


class MultiStageModule(dspy.Module):
    """Module with multiple stages to coordinate."""

    def __init__(self):
        super().__init__()
        self.stage1 = dspy.ChainOfThought(Stage1Signature)
        self.stage2 = dspy.ChainOfThought(Stage2Signature)

    def forward(self, input_text):
        stage1_result = self.stage1(input_text=input_text)
        stage2_result = self.stage2(intermediate=stage1_result.intermediate)
        return stage2_result


# ============================================================================
# 2. METRIC
# ============================================================================

def accuracy_metric(example, pred, trace=None):
    predicted = pred.output.strip().lower()
    expected = example.output.strip().lower()
    return 1.0 if predicted == expected else 0.0


# ============================================================================
# 3. COPRO OPTIMIZATION
# ============================================================================

def run_copro_optimization():
    print("\\n" + "="*70)
    print("COPRO Optimization")
    print("="*70 + "\\n")

    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)

    # Load data
    trainset = []  # Your training data

    module = MultiStageModule()

    # Configure COPRO
    optimizer = COPRO(
        metric=accuracy_metric,
        breadth=10,  # Number of prompt candidates per stage
        depth=3,     # Optimization rounds
        init_temperature=1.4
    )

    print("COPRO Configuration:")
    print(f"  • Coordinates optimization across all stages")
    print(f"  • Breadth: 10 candidates per stage")
    print(f"  • Depth: 3 rounds\\n")

    optimized_module = optimizer.compile(module, trainset=trainset)

    print("\\n✓ Optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_copro_optimization()
'''

    def _generate_knn_fewshot(self, task_type: str = "classification") -> str:
        """Generate KNNFewShot optimization template."""
        return '''"""
KNNFewShot Optimization Script

KNNFewShot uses K-nearest neighbors to dynamically select few-shot examples
based on similarity to the current input.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import KNNFewShot
from pathlib import Path
import json

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION
# ============================================================================

def accuracy_metric(example, prediction, trace=None):
    """Calculate accuracy metric."""
    return float(prediction.output.lower() == example.output.lower())


# ============================================================================
# 3. LOAD TRAINING DATA
# ============================================================================

def load_training_data(file_path: str):
    """Load training examples from JSONL file."""
    examples = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(
                input_text=data['input'],
                output=data['output']
            ).with_inputs('input_text'))
    return examples


# ============================================================================
# 4. KNNFewShot OPTIMIZATION
# ============================================================================

def run_knn_fewshot_optimization():
    """Run KNNFewShot optimization."""

    print("KNNFewShot Optimization")
    print("=" * 60)

    # Load data
    trainset = load_training_data("training_data.jsonl")
    valset = load_training_data("validation_data.jsonl")

    print(f"Loaded {len(trainset)} training examples")
    print(f"Loaded {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()

    # Configure KNNFewShot
    optimizer = KNNFewShot(
        metric=accuracy_metric,
        k=5,  # Number of nearest neighbors to retrieve
        max_bootstrapped_demos=4,  # Max examples per prediction
    )

    print("KNNFewShot Configuration:")
    print(f"  K (neighbors): {optimizer.k}")
    print(f"  Max demos: {optimizer.max_bootstrapped_demos}")
    print("\\nStarting KNNFewShot optimization...\\n")

    # Optimize
    optimized_module = optimizer.compile(module, trainset=trainset, valset=valset)

    print("\\n✓ Optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_knn_fewshot_optimization()
'''

    def _generate_labeled_fewshot(self, task_type: str = "classification") -> str:
        """Generate LabeledFewShot optimization template."""
        return '''"""
LabeledFewShot Optimization Script

LabeledFewShot uses labeled examples for few-shot learning with quality filtering.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import LabeledFewShot
from pathlib import Path
import json

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION
# ============================================================================

def accuracy_metric(example, prediction, trace=None):
    """Calculate accuracy metric."""
    return float(prediction.output.lower() == example.output.lower())


# ============================================================================
# 3. LOAD LABELED TRAINING DATA
# ============================================================================

def load_labeled_data(file_path: str):
    """Load labeled training examples from JSONL file."""
    examples = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(
                input_text=data['input'],
                output=data['output'],
                label=data.get('label', 'high_quality')  # Quality label
            ).with_inputs('input_text'))
    return examples


# ============================================================================
# 4. LabeledFewShot OPTIMIZATION
# ============================================================================

def run_labeled_fewshot_optimization():
    """Run LabeledFewShot optimization."""

    print("LabeledFewShot Optimization")
    print("=" * 60)

    # Load labeled data
    trainset = load_labeled_data("labeled_training_data.jsonl")
    valset = load_labeled_data("validation_data.jsonl")

    print(f"Loaded {len(trainset)} labeled training examples")
    print(f"Loaded {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()

    # Configure LabeledFewShot
    optimizer = LabeledFewShot(
        metric=accuracy_metric,
        max_labeled_demos=4,  # Max labeled examples to use
        quality_threshold=0.8,  # Minimum quality score
    )

    print("LabeledFewShot Configuration:")
    print(f"  Max labeled demos: {optimizer.max_labeled_demos}")
    print(f"  Quality threshold: {optimizer.quality_threshold}")
    print("\\nStarting LabeledFewShot optimization...\\n")

    # Optimize
    optimized_module = optimizer.compile(module, trainset=trainset, valset=valset)

    print("\\n✓ Optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_labeled_fewshot_optimization()
'''

    def _generate_bootstrap_finetune(self, task_type: str = "classification") -> str:
        """Generate BootstrapFinetune optimization template."""
        return '''"""
BootstrapFinetune Optimization Script

BootstrapFinetune bootstraps examples and fine-tunes the underlying language model.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import BootstrapFinetune
from pathlib import Path
import json

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION
# ============================================================================

def accuracy_metric(example, prediction, trace=None):
    """Calculate accuracy metric."""
    return float(prediction.output.lower() == example.output.lower())


# ============================================================================
# 3. LOAD TRAINING DATA
# ============================================================================

def load_training_data(file_path: str):
    """Load training examples from JSONL file."""
    examples = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(
                input_text=data['input'],
                output=data['output']
            ).with_inputs('input_text'))
    return examples


# ============================================================================
# 4. BootstrapFinetune OPTIMIZATION
# ============================================================================

def run_bootstrap_finetune_optimization():
    """Run BootstrapFinetune optimization."""

    print("BootstrapFinetune Optimization")
    print("=" * 60)
    print("Note: This requires model fine-tuning capability")
    print("=" * 60)

    # Load data
    trainset = load_training_data("training_data.jsonl")
    valset = load_training_data("validation_data.jsonl")

    print(f"Loaded {len(trainset)} training examples")
    print(f"Loaded {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()

    # Configure BootstrapFinetune
    optimizer = BootstrapFinetune(
        metric=accuracy_metric,
        max_bootstrapped_demos=4,
        num_epochs=3,  # Fine-tuning epochs
    )

    print("BootstrapFinetune Configuration:")
    print(f"  Max bootstrapped demos: {optimizer.max_bootstrapped_demos}")
    print(f"  Fine-tuning epochs: {optimizer.num_epochs}")
    print("\\nStarting BootstrapFinetune optimization...\\n")

    # Optimize (this will bootstrap and fine-tune)
    optimized_module = optimizer.compile(module, trainset=trainset, valset=valset)

    print("\\n✓ Optimization and fine-tuning complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_bootstrap_finetune_optimization()
'''

    def _generate_avatar(self, task_type: str = "classification") -> str:
        """Generate AvatarOptimizer template."""
        return '''"""
AvatarOptimizer Script

AvatarOptimizer uses multi-agent collaboration with avatar models for reflection and improvement.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import AvatarOptimizer
from pathlib import Path
import json

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION WITH FEEDBACK
# ============================================================================

def accuracy_metric_with_feedback(example, prediction, trace=None):
    """Calculate accuracy with feedback for reflection."""
    is_correct = float(prediction.output.lower() == example.output.lower())
    feedback = "Correct" if is_correct else f"Expected: {example.output}"
    return is_correct, feedback


# ============================================================================
# 3. LOAD TRAINING DATA
# ============================================================================

def load_training_data(file_path: str):
    """Load training examples from JSONL file."""
    examples = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(
                input_text=data['input'],
                output=data['output']
            ).with_inputs('input_text'))
    return examples


# ============================================================================
# 4. AvatarOptimizer OPTIMIZATION
# ============================================================================

def run_avatar_optimization():
    """Run AvatarOptimizer optimization."""

    print("AvatarOptimizer - Multi-Agent Optimization")
    print("=" * 60)

    # Load data
    trainset = load_training_data("training_data.jsonl")
    valset = load_training_data("validation_data.jsonl")

    print(f"Loaded {len(trainset)} training examples")
    print(f"Loaded {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()

    # Configure AvatarOptimizer
    # Note: Requires reflection model (can be same as main model)
    optimizer = AvatarOptimizer(
        metric=accuracy_metric_with_feedback,
        num_avatars=3,  # Number of avatar agents
        max_iterations=10,
    )

    print("AvatarOptimizer Configuration:")
    print(f"  Number of avatars: {optimizer.num_avatars}")
    print(f"  Max iterations: {optimizer.max_iterations}")
    print("\\nStarting AvatarOptimizer optimization...\\n")

    # Optimize
    optimized_module = optimizer.compile(module, trainset=trainset, valset=valset)

    print("\\n✓ Multi-agent optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_avatar_optimization()
'''

    def _generate_simba(self, task_type: str = "classification") -> str:
        """Generate SIMBA optimization template."""
        return '''"""
SIMBA Optimization Script

SIMBA (Simple but Effective) uses iterative refinement for quick optimization.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import SIMBA
from pathlib import Path
import json

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION
# ============================================================================

def accuracy_metric(example, prediction, trace=None):
    """Calculate accuracy metric."""
    return float(prediction.output.lower() == example.output.lower())


# ============================================================================
# 3. LOAD TRAINING DATA
# ============================================================================

def load_training_data(file_path: str):
    """Load training examples from JSONL file."""
    examples = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(
                input_text=data['input'],
                output=data['output']
            ).with_inputs('input_text'))
    return examples


# ============================================================================
# 4. SIMBA OPTIMIZATION
# ============================================================================

def run_simba_optimization():
    """Run SIMBA optimization."""

    print("SIMBA Optimization - Simple but Effective")
    print("=" * 60)

    # Load data
    trainset = load_training_data("training_data.jsonl")
    valset = load_training_data("validation_data.jsonl")

    print(f"Loaded {len(trainset)} training examples")
    print(f"Loaded {len(valset)} validation examples\\n")

    # Create module
    module = YourModule()

    # Configure SIMBA
    optimizer = SIMBA(
        metric=accuracy_metric,
        max_iterations=5,  # Quick optimization
    )

    print("SIMBA Configuration:")
    print(f"  Max iterations: {optimizer.max_iterations}")
    print("\\nStarting SIMBA optimization...\\n")

    # Optimize
    optimized_module = optimizer.compile(module, trainset=trainset, valset=valset)

    print("\\n✓ SIMBA optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_module.save(output_dir / "optimized_module.json")

    return optimized_module

if __name__ == "__main__":
    run_simba_optimization()
'''

    def _generate_ensemble_optimizer(self, task_type: str = "classification") -> str:
        """Generate Ensemble Optimizer template."""
        return '''"""
Ensemble Optimizer Script

Ensemble Optimizer optimizes multiple models/predictors and combines their outputs.

Generated by DSPy Code - Optimizer Template
"""

import dspy
from dspy.teleprompt import Ensemble
from pathlib import Path
import json

# ============================================================================
# 1. YOUR MODULE
# ============================================================================

class YourSignature(dspy.Signature):
    """Your task signature."""
    input_text = dspy.InputField(desc="Input text")
    output = dspy.OutputField(desc="Output")


class YourModule(dspy.Module):
    """Your DSPy module to optimize."""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought(YourSignature)

    def forward(self, input_text):
        return self.predictor(input_text=input_text)


# ============================================================================
# 2. METRIC FUNCTION
# ============================================================================

def accuracy_metric(example, prediction, trace=None):
    """Calculate accuracy metric."""
    return float(prediction.output.lower() == example.output.lower())


# ============================================================================
# 3. LOAD TRAINING DATA
# ============================================================================

def load_training_data(file_path: str):
    """Load training examples from JSONL file."""
    examples = []
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            examples.append(dspy.Example(
                input_text=data['input'],
                output=data['output']
            ).with_inputs('input_text'))
    return examples


# ============================================================================
# 4. ENSEMBLE OPTIMIZER
# ============================================================================

def run_ensemble_optimization():
    """Run Ensemble optimization."""

    print("Ensemble Optimizer - Multiple Models")
    print("=" * 60)

    # Load data
    trainset = load_training_data("training_data.jsonl")
    valset = load_training_data("validation_data.jsonl")

    print(f"Loaded {len(trainset)} training examples")
    print(f"Loaded {len(valset)} validation examples\\n")

    # Create multiple modules (different predictors)
    modules = [
        YourModule(),  # Can use different predictors
        YourModule(),  # Or different configurations
        YourModule(),
    ]

    # Configure Ensemble Optimizer
    optimizer = Ensemble(
        metric=accuracy_metric,
        num_models=3,  # Number of models in ensemble
        aggregation_method="voting",  # or "weighted", "average"
    )

    print("Ensemble Optimizer Configuration:")
    print(f"  Number of models: {optimizer.num_models}")
    print(f"  Aggregation method: {optimizer.aggregation_method}")
    print("\\nStarting Ensemble optimization...\\n")

    # Optimize each model and combine
    optimized_ensemble = optimizer.compile(modules, trainset=trainset, valset=valset)

    print("\\n✓ Ensemble optimization complete!\\n")

    # Save
    output_dir = Path("optimization")
    output_dir.mkdir(exist_ok=True)
    optimized_ensemble.save(output_dir / "optimized_ensemble.json")

    return optimized_ensemble

if __name__ == "__main__":
    run_ensemble_optimization()
'''
