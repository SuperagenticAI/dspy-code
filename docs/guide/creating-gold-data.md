# Creating Gold Example Data

Complete guide to creating high-quality training data for DSPy optimization using DSPy Code.

## What is Gold Example Data?

**Gold example data** (also called training data) consists of input-output pairs that represent the correct behavior of your DSPy program.

**Example for sentiment analysis:**

```json
{
  "text": "I love this product!",
  "sentiment": "positive"
}
```

**Why it's called "gold":**

- Represents the "gold standard" of correct outputs
- Used to train and optimize your DSPy programs
- Quality of gold data directly impacts optimization results

## Data Requirements for GEPA

GEPA (Genetic Prompt Evolution Algorithm) requires:

**Minimum:**
- 10-20 examples for simple tasks
- 50-100 examples for complex tasks

**Recommended:**
- 50-200 examples for production use
- Diverse examples covering edge cases
- Balanced across categories (for classification)

**Format:**
- JSON or JSONL (JSON Lines)
- Consistent field names
- All examples have same input fields
- Clear, unambiguous outputs

## Methods to Create Gold Data

DSPy Code provides three methods:

1. **AI-Generated** - Let AI create synthetic examples
2. **Interactive** - Manually enter examples
3. **Import** - Load from existing files

### Method 1: AI-Generated Data (Recommended)

Use the LLM to generate diverse, high-quality examples:

```
Generate 50 examples for sentiment analysis
```

**What happens:**

1. DSPy Code analyzes your task
2. Generates diverse input examples
3. Creates correct outputs
4. Ensures variety and coverage

**Output:**

```
🎲 Generating 50 diverse examples for sentiment analysis...

✓ Generated 50 examples!

Sample Examples:
╭────────────────────────────────────────────────────────────────────────────╮
│ Input: "The movie was absolutely fantastic, a real masterpiece!"           │
│ Output: "positive"                                                         │
├────────────────────────────────────────────────────────────────────────────┤
│ Input: "I'm not sure how I feel about this, it's neither good nor bad."    │
│ Output: "neutral"                                                          │
├────────────────────────────────────────────────────────────────────────────┤
│ Input: "What a terrible experience, I regret every moment."                │
│ Output: "negative"                                                         │
╰────────────────────────────────────────────────────────────────────────────╯

Distribution:
  positive: 17 examples (34%)
  negative: 16 examples (32%)
  neutral: 17 examples (34%)

Next Steps:
• Type /save-data <filename> to save as JSONL
• Ask me to generate more examples
• Use these for GEPA optimization
• Request different types of examples
```

**Advanced generation:**

```
Generate 100 examples for email classification with diverse subjects, senders, and content types
```

```
Generate 50 examples for question answering about Python programming
```

```
Generate 30 examples for text summarization with varying document lengths
```

### Method 2: Interactive Data Collection

Manually enter examples through guided prompts:

```
/data collect
```

**Interactive flow:**

```
📊 Training Data Collection

Let's collect training examples for optimization.
You'll need at least 10 examples.

Example 1:
  Enter inputs (or 'done' to finish):
    Field name [done]: text
    text value: I love this product!
    Add another input field? [y/N]: n
  Expected output: positive
✓ Example 1 added

Example 2:
  Enter inputs (or 'done' to finish):
    Field name [done]: text
    text value: This is terrible
    Add another input field? [y/N]: n
  Expected output: negative
✓ Example 2 added

...

Add more examples? (have 10) [Y/n]: n

✓ Collected 10 examples

Training Data Summary:
Total examples: 10
Input fields: text

Sample Examples:
┌──────────────────────────┬──────────┐
│ text                     │ Output   │
├──────────────────────────┼──────────┤
│ I love this product!     │ positive │
│ This is terrible         │ negative │
│ It's okay                │ neutral  │
└──────────────────────────┴──────────┘

Save to file? [Y/n]: y
Filename [training_data.jsonl]: sentiment_train.jsonl
✓ Saved to data/sentiment_train.jsonl
```

### Method 3: Import from Files

Load existing data from JSON or JSONL files:

```
/data load examples.jsonl
```

