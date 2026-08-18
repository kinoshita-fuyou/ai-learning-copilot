"""Pure-Python BM25 keyword scoring for hybrid retrieval.

Complements the hashing-vector retrieval: BM25 rewards exact keyword overlap
with IDF weighting, while the vector score captures token co-occurrence.
Keeping it dependency-free keeps the whole demo offline and reproducible.
"""

import math
from collections import Counter

from app.embeddings import tokenize


K1 = 1.5
B = 0.75


class BM25Index:
    """In-memory BM25 index over a list of documents."""

    def __init__(self, documents: list[str]) -> None:
        self.documents = documents
        self.doc_count = len(documents)
        self.doc_lengths = [len(tokenize(document)) for document in documents]
        self.avgdl = sum(self.doc_lengths) / max(self.doc_count, 1)
        self.document_frequency: Counter[str] = Counter()
        self.term_frequencies: list[Counter[str]] = []
        for document in documents:
            frequencies = Counter(tokenize(document))
            self.term_frequencies.append(frequencies)
            self.document_frequency.update(frequencies.keys())

    def idf(self, term: str) -> float:
        """IDF with smoothing, never negative."""
        docs_with_term = self.document_frequency.get(term, 0)
        return math.log(1 + (self.doc_count - docs_with_term + 0.5) / (docs_with_term + 0.5))

    def score(self, query: str, document_index: int) -> float:
        query_terms = set(tokenize(query))
        if not query_terms:
            return 0.0
        document_length = self.doc_lengths[document_index]
        frequencies = self.term_frequencies[document_index]
        total = 0.0
        for term in query_terms:
            frequency = frequencies.get(term, 0)
            if frequency == 0:
                continue
            length_norm = K1 * (1 - B + B * document_length / max(self.avgdl, 1e-9))
            total += self.idf(term) * (frequency * (K1 + 1)) / (frequency + length_norm)
        return total

    def score_all(self, query: str) -> list[float]:
        return [self.score(query, index) for index in range(self.doc_count)]
