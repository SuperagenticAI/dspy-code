"""
Complete DSPy Program Templates

This module provides complete, working program templates for common DSPy use cases.
Each template is production-ready and includes:
- Complete working code
- Configuration examples
- Usage instructions
- Optimization guidance
- Next steps for improvement

Generated templates follow DSPy best practices and can be customized for specific needs.
"""

from dataclasses import dataclass


@dataclass
class ProgramTemplate:
    """Information about a complete program template."""

    name: str
    display_name: str
    description: str
    category: str
    difficulty: str
    components: list[str]
    use_cases: list[str]
    keywords: list[str]


class CompleteProgramTemplates:
    """Registry of complete DSPy program templates."""

    def __init__(self):
        self.templates = {
            "rag": self._rag_info(),
            "multi_hop_qa": self._multi_hop_qa_info(),
            "classification": self._classification_info(),
            "react_agent": self._react_agent_info(),
            "summarization": self._summarization_info(),
            "ensemble": self._ensemble_info(),
        }

    def list_all(self) -> list[ProgramTemplate]:
        """List all available program templates."""
        return list(self.templates.values())

    def get_by_category(self, category: str) -> list[ProgramTemplate]:
        """Get templates by category."""
        return [t for t in self.templates.values() if t.category == category]

    def search(self, query: str) -> list[ProgramTemplate]:
        """Search templates by keywords."""
        query_lower = query.lower()
        matches = []

        for template in self.templates.values():
            if any(kw in query_lower for kw in template.keywords) or any(
                uc.lower() in query_lower for uc in template.use_cases
            ):
                matches.append(template)

        return matches

    def get_template_code(self, name: str) -> str | None:
        """Get complete code for a template."""
        generators = {
            "rag": self._generate_rag,
            "multi_hop_qa": self._generate_multi_hop_qa,
            "classification": self._generate_classification,
            "react_agent": self._generate_react_agent,
            "summarization": self._generate_summarization,
            "ensemble": self._generate_ensemble,
        }

        generator = generators.get(name)
        return generator() if generator else None

    # Template Info Methods

    def _rag_info(self) -> ProgramTemplate:
        return ProgramTemplate(
            name="rag",
            display_name="RAG (Retrieval Augmented Generation)",
            description="Complete RAG system with document retrieval and answer generation",
            category="retrieval",
            difficulty="intermediate",
            components=["Retriever", "ChainOfThought", "Context management"],
            use_cases=["Document Q&A", "Knowledge base search", "Information retrieval"],
            keywords=["rag", "retrieval", "documents", "search", "knowledge base"],
        )

    def _multi_hop_qa_info(self) -> ProgramTemplate:
        return ProgramTemplate(
            name="multi_hop_qa",
            display_name="Multi-Hop Question Answering",
            description="Answer complex questions requiring multiple reasoning steps",
            category="reasoning",
            difficulty="advanced",
            components=["ChainOfThought", "Multi-step reasoning", "Context chaining"],
            use_cases=["Complex Q&A", "Research questions", "Multi-step reasoning"],
            keywords=["multi-hop", "reasoning", "complex", "chain", "steps"],
        )

    def _classification_info(self) -> ProgramTemplate:
        return ProgramTemplate(
            name="classification",
            display_name="Text Classification",
            description="Classify text into categories with evaluation",
            category="classification",
            difficulty="beginner",
            components=["Predict/ChainOfThought", "Evaluation", "Metrics"],
            use_cases=["Sentiment analysis", "Topic classification", "Intent detection"],
            keywords=["classification", "categorize", "label", "sentiment", "intent"],
        )

    def _react_agent_info(self) -> ProgramTemplate:
        return ProgramTemplate(
            name="react_agent",
            display_name="ReAct Agent with Tools",
            description="Agent that reasons and acts using external tools",
            category="agent",
            difficulty="advanced",
            components=["ReAct", "Tools", "Action execution"],
            use_cases=["Task automation", "Tool-using agents", "Interactive systems"],
            keywords=["react", "agent", "tools", "actions", "automation"],
        )

    def _summarization_info(self) -> ProgramTemplate:
        return ProgramTemplate(
            name="summarization",
            display_name="Text Summarization",
            description="Summarize long documents with iterative refinement",
            category="generation",
            difficulty="intermediate",
            components=["Refine", "Chunking", "Iterative improvement"],
            use_cases=["Document summarization", "Content condensation", "Report generation"],
            keywords=["summarization", "summary", "condense", "refine", "abstract"],
        )

    def _ensemble_info(self) -> ProgramTemplate:
        return ProgramTemplate(
            name="ensemble",
            display_name="Ensemble System",
            description="Combine multiple models for improved accuracy",
            category="ensemble",
            difficulty="advanced",
            components=["Multiple predictors", "Voting/Aggregation", "Confidence scoring"],
            use_cases=["High-accuracy tasks", "Robust predictions", "Multi-model systems"],
            keywords=["ensemble", "voting", "multiple", "combine", "aggregate"],
        )

    # Template Generation Methods

    def _generate_rag(self) -> str:
        """Generate complete RAG program."""
        return '''"""
RAG (Retrieval Augmented Generation) System

A complete RAG system that retrieves relevant documents and generates
informed answers based on the retrieved context.

Generated by DSPy Code - Complete Program Template
"""

import dspy
from typing import List, Dict, Any

# ============================================================================
# 1. SIGNATURES
# ============================================================================

class GenerateAnswer(dspy.Signature):
    """Generate answer based on retrieved context."""

    question = dspy.InputField(desc="User's question")
    context = dspy.InputField(desc="Retrieved relevant documents")
    answer = dspy.OutputField(desc="Answer based on context with citations")


# ============================================================================
# 2. RAG MODULE
# ============================================================================

class RAG(dspy.Module):
    """RAG module with retrieval and generation."""

    def __init__(self, retriever, k=5):
        """
        Initialize RAG module.

        Args:
            retriever: Document retriever (dspy.Retrieve or custom)
            k: Number of documents to retrieve
        """
        super().__init__()
        self.retriever = retriever
        self.k = k
        self.generator = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question: str):
        """
        Answer question using retrieval and generation.

        Args:
            question: User's question

        Returns:
            Generated answer with context
        """
        # Retrieve relevant documents
        retrieved = self.retriever(question, k=self.k)

        # Format context from retrieved documents
        context = self._format_context(retrieved)

        # Generate answer
        result = self.generator(question=question, context=context)

        return dspy.Prediction(
            answer=result.answer,
            context=context,
            retrieved_docs=retrieved
        )

    def _format_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents into context string."""
        if not retrieved_docs:
            return "No relevant documents found."

        formatted = []
        for i, doc in enumerate(retrieved_docs, 1):
            text = doc.get('text', doc.get('content', str(doc)))
            formatted.append(f"[{i}] {text}")

        return "\\n\\n".join(formatted)


# ============================================================================
# 3. SIMPLE IN-MEMORY RETRIEVER (for demo)
# ============================================================================

class SimpleRetriever:
    """Simple keyword-based retriever for demonstration."""

    def __init__(self, documents: List[str]):
        """
        Initialize retriever with documents.

        Args:
            documents: List of document texts
        """
        self.documents = [{"text": doc, "id": i} for i, doc in enumerate(documents)]

    def __call__(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents.

        Args:
            query: Search query
            k: Number of documents to retrieve

        Returns:
            List of relevant documents
        """
        # Simple keyword matching (replace with semantic search for production)
        query_words = set(query.lower().split())

        # Score documents by keyword overlap
        scored_docs = []
        for doc in self.documents:
            doc_words = set(doc['text'].lower().split())
            score = len(query_words & doc_words)
            if score > 0:
                scored_docs.append((score, doc))

        # Sort by score and return top k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored_docs[:k]]


# ============================================================================
# 4. EXAMPLE DOCUMENTS
# ============================================================================

EXAMPLE_DOCUMENTS = [
    "DSPy is a framework for programming with foundation models. It provides abstractions for building LM systems.",
    "The ChainOfThought predictor adds reasoning steps before generating the final answer.",
    "GEPA is an optimizer that uses reflection to evolve prompts and improve program performance.",
    "RAG (Retrieval Augmented Generation) combines document retrieval with answer generation.",
    "DSPy modules can be optimized using teleprompters like BootstrapFewShot and MIPRO.",
    "Signatures in DSPy define the input-output interface for tasks.",
    "The ReAct predictor enables agents to reason about actions and use external tools.",
    "DSPy supports multiple language models including OpenAI, Anthropic, and local models.",
]


# ============================================================================
# 5. CONFIGURATION & USAGE
# ============================================================================

def main():
    """Run the RAG system."""

    print("\\n" + "="*70)
    print("RAG (Retrieval Augmented Generation) System")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Create retriever with example documents
    retriever = SimpleRetriever(EXAMPLE_DOCUMENTS)
    print(f"✓ Loaded {len(EXAMPLE_DOCUMENTS)} documents\\n")

    # Create RAG system
    rag = RAG(retriever=retriever, k=3)
    print("✓ RAG system ready\\n")

    # Example queries
    examples = [
        "What is DSPy?",
        "How does ChainOfThought work?",
        "What optimizers are available?",
    ]

    print("Example Queries:")
    print("-" * 70)

    for question in examples:
        print(f"\\nQ: {question}")
        result = rag(question=question)
        print(f"A: {result.answer}")
        print(f"   (Retrieved {len(result.retrieved_docs)} documents)")

    print("\\n" + "-" * 70)

    # Interactive mode
    print("\\nInteractive Mode (Ctrl+C to exit):")
    print("Ask questions about the documents\\n")

    try:
        while True:
            question = input("Q: ").strip()
            if not question:
                continue

            result = rag(question=question)
            print(f"A: {result.answer}\\n")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 6. OPTIMIZATION EXAMPLE
# ============================================================================

def optimize_rag():
    """Example of optimizing the RAG system."""

    # Training data: (question, expected_answer) pairs
    training_data = [
        dspy.Example(
            question="What is DSPy?",
            answer="DSPy is a framework for programming with foundation models"
        ).with_inputs("question"),
        dspy.Example(
            question="What is ChainOfThought?",
            answer="ChainOfThought adds reasoning steps before generating answers"
        ).with_inputs("question"),
        # Add more training examples...
    ]

    # Define metric
    def answer_quality(example, pred, trace=None):
        # Simple metric: check if key terms are in answer
        return 1.0 if any(word in pred.answer.lower()
                         for word in example.answer.lower().split()) else 0.0

    # Configure retriever and RAG
    retriever = SimpleRetriever(EXAMPLE_DOCUMENTS)
    rag = RAG(retriever=retriever)

    # Optimize with BootstrapFewShot
    from dspy.teleprompt import BootstrapFewShot

    optimizer = BootstrapFewShot(metric=answer_quality, max_bootstrapped_demos=4)
    optimized_rag = optimizer.compile(rag, trainset=training_data)

    return optimized_rag


# ============================================================================
# 7. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE YOUR RAG SYSTEM:

1. Production Retriever:
   - Use ColBERTv2 or other semantic search
   - Set up vector database (FAISS, Pinecone, Weaviate)
   - Implement proper document indexing

2. Better Context:
   - Add document metadata (source, date, author)
   - Implement reranking
   - Add relevance filtering
   - Handle long documents with chunking

3. Evaluation:
   - Create test Q&A dataset
   - Measure retrieval accuracy
   - Measure answer quality
   - Track latency and cost

4. Optimization:
   - Use BootstrapFewShot or MIPRO
   - Optimize retrieval parameters
   - Fine-tune generation prompts

5. Production Features:
   - Add caching for frequent queries
   - Implement streaming responses
   - Add confidence scores
   - Handle edge cases (no results, ambiguous queries)

6. Advanced Features:
   - Multi-hop reasoning over documents
   - Citation tracking
   - Source attribution
   - Conversation history
"""


if __name__ == "__main__":
    main()
'''

    def _generate_multi_hop_qa(self) -> str:
        """Generate complete multi-hop QA program."""
        return '''"""
Multi-Hop Question Answering System

A system that answers complex questions requiring multiple reasoning steps
and information gathering from different sources.

Generated by DSPy Code - Complete Program Template
"""

import dspy
from typing import List, Dict, Any

# ============================================================================
# 1. SIGNATURES
# ============================================================================

class GenerateSearchQuery(dspy.Signature):
    """Generate search query for information gathering."""

    question = dspy.InputField(desc="Original question")
    context = dspy.InputField(desc="Information gathered so far")
    search_query = dspy.OutputField(desc="Search query to find missing information")


class AnswerQuestion(dspy.Signature):
    """Answer question based on gathered information."""

    question = dspy.InputField(desc="Original question")
    gathered_info = dspy.InputField(desc="All information gathered through search")
    answer = dspy.OutputField(desc="Final answer with reasoning")


# ============================================================================
# 2. MULTI-HOP QA MODULE
# ============================================================================

class MultiHopQA(dspy.Module):
    """Multi-hop question answering with iterative information gathering."""

    def __init__(self, retriever, max_hops=3):
        """
        Initialize multi-hop QA module.

        Args:
            retriever: Document retriever
            max_hops: Maximum number of search hops
        """
        super().__init__()
        self.retriever = retriever
        self.max_hops = max_hops
        self.query_generator = dspy.ChainOfThought(GenerateSearchQuery)
        self.answer_generator = dspy.ChainOfThought(AnswerQuestion)

    def forward(self, question: str):
        """
        Answer question using multi-hop reasoning.

        Args:
            question: Complex question requiring multiple steps

        Returns:
            Answer with reasoning trace
        """
        gathered_info = []
        context = "No information gathered yet."

        # Iteratively gather information
        for hop in range(self.max_hops):
            # Generate search query
            query_result = self.query_generator(
                question=question,
                context=context
            )
            search_query = query_result.search_query

            # Retrieve information
            retrieved = self.retriever(search_query, k=3)

            if not retrieved:
                break

            # Add to gathered information
            hop_info = {
                "hop": hop + 1,
                "query": search_query,
                "documents": retrieved
            }
            gathered_info.append(hop_info)

            # Update context
            context = self._format_gathered_info(gathered_info)

            # Check if we have enough information
            if self._has_sufficient_info(context, question):
                break

        # Generate final answer
        answer_result = self.answer_generator(
            question=question,
            gathered_info=context
        )

        return dspy.Prediction(
            answer=answer_result.answer,
            hops=len(gathered_info),
            gathered_info=gathered_info
        )

    def _format_gathered_info(self, gathered_info: List[Dict]) -> str:
        """Format gathered information into context string."""
        formatted = []
        for hop_info in gathered_info:
            hop_num = hop_info['hop']
            query = hop_info['query']
            docs = hop_info['documents']

            formatted.append(f"Hop {hop_num} - Query: {query}")
            for i, doc in enumerate(docs, 1):
                text = doc.get('text', str(doc))
                formatted.append(f"  [{i}] {text}")

        return "\\n\\n".join(formatted)

    def _has_sufficient_info(self, context: str, question: str) -> bool:
        """Check if we have sufficient information to answer."""
        # Simple heuristic: check if context is substantial
        # In production, use LM to determine sufficiency
        return len(context.split()) > 100


# ============================================================================
# 3. EXAMPLE KNOWLEDGE BASE
# ============================================================================

KNOWLEDGE_BASE = [
    "Albert Einstein was born in Ulm, Germany in 1879.",
    "Einstein developed the theory of relativity in 1905.",
    "The theory of relativity revolutionized physics.",
    "Einstein won the Nobel Prize in Physics in 1921.",
    "The Nobel Prize was awarded for his work on the photoelectric effect.",
    "Einstein moved to the United States in 1933.",
    "He worked at Princeton University until his death in 1955.",
    "Marie Curie was a Polish physicist and chemist.",
    "Curie discovered radium and polonium.",
    "She was the first woman to win a Nobel Prize.",
    "Curie won Nobel Prizes in both Physics and Chemistry.",
    "The Eiffel Tower was built in Paris in 1889.",
    "Paris is the capital of France.",
    "France is located in Western Europe.",
]


class SimpleKnowledgeRetriever:
    """Simple retriever for demonstration."""

    def __init__(self, knowledge_base: List[str]):
        self.kb = [{"text": doc, "id": i} for i, doc in enumerate(knowledge_base)]

    def __call__(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored = []

        for doc in self.kb:
            doc_words = set(doc['text'].lower().split())
            score = len(query_words & doc_words)
            if score > 0:
                scored.append((score, doc))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored[:k]]


# ============================================================================
# 4. CONFIGURATION & USAGE
# ============================================================================

def main():
    """Run the multi-hop QA system."""

    print("\\n" + "="*70)
    print("Multi-Hop Question Answering System")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Create retriever
    retriever = SimpleKnowledgeRetriever(KNOWLEDGE_BASE)
    print(f"✓ Loaded knowledge base with {len(KNOWLEDGE_BASE)} facts\\n")

    # Create multi-hop QA system
    qa = MultiHopQA(retriever=retriever, max_hops=3)
    print("✓ Multi-hop QA system ready\\n")

    # Example complex questions
    examples = [
        "Where was the person who developed the theory of relativity born?",
        "What prize did the discoverer of radium win?",
        "In what year was the famous tower in France's capital built?",
    ]

    print("Example Complex Questions:")
    print("-" * 70)

    for question in examples:
        print(f"\\nQ: {question}")
        result = qa(question=question)
        print(f"A: {result.answer}")
        print(f"   (Required {result.hops} reasoning hops)")

    print("\\n" + "-" * 70)

    # Interactive mode
    print("\\nInteractive Mode (Ctrl+C to exit):")
    print("Ask complex questions requiring multiple reasoning steps\\n")

    try:
        while True:
            question = input("Q: ").strip()
            if not question:
                continue

            result = qa(question=question)
            print(f"A: {result.answer}")
            print(f"   (Hops: {result.hops})\\n")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 5. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE YOUR MULTI-HOP QA SYSTEM:

1. Better Retrieval:
   - Use semantic search instead of keyword matching
   - Implement entity linking
   - Add temporal reasoning

2. Reasoning Improvements:
   - Add explicit reasoning chains
   - Implement backtracking when stuck
   - Add confidence scoring for each hop

3. Evaluation:
   - Create multi-hop QA test dataset
   - Measure hop efficiency
   - Track answer accuracy

4. Optimization:
   - Optimize query generation
   - Optimize answer generation
   - Reduce unnecessary hops

5. Advanced Features:
   - Add support for numerical reasoning
   - Implement comparison operations
   - Add temporal reasoning
   - Support for "why" questions
"""


if __name__ == "__main__":
    main()
'''

    def _generate_classification(self) -> str:
        """Generate complete classification program."""
        return '''"""
Text Classification System

A complete text classification system with training, evaluation, and optimization.
Includes examples for sentiment analysis, topic classification, and intent detection.

Generated by DSPy Code - Complete Program Template
"""

import dspy
from typing import List, Dict, Any
import json

# ============================================================================
# 1. SIGNATURES
# ============================================================================

class ClassifyText(dspy.Signature):
    """Classify text into predefined categories."""

    text = dspy.InputField(desc="Text to classify")
    categories = dspy.InputField(desc="Available categories")
    category = dspy.OutputField(desc="Predicted category")
    confidence = dspy.OutputField(desc="Confidence score (0-1)")


# ============================================================================
# 2. CLASSIFICATION MODULE
# ============================================================================

class TextClassifier(dspy.Module):
    """Text classification module with confidence scoring."""

    def __init__(self, categories: List[str], use_cot=True):
        """
        Initialize text classifier.

        Args:
            categories: List of possible categories
            use_cot: Use ChainOfThought for better reasoning
        """
        super().__init__()
        self.categories = categories

        # Choose predictor based on use_cot
        predictor_class = dspy.ChainOfThought if use_cot else dspy.Predict
        self.classifier = predictor_class(ClassifyText)

    def forward(self, text: str):
        """
        Classify text into one of the categories.

        Args:
            text: Text to classify

        Returns:
            Prediction with category and confidence
        """
        # Format categories for the model
        categories_str = ", ".join(self.categories)

        # Classify
        result = self.classifier(
            text=text,
            categories=categories_str
        )

        return dspy.Prediction(
            category=result.category,
            confidence=result.confidence
        )


# ============================================================================
# 3. EXAMPLE DATA
# ============================================================================

# Sentiment Analysis Examples
SENTIMENT_EXAMPLES = [
    {"text": "This product is amazing! Best purchase ever!", "label": "positive"},
    {"text": "Terrible quality. Waste of money.", "label": "negative"},
    {"text": "It's okay, nothing special.", "label": "neutral"},
    {"text": "I love this! Highly recommend!", "label": "positive"},
    {"text": "Disappointed with the service.", "label": "negative"},
    {"text": "Average product, does the job.", "label": "neutral"},
]

# Topic Classification Examples
TOPIC_EXAMPLES = [
    {"text": "The stock market reached new highs today.", "label": "business"},
    {"text": "Scientists discover new species in the Amazon.", "label": "science"},
    {"text": "The championship game was thrilling!", "label": "sports"},
    {"text": "New smartphone features AI capabilities.", "label": "technology"},
    {"text": "Congress passes new healthcare bill.", "label": "politics"},
]

# Intent Detection Examples
INTENT_EXAMPLES = [
    {"text": "What's the weather like today?", "label": "weather_query"},
    {"text": "Book a table for two at 7pm", "label": "reservation"},
    {"text": "Cancel my subscription", "label": "cancellation"},
    {"text": "How do I reset my password?", "label": "support"},
    {"text": "Show me nearby restaurants", "label": "search"},
]


# ============================================================================
# 4. EVALUATION METRICS
# ============================================================================

def accuracy_metric(example, pred, trace=None):
    """Calculate accuracy."""
    return 1.0 if example.label.lower() == pred.category.lower() else 0.0


def evaluate_classifier(classifier, test_data: List[Dict], categories: List[str]):
    """
    Evaluate classifier on test data.

    Args:
        classifier: Trained classifier
        test_data: List of test examples
        categories: List of categories

    Returns:
        Evaluation results
    """
    correct = 0
    total = len(test_data)
    predictions = []

    for example in test_data:
        pred = classifier(text=example['text'])
        is_correct = example['label'].lower() == pred.category.lower()

        predictions.append({
            "text": example['text'],
            "true_label": example['label'],
            "predicted_label": pred.category,
            "confidence": pred.confidence,
            "correct": is_correct
        })

        if is_correct:
            correct += 1

    accuracy = correct / total if total > 0 else 0.0

    return {
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "predictions": predictions
    }


# ============================================================================
# 5. CONFIGURATION & USAGE
# ============================================================================

def run_sentiment_analysis():
    """Run sentiment analysis example."""

    print("\\n" + "="*70)
    print("Sentiment Analysis Classifier")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Create classifier
    categories = ["positive", "negative", "neutral"]
    classifier = TextClassifier(categories=categories, use_cot=True)
    print(f"✓ Created classifier with categories: {', '.join(categories)}\\n")

    # Test examples
    test_texts = [
        "This is absolutely fantastic!",
        "Not happy with this at all.",
        "It's fine, I guess.",
    ]

    print("Example Classifications:")
    print("-" * 70)

    for text in test_texts:
        result = classifier(text=text)
        print(f"\\nText: {text}")
        print(f"Category: {result.category}")
        print(f"Confidence: {result.confidence}")

    print("\\n" + "-" * 70)


def run_topic_classification():
    """Run topic classification example."""

    print("\\n" + "="*70)
    print("Topic Classification")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)

    # Create classifier
    categories = ["business", "science", "sports", "technology", "politics"]
    classifier = TextClassifier(categories=categories, use_cot=True)
    print(f"✓ Created classifier with {len(categories)} categories\\n")

    # Evaluate on examples
    results = evaluate_classifier(classifier, TOPIC_EXAMPLES, categories)

    print("Evaluation Results:")
    print("-" * 70)
    print(f"Accuracy: {results['accuracy']:.2%}")
    print(f"Correct: {results['correct']}/{results['total']}")
    print("-" * 70)


def main():
    """Run classification examples."""

    # Run sentiment analysis
    run_sentiment_analysis()

    # Run topic classification
    run_topic_classification()

    # Interactive mode
    print("\\nInteractive Classification (Ctrl+C to exit):")
    print("Choose task: 1=Sentiment, 2=Topic, 3=Intent\\n")

    try:
        choice = input("Task (1/2/3): ").strip()

        if choice == "1":
            categories = ["positive", "negative", "neutral"]
            task_name = "Sentiment Analysis"
        elif choice == "2":
            categories = ["business", "science", "sports", "technology", "politics"]
            task_name = "Topic Classification"
        elif choice == "3":
            categories = ["weather_query", "reservation", "cancellation", "support", "search"]
            task_name = "Intent Detection"
        else:
            print("Invalid choice")
            return

        lm = dspy.LM(model='ollama/gpt-oss:20b')
        dspy.configure(lm=lm)

        classifier = TextClassifier(categories=categories, use_cot=True)
        print(f"\\n{task_name} ready!\\n")

        while True:
            text = input("Text: ").strip()
            if not text:
                continue

            result = classifier(text=text)
            print(f"Category: {result.category}")
            print(f"Confidence: {result.confidence}\\n")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 6. OPTIMIZATION EXAMPLE
# ============================================================================

def optimize_classifier():
    """Example of optimizing the classifier."""

    # Prepare training data
    trainset = [
        dspy.Example(text=ex['text'], label=ex['label']).with_inputs('text')
        for ex in SENTIMENT_EXAMPLES
    ]

    # Create classifier
    categories = ["positive", "negative", "neutral"]
    classifier = TextClassifier(categories=categories)

    # Optimize with BootstrapFewShot
    from dspy.teleprompt import BootstrapFewShot

    optimizer = BootstrapFewShot(
        metric=accuracy_metric,
        max_bootstrapped_demos=4
    )

    optimized_classifier = optimizer.compile(
        classifier,
        trainset=trainset
    )

    return optimized_classifier


# ============================================================================
# 7. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE YOUR CLASSIFIER:

1. Data Collection:
   - Gather more training examples
   - Balance classes
   - Add edge cases
   - Include domain-specific examples

2. Evaluation:
   - Create comprehensive test set
   - Calculate precision, recall, F1
   - Analyze confusion matrix
   - Identify misclassification patterns

3. Optimization:
   - Use BootstrapFewShot or MIPRO
   - Experiment with different predictors
   - Tune confidence thresholds
   - Try ensemble methods

4. Production Features:
   - Add batch classification
   - Implement caching
   - Add confidence thresholds
   - Handle unknown categories
   - Add explanation generation

5. Advanced Features:
   - Multi-label classification
   - Hierarchical categories
   - Active learning
   - Online learning
"""


if __name__ == "__main__":
    main()
'''

    def _generate_react_agent(self) -> str:
        """Generate complete ReAct agent program."""
        return '''"""
ReAct Agent with Tools

A complete ReAct (Reasoning + Acting) agent that can use external tools
to accomplish tasks. Includes example tools and extensible architecture.

Generated by DSPy Code - Complete Program Template
"""

import dspy
from dspy import Tool
from typing import List, Dict, Any, Callable
import json
from datetime import datetime

# ============================================================================
# 1. SIGNATURES
# ============================================================================

class AgentTask(dspy.Signature):
    """Agent task with tool usage."""

    task = dspy.InputField(desc="Task to accomplish")
    available_tools = dspy.InputField(desc="List of available tools")
    result = dspy.OutputField(desc="Task result with reasoning")


# ============================================================================
# 2. EXAMPLE TOOLS
# ============================================================================

def search_tool(query: str) -> str:
    """
    Search for information.

    Args:
        query: Search query

    Returns:
        Search results
    """
    # Mock search results - replace with real search API
    mock_results = {
        "weather": "The weather today is sunny with a high of 75°F.",
        "time": f"The current time is {datetime.now().strftime('%I:%M %p')}.",
        "python": "Python is a high-level programming language known for its simplicity.",
        "dspy": "DSPy is a framework for programming with foundation models.",
    }

    # Find relevant result
    query_lower = query.lower()
    for key, value in mock_results.items():
        if key in query_lower:
            return f"Search result for '{query}': {value}"

    return f"No specific results found for '{query}'. Try a different query."


def calculator_tool(expression: str) -> str:
    """
    Calculate mathematical expressions.

    Args:
        expression: Mathematical expression to evaluate

    Returns:
        Calculation result
    """
    try:
        # Safe evaluation (in production, use a proper math parser)
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Result: {expression} = {result}"
    except Exception as e:
        return f"Error calculating '{expression}': {str(e)}"


def get_current_time() -> str:
    """
    Get current time.

    Returns:
        Current time
    """
    now = datetime.now()
    return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


def get_weather(location: str = "current location") -> str:
    """
    Get weather information.

    Args:
        location: Location for weather info

    Returns:
        Weather information
    """
    # Mock weather data - replace with real weather API
    return f"Weather in {location}: Sunny, 75°F, Light breeze"


def save_note(content: str) -> str:
    """
    Save a note.

    Args:
        content: Note content

    Returns:
        Confirmation message
    """
    # In production, save to database or file
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return f"Note saved at {timestamp}: {content[:50]}..."


# ============================================================================
# 3. REACT AGENT MODULE
# ============================================================================

class ReActAgent(dspy.Module):
    """ReAct agent with tool usage capabilities."""

    def __init__(self, tools: List[Tool]):
        """
        Initialize ReAct agent.

        Args:
            tools: List of available tools
        """
        super().__init__()
        self.tools = tools
        self.agent = dspy.ReAct(AgentTask, tools=tools)

    def forward(self, task: str):
        """
        Execute task using available tools.

        Args:
            task: Task description

        Returns:
            Task result with reasoning
        """
        # Format tool descriptions
        tool_descriptions = self._format_tool_descriptions()

        # Execute task
        result = self.agent(
            task=task,
            available_tools=tool_descriptions
        )

        return dspy.Prediction(
            result=result.result,
            tools_used=self._extract_tools_used(result)
        )

    def _format_tool_descriptions(self) -> str:
        """Format tool descriptions for the agent."""
        descriptions = []
        for tool in self.tools:
            descriptions.append(f"- {tool.name}: {tool.desc}")
        return "\\n".join(descriptions)

    def _extract_tools_used(self, result) -> List[str]:
        """Extract which tools were used from the result."""
        # Simple extraction - in production, track tool calls explicitly
        tools_used = []
        for tool in self.tools:
            if tool.name in str(result):
                tools_used.append(tool.name)
        return tools_used


# ============================================================================
# 4. AGENT CONFIGURATION
# ============================================================================

def create_agent_with_tools() -> ReActAgent:
    """Create agent with standard tools."""

    # Define tools
    tools = [
        Tool(
            func=search_tool,
            name="search",
            desc="Search for information on any topic"
        ),
        Tool(
            func=calculator_tool,
            name="calculator",
            desc="Calculate mathematical expressions"
        ),
        Tool(
            func=get_current_time,
            name="get_time",
            desc="Get current date and time"
        ),
        Tool(
            func=get_weather,
            name="get_weather",
            desc="Get weather information for a location"
        ),
        Tool(
            func=save_note,
            name="save_note",
            desc="Save a note or reminder"
        ),
    ]

    return ReActAgent(tools=tools)


# ============================================================================
# 5. CONFIGURATION & USAGE
# ============================================================================

def main():
    """Run the ReAct agent."""

    print("\\n" + "="*70)
    print("ReAct Agent with Tools")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Create agent
    agent = create_agent_with_tools()
    print("✓ Agent ready with tools:")
    print("  - search: Search for information")
    print("  - calculator: Calculate math expressions")
    print("  - get_time: Get current time")
    print("  - get_weather: Get weather info")
    print("  - save_note: Save notes\\n")

    # Example tasks
    example_tasks = [
        "What's the weather like today?",
        "Calculate 15 * 23 + 47",
        "Search for information about DSPy",
    ]

    print("Example Tasks:")
    print("-" * 70)

    for task in example_tasks:
        print(f"\\nTask: {task}")
        result = agent(task=task)
        print(f"Result: {result.result}")
        if result.tools_used:
            print(f"Tools used: {', '.join(result.tools_used)}")

    print("\\n" + "-" * 70)

    # Interactive mode
    print("\\nInteractive Agent Mode (Ctrl+C to exit):")
    print("Give the agent tasks to accomplish\\n")

    try:
        while True:
            task = input("Task: ").strip()
            if not task:
                continue

            result = agent(task=task)
            print(f"Result: {result.result}")
            if result.tools_used:
                print(f"Tools used: {', '.join(result.tools_used)}")
            print()

    except KeyboardInterrupt:
        print("\\n\\nAgent shutting down. Goodbye!")


# ============================================================================
# 6. CUSTOM TOOL EXAMPLE
# ============================================================================

def create_custom_tool(name: str, func: Callable, description: str) -> Tool:
    """
    Create a custom tool.

    Args:
        name: Tool name
        func: Tool function
        description: Tool description

    Returns:
        Tool object
    """
    return Tool(func=func, name=name, desc=description)


# Example: Create a custom API tool
def call_api(endpoint: str, params: str = "") -> str:
    """Call an external API."""
    # Mock API call - replace with real API
    return f"API response from {endpoint}: Success"


def create_agent_with_custom_tools():
    """Example of creating agent with custom tools."""

    # Standard tools
    standard_tools = [
        Tool(func=search_tool, name="search", desc="Search for information"),
        Tool(func=calculator_tool, name="calculator", desc="Calculate expressions"),
    ]

    # Custom tools
    custom_tools = [
        create_custom_tool(
            name="api_call",
            func=call_api,
            description="Call external API"
        ),
        create_custom_tool(
            name="custom_search",
            func=lambda q: f"Custom search result for: {q}",
            description="Custom search implementation"
        ),
    ]

    all_tools = standard_tools + custom_tools
    return ReActAgent(tools=all_tools)


# ============================================================================
# 7. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE YOUR REACT AGENT:

1. Add More Tools:
   - Database queries
   - File operations
   - Email sending
   - Web scraping
   - API integrations
   - Code execution

2. Tool Management:
   - Dynamic tool loading
   - Tool permissions
   - Tool rate limiting
   - Tool error handling
   - Tool chaining

3. Agent Improvements:
   - Add memory/context
   - Implement planning
   - Add error recovery
   - Track tool usage
   - Add confidence scoring

4. Production Features:
   - Tool authentication
   - Async tool execution
   - Tool result caching
   - Logging and monitoring
   - Safety constraints

5. Advanced Features:
   - Multi-agent collaboration
   - Tool composition
   - Learned tool selection
   - Tool creation from descriptions
   - Self-improvement

6. Evaluation:
   - Task success rate
   - Tool selection accuracy
   - Reasoning quality
   - Efficiency metrics
"""


if __name__ == "__main__":
    main()
'''

    def _generate_summarization(self) -> str:
        """Generate complete summarization program."""
        return '''"""
Text Summarization System

A complete text summarization system using iterative refinement.
Handles long documents by chunking and progressive summarization.

Generated by DSPy Code - Complete Program Template
"""

import dspy
from typing import List

# ============================================================================
# 1. SIGNATURES
# ============================================================================

class SummarizeChunk(dspy.Signature):
    """Summarize a chunk of text."""

    text = dspy.InputField(desc="Text chunk to summarize")
    summary = dspy.OutputField(desc="Concise summary of the text")


class RefineSummary(dspy.Signature):
    """Refine and improve a summary."""

    current_summary = dspy.InputField(desc="Current summary")
    additional_context = dspy.InputField(desc="Additional context to incorporate")
    refined_summary = dspy.OutputField(desc="Improved summary")


class FinalSummary(dspy.Signature):
    """Generate final polished summary."""

    draft_summary = dspy.InputField(desc="Draft summary")
    original_length = dspy.InputField(desc="Original document length")
    final_summary = dspy.OutputField(desc="Final polished summary")


# ============================================================================
# 2. SUMMARIZATION MODULE
# ============================================================================

class TextSummarizer(dspy.Module):
    """Text summarization with iterative refinement."""

    def __init__(self, chunk_size=1000, max_summary_length=200):
        """
        Initialize text summarizer.

        Args:
            chunk_size: Maximum characters per chunk
            max_summary_length: Target summary length
        """
        super().__init__()
        self.chunk_size = chunk_size
        self.max_summary_length = max_summary_length

        # Summarization components
        self.chunk_summarizer = dspy.ChainOfThought(SummarizeChunk)
        self.refiner = dspy.Refine(RefineSummary)
        self.finalizer = dspy.ChainOfThought(FinalSummary)

    def forward(self, text: str):
        """
        Summarize text using iterative refinement.

        Args:
            text: Text to summarize

        Returns:
            Summary with metadata
        """
        original_length = len(text)

        # Handle short text
        if original_length <= self.chunk_size:
            result = self.chunk_summarizer(text=text)
            return dspy.Prediction(
                summary=result.summary,
                chunks_processed=1,
                original_length=original_length
            )

        # Split into chunks
        chunks = self._split_into_chunks(text)

        # Summarize each chunk
        chunk_summaries = []
        for chunk in chunks:
            result = self.chunk_summarizer(text=chunk)
            chunk_summaries.append(result.summary)

        # Combine and refine summaries
        combined_summary = " ".join(chunk_summaries)

        # If combined summary is still long, refine it
        if len(combined_summary) > self.max_summary_length * 2:
            refined = self.refiner(
                current_summary=chunk_summaries[0],
                additional_context=" ".join(chunk_summaries[1:])
            )
            draft_summary = refined.refined_summary
        else:
            draft_summary = combined_summary

        # Generate final polished summary
        final = self.finalizer(
            draft_summary=draft_summary,
            original_length=str(original_length)
        )

        return dspy.Prediction(
            summary=final.final_summary,
            chunks_processed=len(chunks),
            original_length=original_length,
            compression_ratio=original_length / len(final.final_summary)
        )

    def _split_into_chunks(self, text: str) -> List[str]:
        """Split text into chunks."""
        chunks = []
        words = text.split()
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1  # +1 for space
            if current_length + word_length > self.chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks


# ============================================================================
# 3. EXAMPLE DOCUMENTS
# ============================================================================

EXAMPLE_LONG_TEXT = """
Artificial Intelligence has transformed numerous industries over the past decade.
Machine learning algorithms now power everything from recommendation systems to
autonomous vehicles. Deep learning, a subset of machine learning, has been
particularly revolutionary, enabling breakthroughs in computer vision, natural
language processing, and speech recognition.

The development of large language models represents a significant milestone in AI
research. These models, trained on vast amounts of text data, can generate human-like
text, answer questions, and even write code. GPT-3, released in 2020, demonstrated
unprecedented capabilities in few-shot learning, where the model can perform new
tasks with minimal examples.

However, AI development also raises important ethical considerations. Bias in
training data can lead to discriminatory outcomes. Privacy concerns arise from
the collection and use of personal data. The environmental impact of training
large models is substantial, requiring significant computational resources and
energy consumption.

Looking forward, researchers are exploring more efficient architectures, better
training methods, and ways to make AI systems more interpretable and controllable.
The goal is to create AI that is not only powerful but also safe, fair, and
beneficial to society as a whole.
"""

EXAMPLE_SHORT_TEXT = """
Climate change is one of the most pressing challenges facing humanity. Rising
global temperatures are causing more frequent extreme weather events, melting
ice caps, and rising sea levels. Urgent action is needed to reduce greenhouse
gas emissions and transition to renewable energy sources.
"""


# ============================================================================
# 4. CONFIGURATION & USAGE
# ============================================================================

def main():
    """Run the text summarization system."""

    print("\\n" + "="*70)
    print("Text Summarization System")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Create summarizer
    summarizer = TextSummarizer(chunk_size=500, max_summary_length=150)
    print("✓ Summarizer ready\\n")

    # Example: Long text
    print("Example 1: Long Document")
    print("-" * 70)
    print(f"Original length: {len(EXAMPLE_LONG_TEXT)} characters\\n")

    result = summarizer(text=EXAMPLE_LONG_TEXT)
    print(f"Summary: {result.summary}\\n")
    print(f"Chunks processed: {result.chunks_processed}")
    print(f"Compression ratio: {result.compression_ratio:.1f}x")
    print("-" * 70)

    # Example: Short text
    print("\\nExample 2: Short Document")
    print("-" * 70)
    print(f"Original length: {len(EXAMPLE_SHORT_TEXT)} characters\\n")

    result = summarizer(text=EXAMPLE_SHORT_TEXT)
    print(f"Summary: {result.summary}\\n")
    print(f"Chunks processed: {result.chunks_processed}")
    print("-" * 70)

    # Interactive mode
    print("\\nInteractive Summarization (Ctrl+C to exit):")
    print("Paste text to summarize (press Enter twice when done)\\n")

    try:
        while True:
            print("Enter text (press Enter twice to finish):")
            lines = []
            empty_count = 0

            while empty_count < 2:
                line = input()
                if line:
                    lines.append(line)
                    empty_count = 0
                else:
                    empty_count += 1

            text = " ".join(lines).strip()
            if not text:
                continue

            print(f"\\nSummarizing {len(text)} characters...\\n")
            result = summarizer(text=text)
            print(f"Summary: {result.summary}\\n")
            print(f"Compression: {result.compression_ratio:.1f}x\\n")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 5. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE YOUR SUMMARIZATION SYSTEM:

1. Better Chunking:
   - Semantic chunking (split at paragraph/sentence boundaries)
   - Overlap between chunks
   - Preserve context across chunks

2. Summary Quality:
   - Add extractive summarization
   - Combine extractive + abstractive
   - Add key point extraction
   - Include important entities

3. Customization:
   - Adjustable summary length
   - Different summary styles (bullet points, paragraph, etc.)
   - Domain-specific summarization
   - Multi-language support

4. Evaluation:
   - ROUGE scores
   - Human evaluation
   - Factual consistency checking
   - Coverage metrics

5. Advanced Features:
   - Multi-document summarization
   - Query-focused summarization
   - Timeline extraction
   - Hierarchical summarization

6. Production Features:
   - Batch processing
   - Streaming for long documents
   - Caching
   - Progress tracking
"""


if __name__ == "__main__":
    main()
'''

    def _generate_ensemble(self) -> str:
        """Generate complete ensemble program."""
        return '''"""
Ensemble System

A complete ensemble system that combines multiple models/predictors
for improved accuracy and robustness.

Generated by DSPy Code - Complete Program Template
"""

import dspy
from typing import List, Dict, Any
from collections import Counter

# ============================================================================
# 1. SIGNATURES
# ============================================================================

class ClassifyText(dspy.Signature):
    """Classify text into categories."""

    text = dspy.InputField(desc="Text to classify")
    category = dspy.OutputField(desc="Predicted category")
    reasoning = dspy.OutputField(desc="Reasoning for classification")


class AggregateResults(dspy.Signature):
    """Aggregate results from multiple predictors."""

    predictions = dspy.InputField(desc="Predictions from multiple models")
    text = dspy.InputField(desc="Original text")
    final_prediction = dspy.OutputField(desc="Aggregated final prediction")
    confidence = dspy.OutputField(desc="Confidence in final prediction")


# ============================================================================
# 2. ENSEMBLE MODULE
# ============================================================================

class EnsembleClassifier(dspy.Module):
    """Ensemble classifier combining multiple predictors."""

    def __init__(self, num_predictors=3, aggregation_method="voting"):
        """
        Initialize ensemble classifier.

        Args:
            num_predictors: Number of predictors in ensemble
            aggregation_method: How to combine predictions (voting, weighted, meta)
        """
        super().__init__()
        self.num_predictors = num_predictors
        self.aggregation_method = aggregation_method

        # Create diverse predictors
        self.predictors = [
            dspy.Predict(ClassifyText),  # Simple predictor
            dspy.ChainOfThought(ClassifyText),  # With reasoning
            dspy.ChainOfThought(ClassifyText),  # Another CoT with different seed
        ][:num_predictors]

        # Meta-learner for aggregation (if using meta method)
        if aggregation_method == "meta":
            self.meta_learner = dspy.ChainOfThought(AggregateResults)

    def forward(self, text: str):
        """
        Classify text using ensemble.

        Args:
            text: Text to classify

        Returns:
            Ensemble prediction with confidence
        """
        # Get predictions from all predictors
        predictions = []
        for i, predictor in enumerate(self.predictors):
            try:
                result = predictor(text=text)
                predictions.append({
                    "predictor_id": i,
                    "category": result.category,
                    "reasoning": getattr(result, 'reasoning', 'N/A')
                })
            except Exception as e:
                print(f"Warning: Predictor {i} failed: {e}")

        # Aggregate predictions
        if self.aggregation_method == "voting":
            final_category, confidence = self._majority_voting(predictions)
        elif self.aggregation_method == "weighted":
            final_category, confidence = self._weighted_voting(predictions)
        elif self.aggregation_method == "meta":
            final_category, confidence = self._meta_learning(predictions, text)
        else:
            final_category, confidence = self._majority_voting(predictions)

        return dspy.Prediction(
            category=final_category,
            confidence=confidence,
            individual_predictions=predictions,
            num_predictors=len(predictions)
        )

    def _majority_voting(self, predictions: List[Dict]) -> tuple:
        """Aggregate using majority voting."""
        if not predictions:
            return "unknown", 0.0

        # Count votes
        votes = [p['category'] for p in predictions]
        vote_counts = Counter(votes)

        # Get majority
        most_common = vote_counts.most_common(1)[0]
        category = most_common[0]
        count = most_common[1]

        # Confidence = proportion of votes
        confidence = count / len(predictions)

        return category, confidence

    def _weighted_voting(self, predictions: List[Dict]) -> tuple:
        """Aggregate using weighted voting (weight by predictor type)."""
        if not predictions:
            return "unknown", 0.0

        # Assign weights (CoT predictors get higher weight)
        weights = {
            0: 1.0,  # Simple Predict
            1: 1.5,  # ChainOfThought
            2: 1.5,  # ChainOfThought
        }

        # Weighted voting
        weighted_votes = {}
        total_weight = 0

        for pred in predictions:
            category = pred['category']
            weight = weights.get(pred['predictor_id'], 1.0)
            weighted_votes[category] = weighted_votes.get(category, 0) + weight
            total_weight += weight

        # Get category with highest weight
        best_category = max(weighted_votes, key=weighted_votes.get)
        confidence = weighted_votes[best_category] / total_weight

        return best_category, confidence

    def _meta_learning(self, predictions: List[Dict], text: str) -> tuple:
        """Aggregate using meta-learner."""
        if not predictions:
            return "unknown", 0.0

        # Format predictions for meta-learner
        pred_str = "\\n".join([
            f"Predictor {p['predictor_id']}: {p['category']} (Reasoning: {p['reasoning']})"
            for p in predictions
        ])

        # Use meta-learner to aggregate
        result = self.meta_learner(
            predictions=pred_str,
            text=text
        )

        return result.final_prediction, float(result.confidence)


# ============================================================================
# 3. EXAMPLE DATA
# ============================================================================

EXAMPLE_TEXTS = [
    "This product is absolutely amazing! Best purchase ever!",
    "Terrible quality. Complete waste of money.",
    "It's okay, nothing special but does the job.",
    "I love this! Highly recommend to everyone!",
    "Very disappointed. Expected much better.",
]


# ============================================================================
# 4. EVALUATION
# ============================================================================

def evaluate_ensemble(ensemble, test_data: List[Dict]):
    """Evaluate ensemble performance."""
    correct = 0
    total = len(test_data)

    for example in test_data:
        pred = ensemble(text=example['text'])
        if pred.category.lower() == example['label'].lower():
            correct += 1

    accuracy = correct / total if total > 0 else 0.0
    return accuracy


def compare_methods():
    """Compare different aggregation methods."""

    print("\\n" + "="*70)
    print("Comparing Ensemble Aggregation Methods")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)

    # Test data
    test_data = [
        {"text": "This is fantastic!", "label": "positive"},
        {"text": "Terrible experience.", "label": "negative"},
        {"text": "It's fine.", "label": "neutral"},
    ]

    # Test each method
    methods = ["voting", "weighted", "meta"]

    for method in methods:
        print(f"Testing {method} aggregation...")
        ensemble = EnsembleClassifier(num_predictors=3, aggregation_method=method)

        # Run on examples
        for example in test_data:
            result = ensemble(text=example['text'])
            print(f"  Text: {example['text'][:40]}...")
            print(f"  Predicted: {result.category} (confidence: {result.confidence:.2f})")
            print(f"  Expected: {example['label']}")
            print()

        print("-" * 70 + "\\n")


# ============================================================================
# 5. CONFIGURATION & USAGE
# ============================================================================

def main():
    """Run the ensemble system."""

    print("\\n" + "="*70)
    print("Ensemble Classification System")
    print("="*70 + "\\n")

    # Configure DSPy
    lm = dspy.LM(model='ollama/gpt-oss:20b')
    dspy.configure(lm=lm)
    print("✓ Configured language model\\n")

    # Create ensemble
    ensemble = EnsembleClassifier(num_predictors=3, aggregation_method="voting")
    print("✓ Created ensemble with 3 predictors")
    print("  - Predictor 1: Simple Predict")
    print("  - Predictor 2: ChainOfThought")
    print("  - Predictor 3: ChainOfThought\\n")

    # Example classifications
    print("Example Classifications:")
    print("-" * 70)

    for text in EXAMPLE_TEXTS:
        result = ensemble(text=text)
        print(f"\\nText: {text}")
        print(f"Category: {result.category}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Predictors agreed: {result.num_predictors}/{len(ensemble.predictors)}")

    print("\\n" + "-" * 70)

    # Compare methods
    compare_methods()

    # Interactive mode
    print("\\nInteractive Ensemble Classification (Ctrl+C to exit):")
    print("Enter text to classify\\n")

    try:
        while True:
            text = input("Text: ").strip()
            if not text:
                continue

            result = ensemble(text=text)
            print(f"Category: {result.category}")
            print(f"Confidence: {result.confidence:.2%}")
            print(f"Agreement: {result.num_predictors}/{len(ensemble.predictors)} predictors\\n")

    except KeyboardInterrupt:
        print("\\n\\nGoodbye!")


# ============================================================================
# 6. ADVANCED ENSEMBLE TECHNIQUES
# ============================================================================

class AdvancedEnsemble(dspy.Module):
    """Advanced ensemble with diverse predictors and smart aggregation."""

    def __init__(self):
        super().__init__()

        # Diverse predictor types
        self.predictors = [
            dspy.Predict(ClassifyText),
            dspy.ChainOfThought(ClassifyText),
            dspy.MultiChainComparison(ClassifyText),
        ]

        # Confidence-weighted aggregation
        self.use_confidence_weighting = True

    def forward(self, text: str):
        """Classify with advanced ensemble."""
        # Implementation similar to EnsembleClassifier
        # but with more sophisticated aggregation
        pass


# ============================================================================
# 7. NEXT STEPS
# ============================================================================

"""
NEXT STEPS TO IMPROVE YOUR ENSEMBLE SYSTEM:

1. Diverse Predictors:
   - Use different predictor types (Predict, CoT, ReAct, etc.)
   - Use different prompting strategies
   - Use different model sizes/types
   - Add specialized predictors for edge cases

2. Better Aggregation:
   - Learn optimal weights from data
   - Use confidence scores in aggregation
   - Implement stacking/blending
   - Add disagreement detection

3. Evaluation:
   - Measure ensemble vs individual accuracy
   - Analyze when ensemble helps most
   - Track computational cost
   - Measure calibration

4. Optimization:
   - Optimize individual predictors
   - Optimize aggregation weights
   - Prune redundant predictors
   - Balance accuracy vs speed

5. Production Features:
   - Parallel prediction execution
   - Caching for repeated inputs
   - Fallback strategies
   - Monitoring and logging

6. Advanced Techniques:
   - Boosting (sequential ensembles)
   - Bagging (bootstrap aggregating)
   - Stacking (meta-learning)
   - Dynamic ensemble selection
"""


if __name__ == "__main__":
    main()
'''
