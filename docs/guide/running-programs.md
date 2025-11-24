# Running DSPy Programs

Execute and test your DSPy programs safely with DSPy Code.

## Quick Run

### Run Generated Code

After generating code:

```
/run
```

Executes the last generated code in a sandboxed environment.

### Run Specific File

```
/run my_program.py
```

## Sandbox Execution

All code runs in a **secure sandbox**:

- ✅ Isolated environment
- ✅ Resource limits
- ✅ Timeout protection
- ✅ Safe execution

## Execution Output

```
Running my_program.py...

Output:
─────────────────────────────
Text: I love this!
Sentiment: positive
Confidence: 0.95
─────────────────────────────

✓ Execution completed (2.3s)
```

## Testing

Test with custom inputs:

```
/test my_module.py
```

Prompts for test inputs and shows results.

## Debugging

Run with debug output:

```
/run my_program.py --debug
```

Shows:
- Execution trace
- Variable values
- Error details

## Common Issues

### Timeout

```
Error: Execution timeout (30s)
```

**Solution:** Optimize code or increase timeout in config

### Import Error

```
Error: Module not found
```

**Solution:** Install required dependencies

### Runtime Error

```
Error: [error message]
```

**Solution:** Check error message, fix code, run `/validate` first

[Learn About Validation →](validation.md){ .md-button .md-button--primary }