**Supported formats:**

**JSONL (JSON Lines) - Recommended:**

```jsonl
{"text": "I love this!", "sentiment": "positive"}
{"text": "Terrible product", "sentiment": "negative"}
{"text": "It's okay", "sentiment": "neutral"}
```

**JSON Array:**

```json
[
  {"text": "I love this!", "sentiment": "positive"},
  {"text": "Terrible product", "sentiment": "negative"},
  {"text": "It's okay", "sentiment": "neutral"}
]
```

**CSV (auto-converted):**

```csv
text,sentiment
"I love this!",positive
"Terrible product",negative
"It's okay",neutral
```

**Import process:**

```
/data load sentiment_examples.csv

Loading data from sentiment_examples.csv...
✓ Detected CSV format
✓ Converting to JSONL
✓ Loaded 50 examples

Validation:
  ✓ All examples have consistent fields
  ✓ No empty values
  ✓ Field names match: text, sentiment

Data Summary:
  Total: 50 examples
  Fields: text (input), sentiment (output)
  Distribution:
    positive: 17 (34%)
    negative: 16 (32%)
    neutral: 17 (34%)

✓ Data ready for optimization!
```

## Data Quality Guidelines

### 1. Diversity

**Good - Diverse examples:**

```json
{"text": "I absolutely love this!", "sentiment": "positive"}
{"text": "Best purchase ever!", "sentiment": "positive"}
{"text": "Exceeded my expectations", "sentiment": "positive"}
{"text": "Terrible quality", "sentiment": "negative"}
{"text": "Very disappointed", "sentiment": "negative"}
{"text": "Waste of money", "sentiment": "negative"}
{"text": "It's okay", "sentiment": "neutral"}
{"text": "Nothing special", "sentiment": "neutral"}
{"text": "Average product", "sentiment": "neutral"}
```

**Bad - Repetitive examples:**

```json
{"text": "I love it", "sentiment": "positive"}
{"text": "I love this", "sentiment": "positive"}
{"text": "I love that", "sentiment": "positive"}
```

### 2. Balance

**Good - Balanced distribution:**

```
positive: 33 examples (33%)
negative: 34 examples (34%)
neutral: 33 examples (33%)
```

**Bad - Imbalanced:**

```
positive: 80 examples (80%)
negative: 15 examples (15%)
neutral: 5 examples (5%)
```

### 3. Clarity

**Good - Clear, unambiguous:**

```json
{"text": "This product is amazing!", "sentiment": "positive"}
{"text": "Worst purchase ever", "sentiment": "negative"}
```

**Bad - Ambiguous:**

```json
{"text": "Well...", "sentiment": "positive"}  // Unclear
{"text": "It's something", "sentiment": "neutral"}  // Vague
```

### 4. Realistic

**Good - Real-world examples:**

```json
{"text": "The app crashes when I click save. Very frustrating.", "sentiment": "negative"}
{"text": "Fast shipping and great customer service!", "sentiment": "positive"}
```

**Bad - Artificial examples:**

```json
{"text": "positive sentiment example", "sentiment": "positive"}
{"text": "test negative", "sentiment": "negative"}
```

### 5. Completeness

**Good - All fields present:**

```json
{
  "question": "What is Python?",
  "context": "Python is a programming language created by Guido van Rossum.",
  "answer": "Python is a programming language"
}
```

**Bad - Missing fields:**

```json
{
  "question": "What is Python?",
  "answer": "Python is a programming language"
  // Missing context field!
}
```

## Data Validation

### Automatic Validation

DSPy Code automatically validates your data:

```
/data validate
```

**Checks performed:**

1. **Consistent fields** - All examples have same inputs
2. **No empty values** - All fields have content
3. **Correct types** - Values match expected types
4. **Sufficient quantity** - Enough examples for optimization
5. **Distribution** - Balanced across categories

**Validation report:**

