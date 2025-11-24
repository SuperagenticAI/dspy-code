# Troubleshooting

Common issues and solutions for DSPy Code.

## Installation Issues

### Command Not Found

```bash
dspy-code: command not found
```

**Solution:**
```bash
pip install --user dspy-code
# Add to PATH if needed
export PATH="$HOME/.local/bin:$PATH"
```

### Permission Denied

```
Permission denied during installation
```

**Solution:**
```bash
pip install --user dspy-code
# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install dspy-code
```

## Connection Issues

### Model Not Connected

```
Error: No model connected
```

**Solution:**
```
/connect ollama llama3.1:8b
```

### Ollama Connection Failed

```
Error: Could not connect to Ollama
```

**Solutions:**
1. Start Ollama: `ollama serve`
2. Check Ollama is running: `ollama list`
3. Pull model: `ollama pull llama3.1:8b`

### API Key Invalid

```
Error: Invalid API key
```

**Solution:**
```bash
# Set environment variable
export OPENAI_API_KEY=sk-your-key-here
# Restart DSPy Code
```

## Code Generation Issues

### No Code Generated

```
Error: Failed to generate code
```

**Solutions:**
1. Check model connection: `/status`
2. Reconnect: `/connect ollama llama3.1:8b`
3. Try simpler request
4. Check model is responding

### Code Has Errors

```
Validation failed: [errors]
```

**Solution:**
```
Ask: "Fix the errors in the last generated code"
```

## Optimization Issues

### Not Enough Examples

```
Error: Need at least 10 examples
```

**Solution:**
```
Generate 20 examples for [task]
```

### GEPA Fails

```
Error: Optimization failed
```

**Solutions:**
1. Check training data: `/data validate`
2. Ensure enough examples (50+ recommended)
3. Check model connection
4. Try with smaller dataset first

## Index Issues

### Index Build Failed

```
Warning: Could not build codebase index
```

**Solutions:**
1. Check Python packages are readable
2. Run `/refresh-index`
3. Check permissions
4. Continue anyway (optional feature)

### Index Stale

```
Warning: Index is stale
```

**Solution:**
```
/refresh-index
```

## Session Issues

### Session Not Found

```
Error: Session 'name' not found
```

**Solution:**
```
/sessions list  # See available sessions
```

### Cannot Save Session

```
Error: Failed to save session
```

**Solutions:**
1. Check disk space
2. Check write permissions
3. Try different name

## Performance Issues

### Slow Response

**Solutions:**
1. Use faster model (gpt-3.5-turbo vs gpt-4)
2. Use local model (Ollama)
3. Reduce example count
4. Check internet connection

### High Memory Usage

**Solutions:**
1. Reduce batch size in optimization
2. Use smaller model
3. Clear cache: `rm -rf .cache/`

## Common Error Messages

### "DSPy not found"

```
Error: DSPy not found. Please install dspy
```

**Solution:**
```bash
pip install dspy
```

### "No code to save"

```
Error: No code to save yet
```

**Solution:**
1. Generate code first
2. Check `/status` to see context

### "Validation failed"

See validation errors and fix:
```
/validate
# Read errors
# Fix issues
/validate again
```

## Getting Help

If you can't find a solution:

1. **Check FAQ**: [FAQ](faq.md)
2. **GitHub Issues**: [Report Issue](https://github.com/superagentic-ai/dspy-code/issues)
3. **Check Status**: `/status` to see current state
4. **Debug Mode**: Start with `dspy-code --debug`

## Debug Mode

For detailed error information:

```bash
dspy-code --debug
```

Shows:
- Full error traces
- API calls
- Internal state
- Detailed logs

[Back to FAQ →](faq.md){ .md-button }
