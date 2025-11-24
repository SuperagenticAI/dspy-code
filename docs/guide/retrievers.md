# DSPy Retrievers Guide

Retrievers in DSPy enable RAG (Retrieval-Augmented Generation) by finding relevant documents or passages to provide context for your language model. This guide covers all retriever types and how to use them.

## What are Retrievers?

Retrievers find and return relevant documents or passages based on a query. They are essential for:

- **RAG Systems** - Providing context from knowledge bases
- **Document Q&A** - Answering questions over documents
- **Information Retrieval** - Finding relevant information quickly
- **Knowledge Grounding** - Reducing hallucinations by grounding in facts

## Available Retriever Types

DSPy Code supports three main retriever approaches:

### 1. ColBERTv2 (Recommended for Production)

State-of-the-art neural retrieval model for semantic search.

**When to use:**
- Production RAG systems
- High-quality retrieval needed
- Semantic search requirements
- Large document collections

**Features:**
- ✅ State-of-the-art quality
- ✅ Fast retrieval with pre-computed indexes
- ✅ Production-ready and scalable
- ✅ Better than simple keyword search

**Example:**

```python
import dspy

# Configure ColBERTv2 retriever
colbertv2_retriever = dspy.ColBERTv2(
    url='http://20.102.90.50:2017/wiki17_abstracts'  # Public server
    # Or your own: url='http://localhost:8893/api/search'
)

# Configure DSPy to use ColBERTv2
dspy.configure(rm=colbertv2_retriever)

# Create retriever module
retriever = dspy.Retrieve(k=5)  # Retrieve top 5 passages

# Use retriever
query = "What is machine learning?"
results = retriever(query)

print(f"Retrieved {len(results.passages)} passages:")
for passage in results.passages:
    print(f"  - {passage[:100]}...")
```

**Setting up your own ColBERTv2 server:**

```bash
# Install ColBERTv2
pip install colbert-ai

# Index your documents
python -m colbert.index --documents your_docs.jsonl --index your_index

# Start the server
python -m colbert.serve --index your_index --port 8893
```

### 2. Custom Retriever

Build your own retriever for domain-specific needs.

**When to use:**
- Custom retrieval logic needed
- Domain-specific search requirements
- Prototyping and experimentation
- Integration with existing systems

**Example - Keyword-Based Retriever:**

```python
import dspy
from typing import List, Dict, Any

class KeywordRetriever:
    """Simple keyword-based retriever."""

    def __init__(self, documents: List[Dict[str, Any]]):
        self.documents = documents

    def __call__(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents based on keyword matching."""
        query_words = set(query.lower().split())

        # Score documents by keyword overlap
        scored_docs = []
        for doc in self.documents:
            doc_text = doc.get('text', '').lower()
            doc_words = set(doc_text.split())
            score = len(query_words & doc_words)

            if score > 0:
                scored_docs.append((score, doc))

        # Sort by score and return top k
        scored_docs.sort(reverse=True, key=lambda x: x[0])
        return [doc for _, doc in scored_docs[:k]]

# Use custom retriever
documents = [
    {"text": "DSPy is a framework for programming with foundation models.", "id": 1},
    {"text": "ColBERTv2 provides neural retrieval capabilities.", "id": 2},
]

retriever = KeywordRetriever(documents)
results = retriever("What is DSPy?", k=2)
```

**Example - Semantic Retriever:**

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticRetriever:
    """Semantic retriever using embeddings."""

    def __init__(self, documents: List[str], embedding_model=None):
        self.documents = documents

        if embedding_model is None:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        else:
            self.embedding_model = embedding_model

        # Pre-compute document embeddings
        self.doc_embeddings = self.embedding_model.encode(documents)

    def __call__(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents using semantic similarity."""
        # Embed query
        query_embedding = self.embedding_model.encode([query])[0]

        # Compute similarity scores
        scores = []
        for i, doc_emb in enumerate(self.doc_embeddings):
            similarity = np.dot(query_embedding, doc_emb) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb)
            )
            scores.append((similarity, self.documents[i]))

        # Sort by similarity and return top k
        scores.sort(reverse=True, key=lambda x: x[0])
        return [{"text": doc, "score": score} for score, doc in scores[:k]]
```

### 3. Embeddings Retriever

Vector-based retrieval using embeddings and vector databases.

**When to use:**
- Vector databases (FAISS, Chroma, Pinecone)
- Embedding-based search
- Large document collections
- Scalable retrieval needs

**Example - FAISS Retriever:**

```python
import dspy
import faiss
from sentence_transformers import SentenceTransformer

class FAISSRetriever:
    """FAISS-based vector retriever."""

    def __init__(self, documents: List[str]):
        self.documents = documents
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Generate embeddings
        embeddings = self.embedding_model.encode(documents)

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))

    def __call__(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents for query."""
        # Embed query
        query_embedding = self.embedding_model.encode([query])

        # Search in FAISS
        distances, indices = self.index.search(query_embedding.astype('float32'), k)

        # Return results
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                results.append({
                    "text": self.documents[idx],
                    "score": float(dist),
                    "index": int(idx)
                })

        return results

# Use FAISS retriever
documents = [
    "DSPy is a framework for programming with foundation models.",
    "ColBERTv2 provides neural retrieval capabilities.",
    "RAG combines retrieval with generation.",
]

retriever = FAISSRetriever(documents)
results = retriever("What is DSPy?", k=2)
```

**Example - Chroma Retriever:**

```python
import chromadb

class ChromaRetriever:
    """Chroma-based vector retriever."""

    def __init__(self, documents: List[Dict[str, Any]], collection_name="documents"):
        import chromadb
        from chromadb.config import Settings

        # Initialize Chroma client
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./chroma_db"
        ))

        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # Add documents if collection is empty
        if self.collection.count() == 0:
            texts = [doc.get('text', '') for doc in documents]
            ids = [doc.get('id', str(i)) for i, doc in enumerate(documents)]
            metadatas = [doc.get('metadata', {}) for doc in documents]

            self.collection.add(
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )

    def __call__(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve documents for query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=k
        )

        # Format results
        retrieved = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                retrieved.append({
                    "text": doc,
                    "id": results['ids'][0][i] if results['ids'] else None,
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                })

        return retrieved
