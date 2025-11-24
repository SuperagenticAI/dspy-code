# CI/CD Integration

Integrate DSPy Code into your CI/CD pipeline for automated testing, validation, and deployment.

---

## Overview

This guide shows how to integrate DSPy Code into continuous integration and continuous deployment pipelines.

---

## GitHub Actions

### Basic Workflow

```yaml
name: DSPy Code CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install DSPy Code
        run: |
          pip install dspy-code
          pip install dspy

      - name: Validate Code
        run: |
          dspy-code /validate my_program.py

      - name: Run Tests
        run: |
          pytest tests/
```

### Advanced Workflow

```yaml
name: DSPy Code CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        run: |
          pip install flake8 black mypy
      - name: Lint
        run: |
          flake8 dspy_code/
          black --check dspy_code/
          mypy dspy_code/

  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        run: |
          pip install dspy-code dspy
      - name: Validate programs
        run: |
          for file in programs/*.py; do
            dspy-code /validate "$file"
          done

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: |
          pytest tests/ --cov=dspy_code --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  optimize:
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - name: Install dependencies
        run: |
          pip install dspy-code dspy gepa
      - name: Optimize programs
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          dspy-code /optimize my_program.py training_data.jsonl

  deploy:
    needs: [lint, validate, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          # Your deployment commands
          echo "Deploying to production..."
```

---

## GitLab CI

### .gitlab-ci.yml

```yaml
stages:
  - validate
  - test
  - optimize
  - deploy

variables:
  PYTHON_VERSION: "3.11"

validate:
  stage: validate
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install dspy-code dspy
  script:
    - dspy-code /validate my_program.py
  only:
    - merge_requests
    - main

test:
  stage: test
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install -r requirements.txt
    - pip install pytest
  script:
    - pytest tests/
  coverage: '/TOTAL.*\s+(\d+%)$/'

optimize:
  stage: optimize
  image: python:${PYTHON_VERSION}
  before_script:
    - pip install dspy-code dspy gepa
  script:
    - dspy-code /optimize my_program.py training_data.jsonl
  only:
    - main
  when: manual

deploy:
  stage: deploy
  image: python:${PYTHON_VERSION}
  script:
    - echo "Deploying to production..."
    # Your deployment commands
  only:
    - main
  when: manual
```

---

## Jenkins

### Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.11'
    }

    stages {
        stage('Install') {
            steps {
                sh '''
                    python${PYTHON_VERSION} -m venv venv
                    . venv/bin/activate
                    pip install dspy-code dspy
                '''
            }
        }

        stage('Validate') {
            steps {
                sh '''
                    . venv/bin/activate
                    dspy-code /validate my_program.py
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    . venv/bin/activate
                    pip install pytest
                    pytest tests/
                '''
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    echo "Deploying to production..."
                    # Your deployment commands
                '''
            }
        }
    }
}
```

---

## CircleCI

### .circleci/config.yml

```yaml
version: 2.1

jobs:
  validate:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: |
            pip install dspy-code dspy
      - run:
          name: Validate
          command: |
            dspy-code /validate my_program.py

  test:
    docker:
      - image: cimg/python:3.11
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: |
            pip install -r requirements.txt
            pip install pytest
      - run:
          name: Run tests
          command: |
            pytest tests/

workflows:
  version: 2
  validate_and_test:
    jobs:
      - validate
      - test
```

---

## Azure DevOps

### azure-pipelines.yml

```yaml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.11'

  - script: |
      pip install dspy-code dspy
    displayName: 'Install dependencies'

  - script: |
      dspy-code /validate my_program.py
    displayName: 'Validate code'

  - script: |
      pip install pytest
      pytest tests/
    displayName: 'Run tests'

  - script: |
      echo "Deploying to production..."
    displayName: 'Deploy'
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
```

---

## Pre-commit Hooks

### .pre-commit-config.yaml

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-dspy
        name: Validate DSPy Code
        entry: dspy-code
        args: ['/validate']
        language: system
        files: \.py$
        pass_filenames: true

      - id: black
        name: Format with Black
        entry: black
        language: system
        files: \.py$

      - id: flake8
        name: Lint with Flake8
        entry: flake8
        language: system
        files: \.py$
```

**Install:**
```bash
pip install pre-commit
pre-commit install
```

---

## Best Practices

### 1. Validate Early

Run validation in CI before tests:

```yaml
- name: Validate
  run: dspy-code /validate my_program.py
```

### 2. Test Coverage

Maintain high test coverage:

```yaml
- name: Test with coverage
  run: pytest --cov=dspy_code --cov-report=xml
```

### 3. Optimize on Main

Only optimize on main branch:

```yaml
if: github.ref == 'refs/heads/main'
```

### 4. Secure Secrets

Use secrets for API keys:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

### 5. Parallel Jobs

Run jobs in parallel:

```yaml
jobs:
  lint:
    # ...
  test:
    # ...
  validate:
    # ...
```

### 6. Conditional Deployment

Deploy only after all checks pass:

```yaml
needs: [lint, test, validate]
```

---

## Monitoring

### Integration Tests

```python
def test_program_integration():
    """Test program in CI environment."""
    program = MyDSPyProgram()
    result = program(input="test")
    assert result is not None
```

### Performance Benchmarks

```python
import time

def benchmark_program():
    """Benchmark program performance."""
    program = MyDSPyProgram()
    start = time.time()
    result = program(input="test")
    duration = time.time() - start
    assert duration < 5.0  # Max 5 seconds
```

---

## Troubleshooting

### Common Issues

**Missing Dependencies:**
```yaml
- name: Install dependencies
  run: pip install dspy-code dspy
```

**API Key Not Set:**
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

**Validation Fails:**
Check your code with:
```bash
dspy-code /validate my_program.py
```

---

**For more details, see [Deployment](deployment.md)**
