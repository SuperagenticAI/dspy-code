# Understanding DSPy Code

Learn how DSPy Code works and how it helps you build better DSPy programs.

## What is DSPy Code?

DSPy Code is an **interactive development environment** for DSPy that:

- Generates DSPy code from natural language
- Validates your code against best practices
- Helps you optimize programs with GEPA
- Provides a knowledge base about DSPy concepts
- Adapts to your installed DSPy version

## Core Concepts

### 1. Living Playbook

DSPy Code is a "living playbook" that:

**Adapts to YOUR DSPy version:**

- Indexes your installed DSPy package
- Answers questions based on YOUR version
- Generates code compatible with YOUR installation

**Understands your project:**

- Scans your existing DSPy code
- Learns your patterns and conventions
- Generates code that fits your project

**Stays current:**

- Re-indexes when you run `/init`
- Detects version changes
- Warns about outdated versions

### 2. Interactive-Only Design

All commands are slash commands in interactive mode:

```
dspy-code
  → /init
  → /model
  → Create a sentiment analyzer
  → /save sentiment.py
  → /validate
  → /run
```

**Why interactive-only?**

- Natural conversation flow
- Context-aware responses
- Better error handling
- Easier to learn

### 3. Natural Language Generation

Describe what you want in plain English:

```
Build a module for sentiment analysis with text input and sentiment output
```

DSPy Code generates:

- Complete Signature
- Module implementation
- Example usage
- Configuration code

### 4. Version Awareness

DSPy Code shows your DSPy version on startup:

```
✓ DSPy Version: 3.0.4
```

If your version is old:

```
✓ DSPy Version: 2.5.0 (Old! Consider upgrading to >=3.0.0)
```

**Why this matters:**

- DSPy APIs change between versions
- Generated code matches YOUR version
- Avoid compatibility issues

## Architecture

### Components

```
DSPy Code
├── Interactive Session
│   ├── Natural language processing
│   ├── Context management
│   └── Conversation history
├── Code Generation
│   ├── Signature generator
│   ├── Module generator
│   └── Program templates
├── Validation Engine
│   ├── Syntax checker
│   ├── Best practices validator
│   └── Quality scorer
├── Optimization
│   ├── GEPA integration
│   ├── Metric generation
│   └── Data collection
├── Codebase RAG
│   ├── DSPy indexer
│   ├── Project scanner
│   └── Semantic search
└── Model Connector
    ├── Ollama
    ├── OpenAI
    ├── Anthropic
    └── Gemini
```

### Data Flow

```
User Input
    ↓
Natural Language Understanding
    ↓
Intent Detection
    ↓
Code Generation / Command Execution
    ↓
Validation (if code)
    ↓
Response to User
```

## How Code Generation Works

### Step 1: Intent Detection

DSPy Code analyzes your request:

```
"Build a module for sentiment analysis"
```

Detected intent:

- **Type**: Module generation
- **Task**: Sentiment analysis
- **Predictor**: Not specified (will use default)

### Step 2: Signature Generation

Creates the DSPy Signature:

```python
class SentimentSignature(dspy.Signature):
    """Analyze sentiment of text."""
    text = dspy.InputField(desc="Text to analyze")
    sentiment = dspy.OutputField(desc="positive, negative, or neutral")
```

### Step 3: Module Generation

Creates the Module:

```python
class SentimentAnalyzer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(SentimentSignature)

    def forward(self, text):
        return self.predictor(text=text)
```

### Step 4: Add Usage Examples

Includes example code:

```python
# Example usage
analyzer = SentimentAnalyzer()
result = analyzer(text="I love this!")
print(result.sentiment)
```

### Step 5: Context Storage

Stores in session context:

```python
context['last_generated'] = code
context['type'] = 'module'
```

Now you can use `/save`, `/validate`, `/run`!

## How Validation Works

### Validation Checks

**1. Signature Validation:**

