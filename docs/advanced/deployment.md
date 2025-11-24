# Deployment

Guide to deploying DSPy programs built with DSPy Code to production.

---

## Overview

This guide covers deploying DSPy programs created with DSPy Code to production environments.

---

## Pre-Deployment Checklist

### 1. Code Validation

Ensure your code is validated:

```bash
dspy-code
> /validate my_program.py
```

**Check for:**
- Syntax errors
- Missing imports
- Incorrect signatures
- Best practice violations

---

### 2. Optimization

Optimize your program for production:

```bash
dspy-code
> /optimize my_program.py training_data.jsonl
```

**Benefits:**
- Better performance
- Reduced latency
- Lower costs
- Improved accuracy

---

### 3. Testing

Test thoroughly before deployment:

```bash
dspy-code
> /run my_program.py --test-file test_data.jsonl
```

**Test Coverage:**
- Edge cases
- Error handling
- Performance benchmarks
- Integration tests

---

## Deployment Options

### Option 1: Python Package

Package your DSPy program as a Python package.

**Structure:**
```
my_dspy_app/
├── __init__.py
├── program.py
├── requirements.txt
├── setup.py
└── README.md
```

**requirements.txt:**
```
dspy>=3.0.0
openai>=1.0.0
anthropic>=0.18.0
```

**Install:**
```bash
pip install -e .
```

---

### Option 2: Docker Container

Containerize your DSPy application.

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "my_program.py"]
```

**Build:**
```bash
docker build -t my-dspy-app .
```

**Run:**
```bash
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY my-dspy-app
```

---

### Option 3: API Service

Deploy as a REST API using FastAPI or Flask.

**FastAPI Example:**
```python
from fastapi import FastAPI
from my_program import MyDSPyProgram

app = FastAPI()
program = MyDSPyProgram()

@app.post("/predict")
async def predict(input_data: dict):
    result = program(**input_data)
    return {"result": result}
```

**Deploy:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

### Option 4: Serverless

Deploy to serverless platforms.

#### AWS Lambda

```python
import json
from my_program import MyDSPyProgram

program = MyDSPyProgram()

def lambda_handler(event, context):
    input_data = json.loads(event['body'])
    result = program(**input_data)
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

#### Google Cloud Functions

```python
from my_program import MyDSPyProgram

program = MyDSPyProgram()

def predict(request):
    input_data = request.get_json()
    result = program(**input_data)
    return {'result': result}
```

---

## Environment Configuration

### Environment Variables

Set required environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export DSPY_MODEL="gpt-4o"
```

### Configuration Files

Use `dspy_config.yaml` for deployment:

```yaml
models:
  default: production-model
  providers:
    - name: production-model
      type: openai
      model: gpt-4o
      api_key: ${OPENAI_API_KEY}
```

---

## Monitoring & Logging

### Logging Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Metrics Collection

Track key metrics:
- Request latency
- Token usage
- Error rates
- Cost per request

---

## Performance Optimization

### Caching

Cache frequent requests:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_prediction(input_text):
    return program(input_text)
```

### Batch Processing

Process multiple inputs together:

```python
def batch_predict(inputs):
    results = []
    for input in inputs:
        results.append(program(**input))
    return results
```

### Async Processing

Use async for better concurrency:

```python
import asyncio

async def async_predict(input_data):
    return await asyncio.to_thread(program, **input_data)
```

---

## Security Best Practices

### API Key Management

- Never commit API keys
- Use environment variables
- Rotate keys regularly
- Use least privilege access

### Input Validation

```python
def validate_input(input_data):
    if not isinstance(input_data, dict):
        raise ValueError("Input must be a dictionary")
    # Additional validation
    return input_data
```

### Rate Limiting

Implement rate limiting to prevent abuse:

```python
from functools import wraps
import time

def rate_limit(max_calls=100, period=60):
    calls = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - period]
            if len(calls) >= max_calls:
                raise Exception("Rate limit exceeded")
            calls.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Deploy DSPy App

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Validate
        run: |
          dspy-code /validate my_program.py
      - name: Deploy
        run: |
          # Your deployment commands
```

---

## Scaling Considerations

### Horizontal Scaling

- Use load balancers
- Deploy multiple instances
- Use message queues for async processing

### Vertical Scaling

- Increase compute resources
- Optimize model selection
- Use caching strategies

### Cost Optimization

- Monitor token usage
- Use appropriate models for tasks
- Implement caching
- Batch requests when possible

---

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
pip install -r requirements.txt
```

**API Key Issues:**
```bash
export OPENAI_API_KEY="your-key"
```

**Model Connection:**
```bash
dspy-code
> /connect openai gpt-4o
```

---

## Best Practices

1. **Validate Before Deploy** - Always validate code
2. **Optimize for Production** - Use GEPA optimization
3. **Monitor Performance** - Track metrics
4. **Secure Secrets** - Never commit API keys
5. **Test Thoroughly** - Comprehensive testing
6. **Document Deployment** - Clear deployment docs
7. **Version Control** - Track deployments
8. **Rollback Plan** - Prepare for issues

---

**For more details, see [CI/CD Integration](cicd.md)**
