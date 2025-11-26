# Natural Language Commands

DSPy Code supports **natural language for all commands**! You don't need to remember slash commands - just describe what you want to do.

## 🎯 How It Works

Instead of remembering exact slash commands, you can either:

- Use the **interactive selector**: `/model`
- Or just describe what you want in natural language.

For example, instead of typing `/connect ollama gpt-oss:120b`, you can say:

```
connect to ollama gpt-oss:120b
```

DSPy Code automatically understands your intent and routes it to the appropriate command (for example, `/model` or `/connect`).

---

## 📋 Supported Natural Language Commands

### Connection Commands

**Instead of:** `/model` (interactive selector)  
**You can say:**
- "help me pick a model"
- "connect a model for me"
- "set up a model"
- "select a model to use"

**Instead of:** `/connect ollama gpt-oss:120b`  
**You can say:**
- "connect to ollama gpt-oss:120b"
- "use model ollama gpt-oss:120b"
- "switch to ollama gpt-oss:120b"
- "set up model ollama gpt-oss:120b"
- "configure model ollama gpt-oss:120b"

**Instead of:** `/disconnect`  
**You can say:**
- "disconnect from model"
- "stop using model"
- "close connection"

**Instead of:** `/models`  
**You can say:**
- "list available models"
- "show me all models"
- "what models are available"

**Instead of:** `/status`  
**You can say:**
- "status"
- "what is the current status"
- "show me the status"
- "where am I"

---

### File Operations

**Instead of:** `/save my_program.py`  
**You can say:**
- "save the code as my_program.py"
- "save this as my_program.py"
- "write to file my_program.py"
- "store the code as my_program.py"

**Instead of:** `/save-data training.jsonl`  
**You can say:**
- "save the data as training.jsonl"
- "save my examples as training.jsonl"
- "export data to training.jsonl"

---

### Validation and Execution

**Instead of:** `/validate`  
**You can say:**
- "validate the code"
- "check the code for errors"
- "verify the program"
- "test the code syntax"
- "is the code valid"

**Instead of:** `/run`  
**You can say:**
- "run the code"
- "execute the program"
- "test the execution"
- "start the program"

**Instead of:** `/test`  
**You can say:**
- "test the code"
- "run tests"
- "execute tests"

---

### Project Management

**Instead of:** `/init`  
**You can say:**
- "initialize the project"
- "setup project"
- "create new project"
- "start new project"
- "new project"

**Instead of:** `/project`  
**You can say:**
- "project info"
- "show me the project"
- "what is the project"

---

### Optimization

**Instead of:** `/optimize my_program.py`  
**You can say:**
- "optimize the code"
- "optimize my program"
- "optimize my_program.py"
- "improve the program"
- "improve performance"
- "use gepa"
- "run gepa"
- "run optimization"
- "run GEPA optimization"
- "make it better"
- "enhance the code"
- "optimize with GEPA"
- "optimize my_module.py with training_data.jsonl"

**Instead of:** `/optimize my_program.py training_data.jsonl`  
**You can say:**
- "optimize my_program.py with training_data.jsonl"
- "run GEPA on my_program.py using training_data.jsonl"
- "optimize the program with training data"
- "improve my code with examples from training_data.jsonl"

**Instead of:** `/optimize-status`  
**You can say:**
- "gepa status"
- "optimization status"
- "how is optimization going"
- "check optimization progress"
- "what's the optimization status"

**Instead of:** `/optimize-cancel`  
**You can say:**
- "cancel optimization"
- "stop gepa"
- "abort optimization"
- "stop the optimization"

---

### Evaluation

**Instead of:** `/eval`  
**You can say:**
- "evaluate the code"
- "evaluate my program"
- "evaluate the program"
- "run evaluation"
- "test performance"
- "test the code"
- "measure performance"
- "assess performance"
- "check performance"

**Instead of:** `/eval my_program.py`  
**You can say:**
- "evaluate my_program.py"
- "test performance of my_program.py"
- "run evaluation on my_program.py"
- "evaluate the program in my_program.py"

**Instead of:** `/eval my_program.py test_data.jsonl`  
**You can say:**
- "evaluate my_program.py with test_data.jsonl"
- "test my program using test_data.jsonl"
- "run evaluation on my_program.py with test_data.jsonl"
- "measure performance with test_data.jsonl"

**Instead of:** `/eval metric=accuracy`  
**You can say:**
- "evaluate with accuracy"
- "test accuracy"
- "measure accuracy"
- "calculate accuracy"
- "check accuracy"
- "evaluate using accuracy metric"
- "test performance with accuracy"

**Instead of:** `/eval my_program.py test_data.jsonl metric=f1`  
**You can say:**
- "evaluate my_program.py with test_data.jsonl using F1 score"
- "test F1 score of my program with test data"
- "measure F1 metric on my_program.py with test_data.jsonl"
- "calculate F1 score for my program"

---

### Data Generation

**Instead of:** `/data sentiment 20`  
**You can say:**
- "generate 20 examples for sentiment analysis"
- "create training data for sentiment"
- "make 20 examples for sentiment"
- "produce data for sentiment analysis"

---

### Explanation and Help

**Instead of:** `/explain ChainOfThought`  
**You can say:**
- "explain ChainOfThought"
- "what is ChainOfThought"
- "how does ChainOfThought work"
- "tell me about ChainOfThought"
- "describe ChainOfThought"

