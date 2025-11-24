# Async and Streaming Support

DSPy Code supports async/await and streaming for production applications. This guide covers async execution, streaming outputs, usage tracking, caching, and logging.

## Overview

DSPy provides several features for production applications:

- **Async/Await** - Parallel execution of programs
- **Streaming** - Real-time incremental output
- **Usage Tracking** - Monitor token usage and costs
- **Caching** - Reduce costs and improve latency
- **Logging** - Debugging and monitoring

## Async/Await Support

### Asyncify

Convert synchronous DSPy programs to async for parallel execution.

**When to use:**
- Parallel execution of multiple programs
- Concurrent requests
- Async web frameworks (FastAPI, etc.)
- Better resource utilization

**Example:**

```python
import dspy
import asyncio
from dspy.utils.asyncify import asyncify

# Create your program
class QAProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought("question -> answer")

    def forward(self, question: str):
        return self.predictor(question=question)

# Convert to async
program = QAProgram()
async_program = asyncify(program)

# Use async program
async def process_questions():
    questions = [
        "What is machine learning?",
        "What is deep learning?",
        "What is neural networks?",
    ]

    # Process all questions concurrently
    tasks = [async_program(question=q) for q in questions]
    results = await asyncio.gather(*tasks)

    for question, result in zip(questions, results):
        print(f"Q: {question}")
        print(f"A: {result.answer}\n")

    return results

# Run async function
asyncio.run(process_questions())
```

**Configuration:**

```python
# Set max concurrent workers
dspy.settings.async_max_workers = 10  # Default is usually 5
```

**Benefits:**
- Parallel execution of multiple programs
- Better resource utilization
- Faster processing for batch operations
- Compatible with async web frameworks
- Non-blocking execution

## Streaming Support

### Streamify

Stream outputs incrementally instead of waiting for complete response.

**When to use:**
- Real-time user feedback
- Better user experience
- Long-running tasks
- Progressive output display

**Example:**

```python
import dspy
import asyncio
from dspy.streaming import streamify

# Create your program
class QAProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought("question -> answer")

    def forward(self, question: str):
        return self.predictor(question=question)

# Convert to streaming
program = QAProgram()
streaming_program = streamify(
    program,
    include_final_prediction_in_output_stream=True,
    async_streaming=True
)

# Use streaming program
async def stream_response():
    question = "What is machine learning?"

    print(f"Q: {question}\n")
    print("A: ", end="", flush=True)

    async for chunk in streaming_program(question=question):
        if hasattr(chunk, 'answer'):
            # Stream the answer field
            print(chunk.answer, end="", flush=True)
        elif isinstance(chunk, str):
            # Stream text directly
            print(chunk, end="", flush=True)

    print("\n")  # New line after streaming

# Run streaming
asyncio.run(stream_response())
```

**Custom Status Messages:**

```python
from dspy.streaming.messages import StatusMessageProvider

class CustomStatusProvider(StatusMessageProvider):
    """Custom status message provider."""

    def get_status_message(self, module_name: str, status: str) -> str:
        """Generate custom status messages."""
        messages = {
            "starting": f"🚀 Starting {module_name}...",
            "processing": f"⚙️  Processing with {module_name}...",
            "complete": f"✓ {module_name} complete",
        }
        return messages.get(status, f"{module_name}: {status}")

# Use custom status provider
streaming_with_status = streamify(
    program,
    status_message_provider=CustomStatusProvider(),
    include_final_prediction_in_output_stream=True
)
```

**Stream Specific Fields:**

```python
from dspy.streaming.streaming_listener import StreamListener

# Create listener for specific field
answer_listener = StreamListener(
    target_module="QAProgram",
    target_field="answer"
)

streaming_with_listener = streamify(
    program,
    stream_listeners=[answer_listener],
    include_final_prediction_in_output_stream=True
)
```

**Benefits:**
- Real-time user feedback
- Better user experience
- Progressive output display
- Lower perceived latency
- Works with streaming-capable models

## Usage Tracking

Monitor token usage, API calls, and costs.

**Example:**

```python
import dspy
from dspy.utils.usage_tracker import UsageTracker

# Configure DSPy
dspy.configure(
    lm=dspy.LM(model="openai/gpt-4o")
)

# Create program
program = YourProgram()

# Track usage
tracker = UsageTracker()
tracker.reset()

# Run program
result = program(input="...")

# Get usage statistics
stats = tracker.get_stats()

print("Usage Statistics:")
print(f"Total tokens: {stats.get('total_tokens', 0)}")
print(f"Total cost: ${stats.get('total_cost', 0):.4f}")
print(f"API calls: {stats.get('api_calls', 0)}")
print(f"Cache hits: {stats.get('cache_hits', 0)}")
print(f"Cache misses: {stats.get('cache_misses', 0)}")
```

**Export Usage Data:**

```python
import json
from pathlib import Path

tracker = UsageTracker()
stats = tracker.get_stats()

# Export to JSON
output_file = Path("usage_stats.json")
with open(output_file, 'w') as f:
    json.dump(stats, f, indent=2)

print(f"✓ Exported usage data to {output_file}")
```

**Benefits:**
- Monitor costs in real-time
- Optimize token usage
- Budget management
- Performance analysis
- Cost per request tracking

## Caching

Cache LM responses to reduce costs and improve latency.

**Example:**

```python
import dspy
import os

# Set cache directory
os.environ['DSPY_CACHEDIR'] = './.dspy_cache'

# Configure DSPy
dspy.configure(
    lm=dspy.LM(model="openai/gpt-4o")
)

# Create program
program = YourProgram()

# First call - will be cached
result1 = program(input="What is DSPy?")

# Second call - will use cache (same result)
result2 = program(input="What is DSPy?")

# Third call with rollout_id - bypasses cache, gets fresh response
result3 = program(
    input="What is DSPy?",
    config={"rollout_id": "fresh_1", "temperature": 1.0}
)
```

