# Architecture Overview

This document provides a high-level overview of the DSPy Code architecture, showing how the major components interact.

## System Architecture

```mermaid
graph TB
    subgraph CLI["CLI Layer"]
        Main[main.py]
        Commands[commands/]
    end

    subgraph Core["Core Infrastructure"]
        Config[config.py]
        DebugLogger[debug_logger.py]
        Exceptions[exceptions.py]
        Logging[logging.py]
    end

    subgraph Models["Model Layer"]
        ModelManager[model_manager.py]
        LLMConnector[llm_connector.py]
        CodeGenerator[code_generator.py]
        Cache[cache.py]
        Streaming[streaming.py]
    end

    subgraph MCP["MCP Integration"]
        ClientManager[client_manager.py]
        SessionWrapper[session_wrapper.py]
        Retry[retry.py]
        Transports[transports/]
    end

    subgraph Validation["Validation Layer"]
        Validator[validator.py]
        SignatureValidator[signature_validator.py]
        ModuleValidator[module_validator.py]
        SecurityValidator[security_validator.py]
        QualityScorer[quality_scorer.py]
        AutoFixer[auto_fixer.py]
    end

    subgraph Execution["Execution Layer"]
        Engine[engine.py]
        Sandbox[sandbox.py]
    end

    subgraph RAG["RAG System"]
        CodebaseRAG[codebase_rag.py]
        Indexer[indexer.py]
        Search[search.py]
    end

    subgraph Project["Project Management"]
        Scanner[scanner.py]
        Initializer[initializer.py]
        ContextManager[context_manager.py]
    end

    Main --> Commands
    Commands --> Core
    Commands --> Models
    Commands --> MCP
    Commands --> Validation
    Commands --> Execution
    Commands --> RAG
    Commands --> Project

    Models --> Core
    Models --> Cache
    Models --> Streaming
    ModelManager --> LLMConnector
    ModelManager --> CodeGenerator

    MCP --> Core
    ClientManager --> SessionWrapper
    ClientManager --> Retry
    ClientManager --> Transports

    Validation --> Core
    Validator --> SignatureValidator
    Validator --> ModuleValidator
    Validator --> SecurityValidator
    Validator --> QualityScorer
    Validator --> AutoFixer

    Execution --> Core
    Engine --> Sandbox

    RAG --> Core
    CodebaseRAG --> Indexer
    CodebaseRAG --> Search
```

## Component Descriptions

### CLI Layer
- **main.py**: Application entry point, CLI argument parsing
- **commands/**: Individual command implementations (create, run, optimize, etc.)

### Core Infrastructure
- **config.py**: Configuration management with dataclasses for type safety
- **debug_logger.py**: Debug logging with timing and detailed output
- **exceptions.py**: Custom exception hierarchy
- **logging.py**: Structured logging configuration

### Model Layer
- **model_manager.py**: Manages LLM connections and model selection
- **llm_connector.py**: DSPy LLM integration
- **code_generator.py**: AI-powered code generation
- **cache.py**: LRU cache with TTL for code generation results
- **streaming.py**: Token streaming support with cancellation

### MCP Integration
- **client_manager.py**: MCP client lifecycle management
- **session_wrapper.py**: Session state and operations
- **retry.py**: Exponential backoff retry logic
- **transports/**: stdio, SSE, and WebSocket transport implementations

### Validation Layer
- **validator.py**: Main validation orchestrator
- **signature_validator.py**: DSPy signature validation
- **module_validator.py**: DSPy module structure validation
- **security_validator.py**: Security pattern detection (eval, exec, etc.)
- **quality_scorer.py**: Code quality scoring
- **auto_fixer.py**: Automatic code fixes for common issues

### Execution Layer
- **engine.py**: Code execution with async subprocess support
- **sandbox.py**: Sandboxed execution environment

### RAG System
- **codebase_rag.py**: Retrieval-augmented generation for codebase
- **indexer.py**: Lazy-loaded code indexing
- **search.py**: Semantic code search

### Project Management
- **scanner.py**: Project structure scanning
- **initializer.py**: Project initialization
- **context_manager.py**: Project context handling

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant CodeGen as Code Generator
    participant Cache
    participant LLM
    participant Validator
    participant Executor

    User->>CLI: dspy-code create
    CLI->>CodeGen: generate_code(prompt)
    CodeGen->>Cache: check_cache(key)
    alt Cache Hit
        Cache-->>CodeGen: cached_result
    else Cache Miss
        CodeGen->>LLM: generate(prompt)
        LLM-->>CodeGen: generated_code
        CodeGen->>Cache: store(key, code)
    end
    CodeGen->>Validator: validate(code)
    Validator-->>CodeGen: validation_result
    CodeGen-->>CLI: code + validation
    CLI->>Executor: run(code)
    Executor-->>CLI: execution_result
    CLI-->>User: output
```

## MCP Connection Flow

```mermaid
sequenceDiagram
    participant App
    participant ClientManager
    participant Retry as RetryController
    participant Transport
    participant Server as MCP Server

    App->>ClientManager: connect()
    ClientManager->>Retry: with_retry()
    loop Until Success or Max Retries
        Retry->>Transport: create_connection()
        Transport->>Server: handshake
        alt Success
            Server-->>Transport: connected
            Transport-->>Retry: session
        else Failure
            Server-->>Transport: error
            Transport-->>Retry: exception
            Retry->>Retry: exponential_backoff()
        end
    end
    Retry-->>ClientManager: session
    ClientManager-->>App: connected
```

## Configuration Hierarchy

```mermaid
graph TD
    ProjectConfig[ProjectConfig]
    ModelConfig[ModelConfig]
    MCPConfig[MCPConfig]
    RetryConfig[RetryConfig]
    CacheConfig[CacheConfig]
    QualityScoringConfig[QualityScoringConfig]

    ProjectConfig --> ModelConfig
    ProjectConfig --> MCPConfig
    ProjectConfig --> RetryConfig
    ProjectConfig --> CacheConfig
    ProjectConfig --> QualityScoringConfig
```

## Key Design Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Components receive dependencies through constructors
3. **Configuration-Driven**: Behavior controlled through typed configuration classes
4. **Graceful Degradation**: Fallbacks for streaming, caching, and MCP connections
5. **Security by Default**: Security validation integrated into the validation pipeline
6. **Observable**: Debug logging throughout for troubleshooting
