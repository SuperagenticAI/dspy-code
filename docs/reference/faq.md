# Frequently Asked Questions

Common questions about DSPy Code, answered!

## General Questions

### What is DSPy Code?

DSPy Code is an interactive development environment for DSPy. It helps you create, validate, and optimize DSPy programs through a simple command-line interface with natural language support.

### Do I need to know DSPy to use DSPy Code?

No! DSPy Code is perfect for beginners. You can:

- Generate code from plain English descriptions
- Ask questions about DSPy concepts
- Learn by example with built-in templates
- Get validation feedback to learn best practices

### Is DSPy Code free?

Yes! DSPy Code is open source and completely free to use.

### What DSPy versions are supported?

DSPy Code works with ANY DSPy version (2.x, 3.x, or newer). It adapts to your installed version automatically!

## Installation & Setup

### How do I install DSPy Code?

```bash
pip install dspy-code
```

See the [Installation Guide](../getting-started/installation.md) for details.

### Do I need to install DSPy separately?

Yes, DSPy Code requires DSPy to be installed:

```bash
pip install dspy
```

### Can I use DSPy Code without installing provider SDKs?

Yes! Provider SDKs (openai, anthropic, etc.) are optional. DSPy Code will tell you if you need one and how to install it.

### Why does indexing fail with permission errors?

This can happen if your Python packages are in restricted directories. Don't worry! DSPy Code still works. You just won't be able to ask questions about DSPy internals.

## Using DSPy Code

### How do I start DSPy Code?

Just run:

```bash
dspy-code
```

That's it! No complex commands needed.

### What are slash commands?

Slash commands are commands that start with `/`. For example:

- `/init` - Initialize project
- `/save` - Save code
- `/help` - Show help

See all commands in the [Slash Commands Reference](../guide/slash-commands.md).

### Can I use natural language?

Yes! Just describe what you want:

```
Create a sentiment analyzer
```

```
Build a question answering system
```

No need for `/create` or special syntax.

### How do I save generated code?

```
/save filename.py
```

The code will be saved to your `generated/` directory.

### How do I check if code was generated?

Use the `/status` command:

```
/status
```

This shows what's in your current session.

### Can I use DSPy Code offline?

Yes! DSPy Code works offline using templates. For better results, connect to a model:

```
/connect ollama llama3.1:8b
```

## Code Generation

### What can DSPy Code generate?

DSPy Code can generate:

- Signatures
- Modules
- Complete programs
- Optimization scripts
- Evaluation code
- Training data

### How accurate is the generated code?

The code follows DSPy best practices and is validated automatically. With a connected model, it's highly accurate. Without a model, it uses proven templates.

### Can I customize the generated code?

Yes! The generated code is yours to modify. DSPy Code gives you a starting point, and you can customize it however you like.

### Why is my code generation slow?

Code generation speed depends on:

- Your connected model (local vs cloud)
- Model size
- Complexity of your request

Ollama (local) is usually faster than cloud APIs.

### Can I generate code without connecting a model?

Yes! DSPy Code uses templates when no model is connected. The code will be more generic but still functional.

## Model Connection

### What models can I use?

DSPy Code supports:

- **Ollama** (local models)
- **OpenAI** (GPT-4, GPT-3.5, etc.)
- **Anthropic** (Claude models)
- **Google** (Gemini models)

### How do I connect to Ollama?

```
/connect ollama llama3.1:8b
```

Make sure Ollama is running:

```bash
ollama serve
```

### How do I use OpenAI?

Set your API key:

```bash
export OPENAI_API_KEY=sk-...
```

Then connect:

```
/connect openai gpt-4
```

### Can I switch models?

Yes! Disconnect and connect to a different model:

```
/disconnect
/connect anthropic claude-3-sonnet
```

### Do I need an API key for Ollama?

No! Ollama runs locally and doesn't need an API key.

## Validation & Testing

### What does /validate check?

The validator checks:

