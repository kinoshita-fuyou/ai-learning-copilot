"""Deterministic local text embeddings.

Uses the feature-hashing trick so the project runs fully offline without an
API key. ``HashingEmbedder.embed`` mirrors hosted embedding APIs, so a remote
provider can be swapped in later without touching the retrieval code.
"""

import hashlib
import math
import re


TOKEN_PATTERN = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    tokens = TOKEN_PATTERN.findall(text.lower())
    cjk_chars = [token for token in tokens if len(token) == 1 and "\u4e00" <= token <= "\u9fff"]
    bigrams = [left + right for left, right in zip(cjk_chars, cjk_chars[1:])]
    return tokens + bigrams


class HashingEmbedder:
    def __init__(self, dimensions: int = 512) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            vector[int.from_bytes(digest, "little") % self.dimensions] += 1.0
        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
