---
hide:
  - navigation
  - toc
---

<div class="hero-section">
  <div class="hero-background">
    <div class="hero-particles"></div>
    <div class="hero-gradient-orb orb-1"></div>
    <div class="hero-gradient-orb orb-2"></div>
    <div class="hero-gradient-orb orb-3"></div>
  </div>
  <div class="hero-content">
    <div class="hero-top">
      <h1 class="hero-title gradient-text-purple-pink-orange">
        Welcome to DSPy Code
      </h1>

      <div class="hero-logo">
        <img src="resource/dspy-code.png" alt="DSPy Code Logo" class="animated-logo">
      </div>

      <h2 class="hero-subtitle gradient-text-purple-pink-orange">
        Comprehensive CLI to Optimize Your DSPy Code
      </h2>
    </div>

    <div class="hero-middle">
      <p class="hero-description">
        Your AI-Powered DSPy Development Assistant: Claude Code for DSPy
      </p>

      <div class="hero-features">
        <div class="feature-item">
          <span class="feature-icon">✨</span>
          <span class="feature-text">Natural Language</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🔗</span>
          <span class="feature-text">MCP Client</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🧬</span>
          <span class="feature-text">GEPA Optimization</span>
        </div>
        <div class="feature-item">
          <span class="feature-icon">🧠</span>
          <span class="feature-text">Codebase RAG</span>
        </div>
      </div>
    </div>

    <div class="hero-bottom">
      <div class="hero-tags">
        <span class="tag tag-animated">Learn</span>
        <span class="tag tag-animated">Build</span>
        <span class="tag tag-animated">Optimize</span>
        <span class="tag tag-animated">Connect</span>
      </div>

      <div class="hero-cta">
        <a href="getting-started/installation/" class="cta-button primary">🚀 Get Started</a>
        <a href="getting-started/quick-start/" class="cta-button secondary">⚡ Quick Start</a>
      </div>
    </div>
  </div>
</div>

---

## 🎯 What is DSPy Code?

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2em; border-radius: 10px; color: white; margin: 2em 0;">
  <h3 style="color: white; margin-top: 0;">Comprehensive CLI to Optimize Your DSPy Code - The Living Playbook</h3>
  <p style="font-size: 1.1em; line-height: 1.8;">
    DSPy Code is an <strong>interactive development environment</strong> that transforms how you learn and build with DSPy.
    No need to read docs, books, or tutorials. Just enter the CLI, start building, ask questions, and get answers from your actual code in natural language.
  </p>
  <p style="font-size: 1.1em; line-height: 1.8; margin-bottom: 0;">
    <strong>Learn as you build.</strong> Whether you're a complete beginner or a DSPy expert, the CLI adapts to your level and guides you through every step.
  </p>
</div>

---

## 💡 Who is This For?

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle style="color: #7c3aed;" } **Complete Beginners**

    Never used DSPy before? Perfect! Start here and learn by doing. The CLI teaches you DSPy concepts as you build real programs.

    **No prerequisites needed.**

-   :material-code-braces:{ .lg .middle style="color: #4f46e5;" } **DSPy Developers**

    Already know DSPy? Supercharge your workflow with AI-powered code generation, validation, and optimization.

    **Build faster, optimize smarter.**

-   :material-rocket-launch:{ .lg .middle style="color: #6366f1;" } **Production Teams**

    Building production DSPy applications? Get validated, optimized, production-ready code with GEPA optimization and best practices built-in.

    **Ship with confidence.**

</div>

---

## 🚀 Use Cases: When to Use DSPy Code

### 1. Starting a New DSPy Project

**Perfect for:**

- Building a new AI application from scratch
- Prototyping ideas quickly
- Learning DSPy fundamentals

**What you get:**

```bash
dspy-code
/init --fresh
```

✅ Complete project structure  
✅ Configuration files  
✅ Example programs  
✅ Best practices setup  
✅ Ready to code in 2 minutes

**Example:** "I want to build a customer support chatbot with sentiment analysis and automated responses."

[Start Your First Project →](getting-started/quick-start.md){ .md-button .md-button--primary }

---

### 2. Adding DSPy to Existing Projects

**Perfect for:**

- Enhancing existing Python applications
- Adding AI capabilities to current systems
- Modernizing legacy code

**What you get:**

```bash
cd my-existing-project
dspy-code
/init
```

✅ Minimal setup (no disruption)  
✅ Scans your existing code  
✅ Understands your project structure  
✅ Generates code that fits your style  
✅ Works alongside your current code

**Example:** "I have a Django app. I want to add AI-powered document summarization."

[Add to Existing Project →](guide/project-management.md){ .md-button }

---

### 3. Learning DSPy (No Docs Required!)

**Perfect for:**

- First time using DSPy
- Understanding DSPy concepts
- Exploring different patterns

**How it works:**

Just ask questions in natural language:

```
→ What is a DSPy Signature?
→ How does ChainOfThought work?
→ Show me an example of ReAct
→ When should I use GEPA optimization?
```

