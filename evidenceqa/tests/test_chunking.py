from app.chunking import CHUNK_SIZE, chunk_text, normalize_text


def test_normalize_text_removes_empty_lines_and_extra_spaces() -> None:
    text = "\n  First   paragraph.  \n\n\n Second\tparagraph. \n"

    assert normalize_text(text) == "First paragraph.\n\nSecond paragraph."


def test_chunk_text_prefers_paragraph_boundary_and_keeps_offsets() -> None:
    text = ("A" * (CHUNK_SIZE - 30)) + "\n\n" + ("B" * 120)

    chunks = chunk_text(text)

    assert len(chunks) == 2
    assert chunks[0].content.endswith("A")
    assert chunks[1].content.startswith("A")
    assert chunks[0].char_start == 0
    assert chunks[0].char_end == len(chunks[0].content)
