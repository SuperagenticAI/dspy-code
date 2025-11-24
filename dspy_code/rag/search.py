"""
Code search functionality for the RAG system.

This module implements multiple search strategies (TF-IDF, keyword, hybrid)
for finding relevant code elements in the indexed codebase.
"""

import logging
import re

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn not available, using fallback search")

from .models import CodeElement, CodeIndex, SearchResult

logger = logging.getLogger(__name__)


class CodeSearch:
    """Search indexed code using multiple strategies.

    Supports TF-IDF semantic search, keyword search, and hybrid approaches.
    Falls back to simple keyword matching if scikit-learn is not available.
    """

    def __init__(self, index: CodeIndex, use_tfidf: bool = True):
        """Initialize search with code index.

        Args:
            index: CodeIndex to search
            use_tfidf: Whether to use TF-IDF (requires scikit-learn)
        """
        self.index = index
        self.use_tfidf = use_tfidf and SKLEARN_AVAILABLE

        # Build search structures
        self.vectorizer = None
        self.tfidf_matrix = None
        self.element_texts = []

        if self.use_tfidf:
            self._build_tfidf_index()

        # Cache for frequent queries
        self.query_cache: dict[str, list[SearchResult]] = {}

        logger.info(
            f"CodeSearch initialized with {len(index.elements)} elements, TF-IDF: {self.use_tfidf}"
        )

    def _build_tfidf_index(self) -> None:
        """Build TF-IDF index for semantic search."""
        if not SKLEARN_AVAILABLE:
            logger.warning("scikit-learn not available, skipping TF-IDF index")
            return

        try:
            # Build text corpus from code elements
            self.element_texts = []
            for elem in self.index.elements:
                # Combine name, docstring, and signature for better matching
                text_parts = [elem.name]

                if elem.docstring:
                    text_parts.append(elem.docstring)

                text_parts.append(elem.signature)

                # Add some code context (first few lines)
                code_lines = elem.code.split("\n")[:5]
                text_parts.extend(code_lines)

                text = " ".join(text_parts)
                self.element_texts.append(text)

            # Build TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000, stop_words="english", ngram_range=(1, 2), min_df=1
            )

            self.tfidf_matrix = self.vectorizer.fit_transform(self.element_texts)

            logger.info(f"TF-IDF index built: {self.tfidf_matrix.shape}")

        except Exception as e:
            logger.error(f"Failed to build TF-IDF index: {e}")
            self.use_tfidf = False

    def semantic_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Semantic search using TF-IDF.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of SearchResult ordered by relevance
        """
        if not self.use_tfidf or self.vectorizer is None:
            # Fall back to keyword search
            return self.keyword_search(query, top_k)

        try:
            # Transform query
            query_vec = self.vectorizer.transform([query])

            # Compute cosine similarity
            similarities = cosine_similarity(query_vec, self.tfidf_matrix)[0]

            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]

            # Build results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:  # Only include non-zero scores
                    results.append(
                        SearchResult(
                            element=self.index.elements[idx],
                            score=float(similarities[idx]),
                            match_type="semantic",
                            matched_terms=self._extract_matched_terms(
                                query, self.element_texts[idx]
                            ),
                        )
                    )

            return results

        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return self.keyword_search(query, top_k)

    def keyword_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Keyword-based search (fallback when TF-IDF unavailable).

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of SearchResult ordered by relevance
        """
        # Extract keywords from query
        keywords = self._extract_keywords(query)

        if not keywords:
            return []

        # Score each element
        scored_elements = []
        for elem in self.index.elements:
            score = self._score_element_keywords(elem, keywords)
            if score > 0:
                scored_elements.append((elem, score, keywords))

        # Sort by score and take top-k
        scored_elements.sort(key=lambda x: x[1], reverse=True)

        results = []
        for elem, score, matched_terms in scored_elements[:top_k]:
            results.append(
                SearchResult(
                    element=elem, score=score, match_type="keyword", matched_terms=matched_terms
                )
            )

        return results

    def hybrid_search(self, query: str, top_k: int = 5) -> list[SearchResult]:
        """Hybrid search combining semantic and keyword approaches.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of SearchResult ordered by relevance
        """
        # Check cache first
        cache_key = f"hybrid:{query}:{top_k}"
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        if self.use_tfidf:
            # Get results from both methods
            semantic_results = self.semantic_search(query, top_k * 2)
            keyword_results = self.keyword_search(query, top_k * 2)

            # Combine and re-rank
            combined = self._combine_results(semantic_results, keyword_results)
            results = self.rank_results(combined, query)[:top_k]
        else:
            # Fall back to keyword only
            results = self.keyword_search(query, top_k)

        # Cache results
        self.query_cache[cache_key] = results

        return results

    def _combine_results(
        self, semantic: list[SearchResult], keyword: list[SearchResult]
    ) -> list[SearchResult]:
        """Combine results from multiple search strategies."""
        # Use dict to deduplicate by element name
        combined_dict: dict[str, SearchResult] = {}

        # Add semantic results
        for result in semantic:
            key = f"{result.element.codebase}:{result.element.name}"
            combined_dict[key] = result

        # Add keyword results, boosting score if already present
        for result in keyword:
            key = f"{result.element.codebase}:{result.element.name}"
            if key in combined_dict:
                # Boost score for elements found by both methods
                existing = combined_dict[key]
                existing.score = (existing.score + result.score) / 2 * 1.5
                existing.match_type = "hybrid"
                existing.matched_terms = list(set(existing.matched_terms + result.matched_terms))
            else:
                combined_dict[key] = result

        return list(combined_dict.values())

    def rank_results(self, results: list[SearchResult], query: str) -> list[SearchResult]:
        """Re-rank results by relevance.

        Args:
            results: List of search results
            query: Original query

        Returns:
            Re-ranked results
        """
        query_lower = query.lower()

        for result in results:
            elem = result.element

            # Boost score based on various factors
            boost = 1.0

            # Exact name match
            if query_lower == elem.name.lower():
                boost *= 2.0
            elif query_lower in elem.name.lower():
                boost *= 1.5

            # Docstring match
            if elem.docstring and query_lower in elem.docstring.lower():
                boost *= 1.3

            # Prefer classes and functions over methods
            if elem.type in ["class", "function"]:
                boost *= 1.2

            # Prefer dspy and dspy_cli over other codebases
            if elem.codebase in ["dspy", "dspy_cli"]:
                boost *= 1.1

            result.score *= boost

        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)

        return results

    def _extract_keywords(self, query: str) -> list[str]:
        """Extract keywords from query."""
        # Remove common words and split
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
            "from",
            "as",
            "is",
            "was",
            "are",
            "were",
            "be",
            "how",
            "do",
            "does",
            "i",
            "you",
            "use",
            "using",
            "create",
            "make",
        }

        # Split on non-alphanumeric and convert to lowercase
        words = re.findall(r"\w+", query.lower())

        # Filter stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 2]

        return keywords

    def _extract_matched_terms(self, query: str, text: str) -> list[str]:
        """Extract terms from query that appear in text."""
        keywords = self._extract_keywords(query)
        text_lower = text.lower()

        matched = [kw for kw in keywords if kw in text_lower]
        return matched

    def _score_element_keywords(self, elem: CodeElement, keywords: list[str]) -> float:
        """Score an element based on keyword matches."""
        score = 0.0

        # Check name (highest weight)
        name_lower = elem.name.lower()
        for keyword in keywords:
            if keyword in name_lower:
                score += 3.0

        # Check docstring
        if elem.docstring:
            docstring_lower = elem.docstring.lower()
            for keyword in keywords:
                if keyword in docstring_lower:
                    score += 2.0

        # Check signature
        signature_lower = elem.signature.lower()
        for keyword in keywords:
            if keyword in signature_lower:
                score += 1.5

        # Check code (lower weight)
        code_lower = elem.code.lower()
        for keyword in keywords:
            if keyword in code_lower:
                score += 0.5

        return score

    def search_by_name(self, name: str, exact: bool = False) -> list[SearchResult]:
        """Search for elements by name.

        Args:
            name: Name to search for
            exact: Whether to require exact match

        Returns:
            List of matching elements
        """
        results = []
        name_lower = name.lower()

        for elem in self.index.elements:
            elem_name_lower = elem.name.lower()

            if exact:
                if elem_name_lower == name_lower:
                    results.append(
                        SearchResult(
                            element=elem, score=1.0, match_type="exact", matched_terms=[name]
                        )
                    )
            elif name_lower in elem_name_lower:
                # Score based on how close the match is
                score = len(name) / len(elem.name)
                results.append(
                    SearchResult(element=elem, score=score, match_type="name", matched_terms=[name])
                )

        results.sort(key=lambda x: x.score, reverse=True)
        return results

    def search_by_type(
        self, element_type: str, query: str | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        """Search for elements of a specific type.

        Args:
            element_type: Type to search for ('function', 'class', 'method')
            query: Optional query to filter results
            top_k: Number of results to return

        Returns:
            List of matching elements
        """
        # Filter by type
        typed_elements = [elem for elem in self.index.elements if elem.type == element_type]

        if not query:
            # Return all of this type
            results = [
                SearchResult(element=elem, score=1.0, match_type="type", matched_terms=[])
                for elem in typed_elements[:top_k]
            ]
            return results

        # Search within typed elements
        keywords = self._extract_keywords(query)
        scored = []

        for elem in typed_elements:
            score = self._score_element_keywords(elem, keywords)
            if score > 0:
                scored.append((elem, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = [
            SearchResult(element=elem, score=score, match_type="type", matched_terms=keywords)
            for elem, score in scored[:top_k]
        ]

        return results

    def search_by_codebase(
        self, codebase: str, query: str | None = None, top_k: int = 5
    ) -> list[SearchResult]:
        """Search within a specific codebase.

        Args:
            codebase: Codebase to search in
            query: Optional query to filter results
            top_k: Number of results to return

        Returns:
            List of matching elements
        """
        # Filter by codebase
        codebase_elements = [elem for elem in self.index.elements if elem.codebase == codebase]

        if not query:
            # Return all from this codebase
            results = [
                SearchResult(element=elem, score=1.0, match_type="codebase", matched_terms=[])
                for elem in codebase_elements[:top_k]
            ]
            return results

        # Search within codebase elements
        keywords = self._extract_keywords(query)
        scored = []

        for elem in codebase_elements:
            score = self._score_element_keywords(elem, keywords)
            if score > 0:
                scored.append((elem, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = [
            SearchResult(element=elem, score=score, match_type="codebase", matched_terms=keywords)
            for elem, score in scored[:top_k]
        ]

        return results

    def clear_cache(self) -> None:
        """Clear the query cache."""
        self.query_cache.clear()
        logger.debug("Search cache cleared")