```

## Building RAG Systems with Retrievers

### Complete RAG Module

```python
import dspy

class RAGSignature(dspy.Signature):
    """Answer questions using retrieved context."""
    context = dspy.InputField(desc="Retrieved context passages")
    question = dspy.InputField(desc="User's question")
    answer = dspy.OutputField(desc="Answer based on context")


class RAGModule(dspy.Module):
    """RAG system using retriever."""

    def __init__(self, k=5):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought(RAGSignature)

    def forward(self, question: str):
        # Retrieve relevant passages
        retrieved = self.retrieve(question)
        context = "\n\n".join(retrieved.passages)

        # Generate answer from context
        result = self.generate(context=context, question=question)
        return result

# Configure retriever
colbertv2_retriever = dspy.ColBERTv2(url='http://localhost:8893/api/search')
dspy.configure(rm=colbertv2_retriever)

# Use RAG system
rag = RAGModule(k=5)
result = rag(question="What is DSPy?")
print(result.answer)
```

## Using Retrievers in DSPy Code

### Via Slash Commands

List all retrievers:

```bash
/retrievers
```

Get details for a specific retriever:

```bash
/retrievers colbertv2
/retrievers custom
/retrievers embeddings
```

### Via Natural Language

Ask about retrievers:

```
What is ColBERTv2?
How do I use a custom retriever?
Tell me about embeddings retrieval
```

### Via Code Generation

Request retriever usage:

```
Create a RAG system with ColBERTv2
Build a custom retriever for my documents
Generate code for FAISS-based retrieval
```

## Choosing the Right Retriever

| Retriever | Best For | Difficulty | Quality |
|-----------|----------|------------|---------|
| **ColBERTv2** | Production RAG, high quality | Intermediate | ⭐⭐⭐⭐⭐ |
| **Custom** | Domain-specific, prototyping | Advanced | ⭐⭐⭐ |
| **Embeddings** | Vector databases, scalability | Intermediate | ⭐⭐⭐⭐ |

## Best Practices

### 1. Document Indexing

- **Chunk documents** appropriately (200-500 tokens per chunk)
- **Add metadata** (source, date, author) for filtering
- **Pre-compute embeddings** for faster retrieval
- **Update indexes** regularly for fresh content

### 2. Retrieval Parameters

- **k value**: Start with 3-5 passages, adjust based on context window
- **Reranking**: Consider reranking top-k results for better quality
- **Filtering**: Use metadata filters for domain-specific retrieval

### 3. RAG Optimization

- **Context length**: Balance between context and generation tokens
- **Relevance threshold**: Filter out low-relevance passages
- **Diversity**: Ensure retrieved passages are diverse
- **Source attribution**: Track sources for citations

## Troubleshooting

### ColBERTv2 Issues

- **Server not responding**: Check server URL and port
- **Slow retrieval**: Ensure indexes are pre-computed
- **Low quality**: Try adjusting k value or reranking

### Custom Retriever Issues

- **Low relevance**: Improve scoring function or use semantic search
- **Performance**: Consider caching or pre-computing
- **Integration**: Ensure compatibility with DSPy's Retrieve module

### Embeddings Retriever Issues

- **Memory**: Use FAISS GPU or distributed indexes for large collections
- **Quality**: Try different embedding models (e.g., sentence-transformers)
- **Index updates**: Rebuild index when documents change

## Next Steps

- Learn about [RAG Systems](../tutorials/rag-system.md) for complete examples
- Explore [Optimization](optimization.md) to improve retrieval quality
- Check [Evaluation](evaluation.md) to measure retrieval performance
- See [Complete Programs](../tutorials/sentiment-analyzer.md) for full examples

## Additional Resources

- [DSPy Retrievers Documentation](https://dspy-docs.vercel.app/docs/building-blocks/retrievers)
- Use `/retrievers` in the CLI to see all available retrievers
- Use `/explain retriever` for detailed explanations
