# DSPy Adapters Guide

Adapters in DSPy are the interface layer between DSPy modules and Language Models (LMs). They handle the transformation pipeline from DSPy inputs to LM calls and back to structured outputs. Adapters format prompts, parse responses, and manage conversation history.

## What are Adapters?

Adapters sit between your DSPy signatures/modules and the language model. They:

- **Format** your signature fields into prompts the LM understands
- **Parse** LM responses back into structured DSPy outputs
- **Handle** different output formats (JSON, XML, chat, etc.)
- **Support** special features like function calling and structured outputs

## Available Adapters

DSPy Code supports four main adapters:

### 1. ChatAdapter (Default)

The default adapter for natural language interactions.

**When to use:**
- General use cases
- Conversational AI applications
- When you don't need strict structured output
- Default choice for most applications

**Example:**

```python
import dspy

# ChatAdapter is the default
dspy.configure(
    lm=dspy.LM(model="openai/gpt-4o"),
    adapter=dspy.ChatAdapter()  # Optional, this is default
)

class QASignature(dspy.Signature):
    question = dspy.InputField(desc="User's question")
    answer = dspy.OutputField(desc="Natural language answer")

qa = dspy.ChainOfThought(QASignature)
result = qa(question="What is machine learning?")
```

### 2. JSONAdapter

Structured JSON output with native function calling support.

**When to use:**
- Structured data extraction
- API responses
- When you need guaranteed JSON format
- Native function calling support

**Features:**
- ✅ Structured outputs (when supported)
- ✅ Native function calling
- ✅ Automatic JSON mode fallback
- ✅ Works with Pydantic models

**Example:**

```python
import dspy
import pydantic

# Configure with JSONAdapter
dspy.configure(
    lm=dspy.LM(model="openai/gpt-4o"),
    adapter=dspy.JSONAdapter()
)

class Address(pydantic.BaseModel):
    street: str
    city: str
    zip_code: str

class PersonInfo(dspy.Signature):
    text = dspy.InputField(desc="Text containing person information")
    name = dspy.OutputField(desc="Person's name")
    age = dspy.OutputField(desc="Person's age")
    address = Address = dspy.OutputField(desc="Person's address")

extractor = dspy.Predict(PersonInfo)
result = extractor(text="John Smith, age 30, lives at 123 Main St, New York, NY 10001")
```

### 3. XMLAdapter

XML-formatted output for structured responses.

**When to use:**
- XML-based systems
- Legacy integrations
- When you need XML format
- Human-readable structured output

**Example:**

```python
import dspy

# Configure with XMLAdapter
dspy.configure(
    lm=dspy.LM(model="openai/gpt-4o"),
    adapter=dspy.XMLAdapter()
)

class ExtractionSignature(dspy.Signature):
    text = dspy.InputField(desc="Text to extract information from")
    entity = dspy.OutputField(desc="Extracted entity name")
    type = dspy.OutputField(desc="Entity type")

extractor = dspy.ChainOfThought(ExtractionSignature)
result = extractor(text="Apple Inc. was founded by Steve Jobs in Cupertino.")
```

**XML Format:**

```
<entity>
Apple Inc.
</entity>

<type>
ORGANIZATION
</type>
```

### 4. TwoStepAdapter

Two-stage processing: main LM for reasoning, smaller LM for extraction.

**When to use:**
- Using reasoning models (o3, o1)
- When main model struggles with structured output
- Cost optimization (expensive reasoning + cheap extraction)
- Complex extraction tasks

**How it works:**

1. **Step 1**: Main LM (reasoning model) receives the problem and generates a natural language response with reasoning
2. **Step 2**: Extraction LM (smaller model) receives the main LM's response and extracts structured fields using ChatAdapter

**Example:**