- ✅ Inherits from dspy.Signature
- ✅ Has InputField and OutputField
- ✅ Fields have descriptions
- ✅ Docstring present

**2. Module Validation:**

- ✅ Inherits from dspy.Module
- ✅ Has `__init__` method
- ✅ Has `forward` method
- ✅ Uses DSPy predictors

**3. Best Practices:**

- ✅ Type hints used
- ✅ Descriptive names
- ✅ No anti-patterns
- ✅ Proper error handling

**4. Syntax:**

- ✅ Valid Python
- ✅ No syntax errors
- ✅ Imports present

### Quality Scoring

Each check contributes to a quality score:

```
Signature structure: 20 points
Module structure: 20 points
Best practices: 30 points
Documentation: 15 points
Type hints: 15 points

Total: 100 points
```

**Score interpretation:**

- 90-100: Excellent
- 80-89: Good
- 70-79: Acceptable
- <70: Needs improvement

## How Codebase RAG Works

### Indexing Process

**1. Discovery:**

```
Discovering codebases...
  ✓ Found DSPy 3.0.4
  ✓ Found GEPA 1.2.0
  ✓ Found project code
```

**2. Scanning:**

```
Scanning Python files...
  ✓ 150 files in DSPy
  ✓ 45 files in GEPA
  ✓ 12 files in your project
```

**3. Extraction:**

```
Extracting structure...
  ✓ 234 classes
  ✓ 1,456 functions
  ✓ 89 signatures
```

**4. Indexing:**

```
Building search index...
  ✓ 3,421 code elements indexed
  ✓ Cache saved
```

### Answering Questions

When you ask a question:

```
How does ChainOfThought work?
```

**1. Search:**

- Semantic search in indexed code
- Find relevant classes/functions
- Rank by relevance

**2. Context Building:**

- Extract code snippets
- Get docstrings
- Find usage examples

**3. Answer Generation:**

- Use LLM with context
- Generate explanation
- Include code examples

**4. Response:**

```
ChainOfThought is a DSPy predictor that uses reasoning...

Example from your DSPy version:

class ChainOfThought(Predict):
    def __init__(self, signature, rationale_type=None, **config):
        ...
```

## How Optimization Works

### GEPA Overview

GEPA (Genetic Pareto) optimizes DSPy programs by:

1. **Evaluation**: Test current performance
2. **Reflection**: Analyze failures
3. **Evolution**: Generate better prompts
4. **Selection**: Keep best versions
5. **Iteration**: Repeat until optimal

!!! warning "Optimization Cost & Resource Considerations"
    - **Cloud models (OpenAI, Anthropic, Gemini)**: GEPA can trigger **many LLM calls**. Only run optimization if you understand the potential API cost and have billing/quotas configured appropriately.
    - **Local runs**: For smooth optimization on local hardware, we recommend at least **32 GB RAM**, especially with larger models.
    - Start with small budgets and fewer examples when experimenting.

### Optimization Process

**1. Prepare Data:**

```
/generate data 50 for sentiment analysis
/save-data sentiment_data.jsonl
```

**2. Generate Optimization Script:**

```
/optimize sentiment_analyzer.py sentiment_data.jsonl
```

**3. Run GEPA:**

```python
from dspy.teleprompt import GEPA

optimizer = GEPA(
    metric=accuracy_with_feedback,
    breadth=10,
    depth=3,
    init_temperature=1.4
)

optimized = optimizer.compile(
    program,
    trainset=examples
)
```

**4. Results:**

```
Initial: 75% accuracy
Final: 92% accuracy
Improvement: +17%
```

### Metrics with Feedback

GEPA uses metrics that provide feedback:

```python
def accuracy_with_feedback(gold, pred, trace=None):
    if gold.sentiment == pred.sentiment:
        return 1.0
    else:
        feedback = f"Expected {gold.sentiment}, got {pred.sentiment}"
        return {'score': 0.0, 'feedback': feedback}
```