- Signature correctness
- Module structure
- Best practices
- Common mistakes
- Security issues

### Is validation required?

No, but it's highly recommended! Validation catches issues before you run your code.

### Can I validate existing code?

Yes!

```
/validate my_program.py
```

### What if validation fails?

Read the error messages. They tell you exactly what's wrong and how to fix it.

### Is code execution safe?

Yes! Code runs in a sandbox with:

- Timeout protection
- Limited permissions
- Error handling

## Optimization

### What is GEPA?

GEPA (Genetic Prompt Evolution Algorithm) is a DSPy optimizer that uses reflection to evolve better prompts automatically.

### Is GEPA optimization real or simulated?

**Real!** DSPy Code uses actual `dspy.teleprompt.GEPA` from your installed DSPy version. No mocking or simulation.

### Do I need training data for optimization?

Yes. You can:

- Generate it with DSPy Code
- Provide your own
- Use existing datasets

### How long does optimization take?

It depends on:

- Budget setting (light/medium/heavy)
- Number of training examples
- Model speed

Light budget: 5-10 minutes  
Medium budget: 20-30 minutes  
Heavy budget: 1-2 hours

### Can I optimize without GEPA?

GEPA is the recommended optimizer, but DSPy has other optimizers you can use manually.

## Troubleshooting

### CLI won't start

```bash
# Check installation
pip install dspy-code

# Try with python -m
python -m dspy_code
```

### No code generated

1. Check your description is clear
2. Try connecting a model
3. Use `/examples` for templates

### Can't save code

1. Check if code exists: `/status`
2. Specify filename: `/save file.py`
3. Check directory permissions

### Validation errors

Read the error messages carefully. They tell you exactly what to fix.

### Model connection fails

**Ollama:**

```bash
# Make sure it's running
ollama serve

# Check if model is pulled
ollama list
ollama pull llama3.1:8b
```

**OpenAI/Anthropic:**

```bash
# Check API key is set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY
```

### Indexing takes too long

This is normal! Indexing scans your installed packages. It only happens during `/init` and is cached.

### Permission denied during indexing

This is okay! DSPy Code will skip what it can't access and still work normally.

## Advanced Questions

### Can I use DSPy Code in CI/CD?

Yes! DSPy Code works in automated environments. See the [CI/CD Guide](../advanced/cicd.md).

### Can I use DSPy Code in Docker?

Yes! See the [Deployment Guide](../advanced/deployment.md) for Docker examples.

### Can I integrate MCP servers?

Yes! DSPy Code has full MCP support. See the [MCP Integration Guide](../advanced/mcp-integration.md).

### Can I customize the configuration?

Yes! Edit `dspy_config.yaml` to customize:

- Output directories
- Model settings
- Indexing options
- And more

See the [Configuration Reference](configuration.md).

### Can I contribute to DSPy Code?

Yes! Contributions are welcome. See the [Contributing Guide](../about/contributing.md) for technical guidelines.

## Getting Help

### Where can I get help?

- Check this FAQ
- Read the [Troubleshooting Guide](troubleshooting.md)
- Report issues on [GitHub Issues](https://github.com/superagentic-ai/dspy-code/issues)

### How do I report a bug?

Open an issue on [GitHub](https://github.com/superagentic-ai/dspy-code/issues) with:

- DSPy Code version
- DSPy version
- What you tried
- What happened
- Error messages

### How do I request a feature?

Open a feature request on [GitHub](https://github.com/superagentic-ai/dspy-code/issues) describing:

- What you want to do
- Why it would be useful
- Example use cases

## Still Have Questions?

Can't find your answer? Try:

- [Troubleshooting Guide](troubleshooting.md)
- [Command Reference](commands.md)
- [GitHub Issues](https://github.com/superagentic-ai/dspy-code/issues)

---

**Didn't find your answer?** [Open an issue](https://github.com/superagentic-ai/dspy-code/issues) for technical support.