**Cache Statistics:**

```python
from pathlib import Path

cache_dir = "./.dspy_cache"
cache_path = Path(cache_dir)

if cache_path.exists():
    cache_files = list(cache_path.glob("*.cache"))

    print("Cache Statistics:")
    print(f"Cache files: {len(cache_files)}")

    total_size = sum(f.stat().st_size for f in cache_files)
    print(f"Total cache size: {total_size / 1024 / 1024:.2f} MB")
```

**Clear Cache:**

```python
from pathlib import Path
import shutil

cache_path = Path("./.dspy_cache")
if cache_path.exists():
    shutil.rmtree(cache_path)
    cache_path.mkdir()
    print("✓ Cleared cache")
```

**Benefits:**
- Reduced API costs (repeated queries use cache)
- Faster responses (cache hits are instant)
- Consistent results for same inputs
- Can bypass cache with rollout_id when needed
- Automatic cache management

## Logging

Configure logging for debugging and monitoring.

**Example:**

```python
import dspy
import logging
from dspy.utils.logging_utils import setup_logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dspy.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Set DSPy log level
dspy.settings.log_level = logging.INFO

# Or use DSPy's logging utils
setup_logging(level=logging.INFO)

# Program with logging
class QAProgram(dspy.Module):
    def __init__(self):
        super().__init__()
        self.predictor = dspy.ChainOfThought("question -> answer")
        self.logger = logging.getLogger(self.__class__.__name__)

    def forward(self, question: str):
        self.logger.info(f"Processing question: {question}")

        try:
            result = self.predictor(question=question)
            self.logger.info(f"Generated answer: {result.answer[:50]}...")
            return result
        except Exception as e:
            self.logger.error(f"Error processing question: {e}", exc_info=True)
            raise
```

**Structured Logging:**

```python
import json

def log_structured(level, message, **kwargs):
    log_entry = {
        "level": level,
        "message": message,
        **kwargs
    }
    print(json.dumps(log_entry))

# Use structured logging
log_structured("INFO", "Processing question", question="What is DSPy?")
log_structured("INFO", "Generated answer", answer="DSPy is a framework...")
```

**Benefits:**
- Debug issues in production
- Monitor program behavior
- Track performance metrics
- Audit trail of operations
- Troubleshooting support

## Using Async/Streaming in DSPy Code

### Via Slash Commands

Show async support:

```bash
/async                  # Show async support overview
/async example         # Generate async example code
```

Show streaming support:

```bash
/streaming             # Show streaming support overview
/streaming example     # Generate streaming example code
```

### Via Natural Language

Ask about async/streaming:

```
How do I use async in DSPy?
Show me streaming examples
Tell me about usage tracking
```

### Via Code Generation

Request async/streaming code:

```
Create an async version of my program
Build a streaming response system
Add usage tracking to my program
```

## Best Practices

### 1. Async Execution

- **Batch operations**: Use async for processing multiple items
- **Concurrent limits**: Set appropriate `async_max_workers`
- **Error handling**: Handle exceptions in async tasks
- **Resource management**: Monitor resource usage

### 2. Streaming

- **User experience**: Use streaming for better UX
- **Progress indicators**: Show status messages
- **Field selection**: Stream only relevant fields
- **Error handling**: Handle streaming errors gracefully

### 3. Usage Tracking

- **Regular monitoring**: Check usage regularly
- **Cost optimization**: Identify expensive operations
- **Budget alerts**: Set up alerts for high usage
- **Export data**: Export for analysis

### 4. Caching

- **Cache strategy**: Decide what to cache
- **Cache invalidation**: Clear cache when needed
- **Fresh responses**: Use rollout_id for fresh results
- **Cache size**: Monitor cache size

### 5. Logging

- **Log levels**: Use appropriate log levels
- **Structured logging**: Use structured format for production
- **Log rotation**: Rotate logs to manage size
- **Security**: Don't log sensitive data

## Troubleshooting

### Async Issues

- **Import errors**: Ensure `asyncer` is installed
- **Deadlocks**: Check for blocking operations
- **Resource limits**: Adjust `async_max_workers`
- **Error propagation**: Handle exceptions properly

### Streaming Issues

- **Model support**: Ensure model supports streaming
- **Field access**: Check field names match signature
- **Status messages**: Verify status provider implementation
- **Performance**: Monitor streaming performance

### Usage Tracking Issues

- **Missing data**: Ensure tracking is enabled
- **Cost calculation**: Verify cost calculation logic
- **Export errors**: Check file permissions
- **Statistics**: Verify statistics calculation

### Caching Issues

- **Cache not working**: Check cache directory permissions
- **Stale cache**: Clear cache when needed
- **Cache size**: Monitor and manage cache size
- **Bypass cache**: Use rollout_id correctly

## Next Steps

- Learn about [Optimization](optimization.md) to improve performance
- Explore [RAG Systems](../tutorials/rag-system.md) for RAG-specific patterns
- Check [Evaluation](evaluation.md) to measure performance
- See [Complete Programs](../tutorials/sentiment-analyzer.md) for full examples

## Additional Resources

- [DSPy Async Documentation](https://dspy-docs.vercel.app/docs/advanced/async)
- [DSPy Streaming Documentation](https://dspy-docs.vercel.app/docs/advanced/streaming)
- Use `/async` and `/streaming` in the CLI for examples
- Use `/explain async` or `/explain streaming` for detailed explanations