```python
import dspy

# Main model: Reasoning model (expensive)
main_lm = dspy.LM(
    model="openai/o3-mini",
    max_tokens=16000,
    temperature=1.0
)

# Extraction model: Smaller, cheaper model
extraction_lm = dspy.LM(model="openai/gpt-4o-mini")

# Create TwoStepAdapter
adapter = dspy.TwoStepAdapter(extraction_model=extraction_lm)

# Configure
dspy.configure(
    lm=main_lm,  # Main reasoning model
    adapter=adapter
)

class ComplexReasoningSignature(dspy.Signature):
    problem = dspy.InputField(desc="Complex problem to solve")
    reasoning = dspy.OutputField(desc="Step-by-step reasoning")
    answer = dspy.OutputField(desc="Final answer")
    confidence = dspy.OutputField(desc="Confidence level")

reasoner = dspy.ChainOfThought(ComplexReasoningSignature)
result = reasoner(problem="If a train travels 60 mph for 2.5 hours, how far does it go?")
```

## Using Adapters in DSPy Code

### Via Slash Commands

List all adapters:

```bash
/adapters
```

Get details for a specific adapter:

```bash
/adapters json
/adapters xml
/adapters chat
/adapters two-step
```

### Via Natural Language

Ask about adapters:

```
What is JSONAdapter?
Explain TwoStepAdapter
Tell me about all adapters
```

### Via Code Generation

Request adapter usage:

```
Create a module using JSONAdapter for structured output
Build a system with TwoStepAdapter for reasoning models
Generate code with XMLAdapter
```

## Choosing the Right Adapter

| Adapter | Best For | Difficulty |
|---------|----------|------------|
| **ChatAdapter** | General use, conversational AI | Beginner |
| **JSONAdapter** | Structured data, APIs, JSON format | Beginner |
| **XMLAdapter** | XML systems, legacy integration | Beginner |
| **TwoStepAdapter** | Reasoning models, cost optimization | Advanced |

## Configuration

### Global Configuration

Set adapter globally for all DSPy operations:

```python
dspy.configure(
    lm=dspy.LM(model="openai/gpt-4o"),
    adapter=dspy.JSONAdapter()
)
```

### Context-Specific Configuration

Use a specific adapter in a context:

```python
with dspy.context(adapter=dspy.XMLAdapter()):
    result = predictor(input="...")
```

## Advanced Features

### JSONAdapter with Pydantic Models

JSONAdapter supports complex nested structures using Pydantic:

```python
import pydantic
import dspy

class Address(pydantic.BaseModel):
    street: str
    city: str
    zip_code: str

class Person(dspy.Signature):
    text = dspy.InputField()
    name = dspy.OutputField()
    address = Address = dspy.OutputField()
```

### TwoStepAdapter Cost Optimization

TwoStepAdapter can be more cost-effective:

- **Main LM** (o3-mini): Used for complex reasoning (expensive)
- **Extraction LM** (gpt-4o-mini): Used only for simple extraction (cheap)

This can be more cost-effective than using a single expensive model for both reasoning and structured output.

## Troubleshooting

### JSONAdapter Issues

If structured outputs fail, JSONAdapter automatically falls back to JSON mode. Check:

- Model supports structured outputs (e.g., gpt-4o, claude-3.5-sonnet)
- No open-ended dict types in output fields
- Native function calling enabled (default)

### TwoStepAdapter Issues

Ensure:

- Main LM is a reasoning model (o3, o1)
- Extraction LM is smaller and cheaper
- Both models are properly configured

## Next Steps

- Learn about [Generating Code](generating-code.md) to create modules with adapters
- Explore [Optimization](optimization.md) to improve your programs
- Check [Validation](validation.md) to ensure code quality
- See [Complete Programs](../tutorials/sentiment-analyzer.md) for full examples

## Additional Resources

- [DSPy Adapters Documentation](https://dspy-docs.vercel.app/docs/building-blocks/adapters)
- Use `/explain adapter <name>` in the CLI for detailed explanations
- Use `/adapters` to see all available adapters