The CLI answers using **YOUR installed DSPy version** and provides working code examples!

**No reading required. Learn by building.**

[Start Learning →](getting-started/understanding.md){ .md-button }

---

### 4. Connecting to MCP Servers for Powerful DSPy Programs

**DSPy Code is an MCP Client!**

Connect to any MCP (Model Context Protocol) server to supercharge your DSPy programs with external tools, APIs, and data sources.

**What you can do:**

```bash
# Add MCP server
/mcp-add web-tools --transport stdio --command "python server.py"

# Connect to server
/mcp-connect web-tools

# Use tools in your DSPy programs
→ Create a DSPy module that searches the web and summarizes results
```

✅ **Access external tools** - Web search, databases, APIs  
✅ **Read from data sources** - Files, documents, databases  
✅ **Execute commands** - System operations, scripts  
✅ **Integrate services** - Third-party APIs and tools  
✅ **Build powerful workflows** - Combine DSPy with external capabilities

**Example:** "Build a RAG system that uses MCP to query my company's database and generate answers."

[Learn MCP Integration →](advanced/mcp-integration.md){ .md-button }

---

### 5. Optimizing DSPy Programs with GEPA

**Perfect for:**

- Improving accuracy of existing programs
- Automatic prompt engineering
- Production optimization

**What you get:**

```bash
# Generate training data
→ Generate 100 examples for sentiment analysis

# Optimize automatically
/optimize my_program.py training_data.jsonl
```

✅ AI-generated training data  
✅ Automatic GEPA optimization  
✅ 10-30% accuracy improvements  
✅ Production-ready optimized code

**Real results:** 75% → 92% accuracy automatically!

[Learn GEPA Optimization →](guide/optimization.md){ .md-button }

---

### 6. Building Production AI Applications

**Perfect for:**

- Enterprise applications
- Production deployments
- Mission-critical systems

**What you get:**

✅ Validated, production-ready code  
✅ Best practices built-in  
✅ Error handling and logging  
✅ Type hints and documentation  
✅ Optimized performance  
✅ Export as packages

**Quality score:** 90+ out of 100 automatically!

[Production Best Practices →](guide/validation.md){ .md-button }

---

## ✨ Key Features

<div class="grid cards" markdown>

-   :material-chat-processing:{ .lg .middle style="color: #7c3aed;" } **Natural Language Interface**

    Describe what you want in plain English. The CLI generates complete, working DSPy code.

    ```
    "Build a RAG system for document Q&A"
    ```

    Done! Complete code generated.

-   :material-server-network:{ .lg .middle style="color: #4f46e5;" } **Built-in MCP Client**

    Connect to any MCP server to access external tools, APIs, databases, and services in your DSPy programs.

    **Build powerful, connected AI applications.**

-   :material-brain:{ .lg .middle style="color: #6366f1;" } **Version-Aware Intelligence**

    Adapts to YOUR installed DSPy version. Answers questions using your actual code, not outdated docs.

    **Always current. Always accurate.**

-   :material-rocket-launch-outline:{ .lg .middle style="color: #8b5cf6;" } **Real GEPA Optimization**

    Not mocked. Real genetic prompt evolution that improves your programs by 10-30% automatically.

    **Production-grade results.**

-   :material-code-tags-check:{ .lg .middle style="color: #a855f7;" } **Smart Validation**

    Every generated code is validated for quality, best practices, and correctness. Score: 90+/100.

    **Ship with confidence.**

-   :material-database-search:{ .lg .middle style="color: #c084fc;" } **Codebase Knowledge**

    Indexes your DSPy installation and project. Ask questions about your own code!

    **"Explain my RAG module"** - Done!

-   :material-connection:{ .lg .middle style="color: #ec4899;" } **Universal Model Support**

    Connect to any LLM: Ollama (local), OpenAI, Anthropic, Gemini. Switch anytime.

    **Your choice, your control.**

-   :material-auto-fix:{ .lg .middle style="color: #f43f5e;" } **Learn as You Build**

    No docs, books, or tutorials needed. Ask questions, get answers from your code, build in real-time.

    **Interactive learning experience.**

</div>

---

## 🎬 See It In Action

### Quick Example

```bash
# Start DSPy Code
dspy-code

# Initialize project
→ /init --fresh

# Connect to model
→ /connect ollama llama3.1:8b

# Generate code in natural language
→ Create a sentiment analyzer with confidence scores

# Validate
→ /validate

# Save
→ /save sentiment_analyzer.py

# Generate training data
→ Generate 50 examples for sentiment analysis

# Optimize with GEPA
→ /optimize sentiment_analyzer.py training_data.jsonl
```

**Result:** Production-ready, optimized sentiment analyzer in 5 minutes!

---

## 🏃 Quick Start

<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5em; margin: 2em 0;">

<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5em; border-radius: 10px; color: white;">
  <h3 style="color: white; margin-top: 0;">1. Install</h3>
  <pre style="background: rgba(0,0,0,0.2); padding: 1em; border-radius: 5px; margin: 0;"><code>pip install dspy-code</code></pre>
