from dataclasses import dataclass


CHUNK_SIZE = 500
CHUNK_OVERLAP = 80


@dataclass(frozen=True)
class TextChunk:
    content: str
    char_start: int
    char_end: int


def normalize_text(text: str) -> str:
    paragraphs = []
    for paragraph in text.replace("\r\n", "\n").replace("\r", "\n").split("\n\n"):
        normalized = "\n".join(" ".join(line.split()) for line in paragraph.splitlines()).strip()
        if normalized:
            paragraphs.append(normalized)
    return "\n\n".join(paragraphs)


def chunk_text(text: str) -> list[TextChunk]:
    if not text:
        return []

    chunks: list[TextChunk] = []
    start = 0
    text_length = len(text)

    while start < text_length:
        limit = min(start + CHUNK_SIZE, text_length)
        end = _find_boundary(text, start, limit)
        raw_chunk = text[start:end]
        content = raw_chunk.strip()

        if content:
            leading_whitespace = len(raw_chunk) - len(raw_chunk.lstrip())
            chunks.append(
                TextChunk(
                    content=content,
                    char_start=start + leading_whitespace,
                    char_end=start + leading_whitespace + len(content),
                )
            )

        if end >= text_length:
            break
        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def _find_boundary(text: str, start: int, limit: int) -> int:
    if limit == len(text):
        return limit

    minimum_boundary = start + CHUNK_SIZE // 2
    paragraph_boundary = text.rfind("\n\n", minimum_boundary, limit)
    if paragraph_boundary != -1:
        return paragraph_boundary + 2

    sentence_boundary = max(
        text.rfind(marker, minimum_boundary, limit)
        for marker in ("。", "！", "？", ". ", "! ", "? ")
    )
    if sentence_boundary != -1:
        return sentence_boundary + 1

    return limit