```
Data Validation Report:

✓ Field Consistency
  All 50 examples have fields: text, sentiment

✓ No Empty Values
  All fields contain data

✓ Type Checking
  text: string (50/50)
  sentiment: string (50/50)

✓ Quantity
  50 examples (minimum 10 required)

⚠ Distribution
  positive: 30 (60%)  ← Overrepresented
  negative: 15 (30%)
  neutral: 5 (10%)   ← Underrepresented

  Recommendation: Add more neutral and negative examples

Quality Score: 85/100

Issues: 1 warning
Errors: 0
```

### Manual Validation

Review examples manually:

```
/data show
```

**Display options:**

```
/data show --limit 10        # Show first 10
/data show --random 5        # Show 5 random
/data show --filter positive # Show only positive
/data show --stats           # Show statistics
```

## Data Augmentation

### Expand Existing Data

Generate variations of existing examples:

```
Augment my training data with 50 more diverse examples
```

**What happens:**

1. Analyzes existing examples
2. Identifies patterns
3. Generates similar but different examples
4. Maintains distribution

**Example:**

**Original:**

```json
{"text": "I love this product!", "sentiment": "positive"}
```

**Augmented:**

```json
{"text": "This product is fantastic!", "sentiment": "positive"}
{"text": "Absolutely love it!", "sentiment": "positive"}
{"text": "Best product I've bought!", "sentiment": "positive"}
```

### Paraphrase Examples

Create paraphrases for more variety:

```
Create 3 paraphrases for each example in my training data
```

### Add Edge Cases

Request specific edge cases:

```
Generate 20 edge case examples for sentiment analysis including sarcasm, mixed emotions, and ambiguous statements
```

**Generated:**

```json
{"text": "Oh great, another bug. Just what I needed.", "sentiment": "negative"}
{"text": "It's good but could be better", "sentiment": "neutral"}
{"text": "I hate to love this", "sentiment": "positive"}
```

## Data Organization

### File Naming

**By task:**

```
data/
├── sentiment_train.jsonl
├── sentiment_val.jsonl
└── sentiment_test.jsonl
```

**By version:**

```
data/
├── sentiment_v1_train.jsonl
├── sentiment_v2_train.jsonl
└── sentiment_v3_train.jsonl
```

**By source:**

```
data/
├── sentiment_ai_generated.jsonl
├── sentiment_manual.jsonl
└── sentiment_real_users.jsonl
```

### Train/Val/Test Split

**Recommended split:**

- Training: 70-80%
- Validation: 10-15%
- Test: 10-15%

**Split existing data:**

```
/data split sentiment_all.jsonl --train 0.7 --val 0.15 --test 0.15
```

**Output:**

```
Splitting sentiment_all.jsonl...

✓ Created sentiment_train.jsonl (70 examples, 70%)
✓ Created sentiment_val.jsonl (15 examples, 15%)
✓ Created sentiment_test.jsonl (15 examples, 15%)

Total: 100 examples
```

### Merge Data Files

Combine multiple data files:

```
/data merge sentiment_ai.jsonl sentiment_manual.jsonl --output sentiment_combined.jsonl
```

## Data for Different Tasks

### Classification

**Structure:**

```json
{
  "input_field": "text to classify",
  "category": "predicted_category"
}
```

**Example - Sentiment:**

```json
{"text": "I love this!", "sentiment": "positive"}
```

**Example - Email:**

```json
{
  "subject": "Meeting tomorrow",
  "body": "Can we reschedule?",
  "category": "work"
}
```

### Question Answering

**Structure:**

```json
{
  "question": "question text",
  "context": "relevant context",
  "answer": "correct answer"
}
```

**Example:**

```json
{
  "question": "What is the capital of France?",
  "context": "France is a country in Europe. Its capital is Paris.",
  "answer": "Paris"
}
```

### Text Generation

**Structure:**

```json
{
  "prompt": "generation prompt",
  "generated_text": "expected output"
}
```

**Example - Summarization:**

```json
{
  "document": "Long document text here...",
  "summary": "Brief summary of the document"
}
```

### Extraction

**Structure:**

```json
{
  "text": "text to extract from",
  "entities": ["extracted", "entities"]
}
```

**Example - Named Entity Recognition:**