</div>

<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 1.5em; border-radius: 10px; color: white;">
  <h3 style="color: white; margin-top: 0;">2. Start</h3>
  <pre style="background: rgba(0,0,0,0.2); padding: 1em; border-radius: 5px; margin: 0;"><code>dspy-code</code></pre>
</div>

<div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 1.5em; border-radius: 10px; color: white;">
  <h3 style="color: white; margin-top: 0;">3. Build</h3>
  <pre style="background: rgba(0,0,0,0.2); padding: 1em; border-radius: 5px; margin: 0;"><code>/init
/connect ollama llama3.1:8b
Create a [your app]</code></pre>
</div>

</div>

[Complete Quick Start Guide →](getting-started/quick-start.md){ .md-button .md-button--primary style="background: linear-gradient(90deg, #667eea, #764ba2); border: none; font-size: 1.1em; padding: 0.8em 2em;" }

---

## 💬 Real Workflows

### Workflow 1: Complete Beginner

```
Day 1:
→ Install DSPy Code
→ /init --fresh
→ "What is DSPy?"
→ "Create a simple text classifier"
→ /save my_first_program.py
→ /run

Result: Working DSPy program, understanding of basics
```

### Workflow 2: Building Production App

```
Week 1:
→ dspy-code /init in existing project
→ Generate signatures, modules, programs
→ Generate 200 training examples
→ Optimize with GEPA
→ Validate (95/100 quality score)
→ Export as package
→ Deploy

Result: Production-ready AI application
```

### Workflow 3: Learning Advanced Patterns

```
→ "Show me how ReAct works"
→ "Create a multi-agent system"
→ "Explain GEPA optimization"
→ "Build a RAG system with custom retrieval"

Result: Deep understanding through hands-on building
```

---

## 🎯 Common Questions

!!! question "Do I need to know DSPy first?"
    **No!** That's the whole point. DSPy Code teaches you as you build. Just start creating and ask questions when you need help.

!!! question "Can I use this with my existing DSPy code?"
    **Yes!** Run `/init` in your project directory. DSPy Code will scan your code and help you extend it.

!!! question "What models can I use?"
    **Any!** Ollama (local), OpenAI, Anthropic, Gemini. Connect with one command: `/connect ollama llama3.1:8b`

!!! question "Is the optimization real or mocked?"
    **Real GEPA optimization!** Actual genetic prompt evolution that improves accuracy by 10-30%.

!!! question "Do I need to read documentation?"
    **No!** Just ask DSPy Code. It answers questions using your actual installed DSPy version.

---

## 🚀 Ready to Start?

<div style="text-align: center; margin: 3em 0; padding: 3em; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px;">
  <h2 style="color: white; font-size: 2em; margin-top: 0;">Start Building in 2 Minutes</h2>
  <p style="color: white; font-size: 1.2em; margin: 1.5em 0;">No docs to read. No tutorials to follow. Just start building.</p>

  <div style="margin: 2em 0;">
    <a href="getting-started/installation.md" style="display: inline-block; background: white; color: #667eea; padding: 1em 3em; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2em; margin: 0.5em;">
      Install Now
    </a>
    <a href="getting-started/quick-start.md" style="display: inline-block; background: rgba(255,255,255,0.2); color: white; padding: 1em 3em; border-radius: 50px; text-decoration: none; font-weight: bold; font-size: 1.2em; margin: 0.5em; border: 2px solid white;">
      Quick Start
    </a>
  </div>
</div>

---

## 📚 Documentation Structure

<div class="grid cards" markdown>

-   **Getting Started**

    Installation, quick start, first program, understanding the architecture

-   **User Guide**

    Interactive mode, code generation, validation, optimization, project management

-   **Tutorials**

    Step-by-step guides for building real applications

-   **Reference**

    Commands, configuration, FAQ, troubleshooting

-   **Advanced**

    MCP integration, custom modules, deployment

</div>

---

## 🤝 Technical Support

Need help? Check these resources:

- **[FAQ](reference/faq.md)** - Common questions answered
- **[Troubleshooting](reference/troubleshooting.md)** - Fix common issues
- **[GitHub Issues](https://github.com/superagentic-ai/dspy-code/issues)** - Report bugs or request features

---

<div style="text-align: center; margin: 3em 0; padding: 2em; background: rgba(124, 58, 237, 0.05); border-radius: 10px;">
  <p style="font-size: 1.1em; color: #6b7280; margin: 0;">
    <strong style="color: #7c3aed;">DSPy Code</strong> by
    <a href="https://super-agentic.ai" style="color: #4f46e5; text-decoration: none; font-weight: bold;">Superagentic AI</a>
  </p>
  <p style="color: #9ca3af; margin-top: 0.5em;">
    Comprehensive CLI to Optimize Your DSPy Code - Learn by building. No docs required.
  </p>
</div>