This feedback helps GEPA learn!

## How Model Connection Works

### Supported Providers

**1. Ollama (Local):**

```
/connect ollama llama3.1:8b
```

**2. OpenAI (modern SDK, example small model):**

```
/connect openai gpt-5-nano
```

**3. Anthropic (paid only, optional):**

```
/connect anthropic claude-sonnet-4.5
```

> Anthropic no longer offers free API keys. If you have a paid key, DSPy Code will work with Claude; otherwise, just skip Anthropic and use another provider.

**4. Gemini (via google-genai):**

```
/connect gemini gemini-2.5-flash
```

### Connection Process

**1. Validation:**

- Check provider is valid
- Verify model name
- Test API key (if needed)

**2. Configuration:**

```python
if provider == "ollama":
    lm = dspy.OllamaLocal(model=model_name)
elif provider == "openai":
    lm = dspy.OpenAI(model=model_name, api_key=api_key)
```

**3. Testing:**

```
Testing connection...
  ✓ Model responds
  ✓ Connection stable
```

**4. Storage:**

```yaml
# dspy_config.yaml
models:
  default: ollama/llama3.1:8b
  ollama:
    llama3.1:8b:
      base_url: http://localhost:11434
```

## Session Management

### Session Context

Each session maintains:

```python
context = {
    'last_generated': "...",  # Last generated code
    'type': 'module',         # Code type
    'last_generated_data': [...],  # Training data
    'data_task': 'sentiment',  # Task description
    'history': [...]          # Conversation history
}
```

### Persistence

**Save session:**

```
/session save my-work
```

**Load session:**

```
/session load my-work
```

**List sessions:**

```
/sessions list
```

### What's Saved

- Generated code
- Training data
- Model configuration
- Conversation history
- Project context

## Configuration

### Project Configuration

`dspy_config.yaml`:

```yaml
project_name: my-dspy-project
dspy_version: 3.0.4

models:
  default: ollama/llama3.1:8b
  ollama:
    llama3.1:8b:
      base_url: http://localhost:11434

paths:
  generated: generated/
  data: data/
  cache: .cache/

rag:
  enabled: true
  cache_ttl: 86400
```

### User Configuration

`~/.dspy-code/config.yaml`:

```yaml
default_model: ollama/llama3.1:8b
verbose: false
auto_save: true
```

## Best Practices

### 1. Always Initialize

Run `/init` when starting a new project:

```
/init
```

This builds the codebase index!

### 2. Check Status Often

Use `/status` to see what's in context:

```
/status
```

### 3. Validate Before Running

Always validate generated code:

```
/validate
/run
```

### 4. Save Your Work

Save sessions for complex projects:

```
/session save project-name
```

### 5. Use Descriptive Requests

Be specific when generating code:

```
Good: "Build a module using ChainOfThought for sentiment analysis with text input and sentiment output"

Bad: "Make a sentiment thing"
```

### 6. Iterate

Refine generated code:

```
Add error handling to the last generated code
Add type hints to all functions
Optimize for better performance
```

## Troubleshooting

### Code Not Saving

Check context:

```
/status
```

If no code in context, generate first:

```
Create a simple signature
/save my_signature.py
```

### Validation Fails

Read error messages:

```
/validate
```

Fix issues:

```
Fix the validation errors in the last generated code
```

### Model Not Connected

Check status:

```
/status
```

Connect:

```
/connect ollama llama3.1:8b
```

### Index Not Built

Run init:

```
/init
```

## Summary

DSPy Code is:

- ✅ Interactive development environment
- ✅ Natural language code generator
- ✅ Validation and quality checker
- ✅ GEPA optimization platform
- ✅ DSPy knowledge base
- ✅ Version-aware assistant

**Start building better DSPy programs today!**

[Build Your First Program →](first-program.md){ .md-button .md-button--primary }
[Learn Slash Commands →](../guide/slash-commands.md){ .md-button }