```json
{
  "text": "Apple Inc. was founded by Steve Jobs in California.",
  "entities": ["Apple Inc.", "Steve Jobs", "California"]
}
```

### RAG (Retrieval-Augmented Generation)

**Structure:**

```json
{
  "query": "user question",
  "retrieved_context": "relevant documents",
  "answer": "generated answer"
}
```

**Example:**

```json
{
  "query": "How do I install DSPy?",
  "retrieved_context": "DSPy can be installed using pip: pip install dspy",
  "answer": "You can install DSPy by running 'pip install dspy' in your terminal."
}
```

## Using Gold Data for Optimization

### Save Data

```
/save-data sentiment_train.jsonl
```

**Saved to:** `data/sentiment_train.jsonl`

### Load Data for Optimization

```
/optimize my_module.py sentiment_train.jsonl
```

### Specify Data in GEPA Script

Generated GEPA scripts include data loading:

```python
def load_training_data(filepath):
    """Load training examples from JSONL."""
    examples = []
    with open(filepath, 'r') as f:
        for line in f:
            data = json.loads(line)
            example = dspy.Example(**data).with_inputs('text')
            examples.append(example)
    return examples

# Load data
trainset = load_training_data('data/sentiment_train.jsonl')
```

## Data Best Practices

### 1. Start with AI Generation

Quickest way to get started:

```
Generate 50 examples for [task]
```

### 2. Review and Refine

Check generated examples:

```
/data show --random 10
```

Remove bad examples, add edge cases.

### 3. Augment with Real Data

Add real user data when available:

```
/data load user_feedback.csv
/data merge ai_generated.jsonl user_feedback.jsonl
```

### 4. Validate Before Optimization

Always validate:

```
/data validate
```

Fix issues before running GEPA.

### 5. Keep Multiple Versions

Save versions as you improve:

```
data/
├── sentiment_v1.jsonl  # Initial AI-generated
├── sentiment_v2.jsonl  # After manual review
└── sentiment_v3.jsonl  # With real user data
```

### 6. Document Your Data

Add metadata file:

```yaml
# data/sentiment_metadata.yaml
dataset: sentiment_v3
created: 2024-01-15
total_examples: 150
source: AI-generated + manual review + user feedback
distribution:
  positive: 50
  negative: 50
  neutral: 50
quality_score: 95
notes: |
  - Includes edge cases for sarcasm
  - Balanced across all categories
  - Validated for consistency
```

## Troubleshooting

### Not Enough Examples

```
⚠️  Only 5 examples. Need at least 10 for optimization.
```

**Solution:**

```
Generate 20 more examples for [task]
```

### Imbalanced Data

```
⚠️  Distribution is imbalanced:
  positive: 80%
  negative: 15%
  neutral: 5%
```

**Solution:**

```
Generate 30 negative examples and 30 neutral examples for sentiment analysis
```

### Inconsistent Fields

```
❌ Example 5 has different fields than Example 1
```

**Solution:**

Review and fix manually, or regenerate:

```
/data validate --fix
```

### Empty Values

```
❌ Example 12 has empty 'text' field
```

**Solution:**

Remove or fix the example:

```
/data remove --index 12
```

Or regenerate:

```
/data validate --remove-empty
```

## Summary

Creating gold example data:

- ✅ AI-generated (fastest)
- ✅ Interactive collection (most control)
- ✅ Import from files (use existing data)
- ✅ Validation and quality checks
- ✅ Data augmentation
- ✅ Train/val/test splits
- ✅ Task-specific formats

**Key commands:**

- `Generate N examples for [task]` - AI generation
- `/data collect` - Interactive collection
- `/data load <file>` - Import data
- `/data validate` - Check quality
- `/save-data <file>` - Save data
- `/data split` - Create train/val/test
- `/data merge` - Combine datasets

**Best practices:**

1. Start with 50-100 examples
2. Ensure diversity and balance
3. Use clear, realistic examples
4. Validate before optimization
5. Keep multiple versions
6. Document your data

[Learn About Optimization →](optimization.md){ .md-button .md-button--primary }
[See Complete Workflow →](../tutorials/gepa-optimization.md){ .md-button }