**Instead of:** `/help`  
**You can say:**
- "help"
- "what can you do"
- "show me help"
- "list commands"
- "what commands are available"

**Instead of:** `/intro`  
**You can say:**
- "introduction"
- "guide"
- "tutorial"
- "getting started"
- "how do I start"

---

### History and Context

**Instead of:** `/history`  
**You can say:**
- "history"
- "show me the conversation history"
- "what did we talk about"
- "previous messages"

**Instead of:** `/clear`  
**You can say:**
- "clear context"
- "reset history"
- "forget everything"
- "start over"
- "new conversation"

---

### Sessions

**Instead of:** `/sessions`  
**You can say:**
- "list sessions"
- "show me all sessions"
- "what sessions do I have"

**Instead of:** `/session save my-session`  
**You can say:**
- "save session as my-session"
- "save conversation as my-session"

**Instead of:** `/session load my-session`  
**You can say:**
- "load session my-session"
- "restore session my-session"
- "open session my-session"

---

### Export/Import

**Instead of:** `/export package.zip`  
**You can say:**
- "export package to package.zip"
- "package the project"
- "create package"

**Instead of:** `/import package.zip`  
**You can say:**
- "import package from package.zip"
- "load package package.zip"
- "open package package.zip"

---

### RAG and Indexing

**Instead of:** `/refresh-index`  
**You can say:**
- "refresh index"
- "rebuild knowledge base"
- "update index"
- "reindex"

**Instead of:** `/index-status`  
**You can say:**
- "index status"
- "knowledge base status"
- "codebase index"

---

### Feature Listings

**Instead of:** `/predictors`  
**You can say:**
- "list predictors"
- "show me predictor types"
- "what predictors are available"

**Instead of:** `/adapters`  
**You can say:**
- "list adapters"
- "show me adapter types"
- "what adapters"

**Instead of:** `/retrievers`  
**You can say:**
- "list retrievers"
- "show me retriever types"
- "what retrievers"

**Instead of:** `/examples rag`  
**You can say:**
- "show me examples"
- "list templates"
- "what examples are available"

---

### MCP Commands

**Instead of:** `/mcp-connect filesystem`  
**You can say:**
- "connect to mcp server filesystem"
- "link to mcp filesystem"
- "use mcp server filesystem"

**Instead of:** `/mcp-tools`  
**You can say:**
- "list mcp tools"
- "show me mcp tools"
- "what mcp tools are available"

**Instead of:** `/mcp-call filesystem read_file`  
**You can say:**
- "call mcp tool filesystem read_file"
- "use mcp tool read_file"
- "invoke mcp tool read_file"

---

## 💡 Tips

1. **Be natural** - Just describe what you want to do
2. **Include details** - Mention filenames, model names, etc.
3. **Mix and match** - You can still use slash commands if you prefer
4. **Both work** - Natural language and slash commands work together

---

## 🎯 Examples

### Complete Workflow in Natural Language

```
You: initialize the project
DSPy Code: ✓ Project initialized

You: connect to ollama llama3.1:8b
DSPy Code: ✓ Connected to ollama llama3.1:8b

You: create a sentiment analyzer
DSPy Code: [Generates code...]

You: save the code as sentiment.py
DSPy Code: ✓ Saved to sentiment.py

You: validate the code
DSPy Code: ✓ Code is valid

You: run the code
DSPy Code: [Executes code...]

You: generate 20 examples for sentiment analysis
DSPy Code: [Generates training data...]

You: optimize the code
DSPy Code: [Runs GEPA optimization...]

You: evaluate my program with accuracy
DSPy Code: [Runs evaluation with accuracy metric...]

You: test performance of sentiment.py with test_data.jsonl
DSPy Code: [Evaluates program with test data...]
```

---

## 🔄 How It Works Internally

DSPy Code uses a **hybrid intelligent routing system**:

### Step 1: Fast Pattern Matching (First Attempt)
- Matches your natural language against known patterns
- Fast and deterministic
- Handles common cases instantly

### Step 2: LLM Reasoning (Intelligent Fallback)
- If pattern matching fails, uses your connected LLM (Ollama, OpenAI, etc.)
- Understands context, variations, and intent
- Handles edge cases and natural language variations
- Uses conversation history and current state

### Step 3: Argument Extraction
- Automatically extracts parameters (filenames, model names, etc.)
- Works with both pattern matching and LLM reasoning

### Step 4: Command Execution
- Routes to the appropriate slash command handler
- Executes the command with extracted arguments

### Example Flow

```
User: "I want to use the llama model that's running locally"
  ↓
Pattern Matching: ✗ No match
  ↓
LLM Reasoning: "User wants to connect to Ollama model"
  ↓
Extract: provider="ollama", model="llama3.1:8b" (from context)
  ↓
Route to: /connect ollama llama3.1:8b
  ↓
Execute command
```

### Benefits

- **Fast** - Common commands are instant (pattern matching)
- **Intelligent** - Handles any natural language variation (LLM reasoning)
- **Context-Aware** - Understands conversation history and current state
- **Flexible** - Works even with unusual phrasings

---

**You can use natural language for everything, or mix it with slash commands - whatever feels more natural to you!** 🚀
