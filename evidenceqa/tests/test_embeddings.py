import math

from app.embeddings import HashingEmbedder, cosine_similarity, tokenize


def test_embed_is_deterministic_and_normalized() -> None:
    embedder = HashingEmbedder()

    first = embedder.embed("员工报销需要提前审批")
    second = embedder.embed("员工报销需要提前审批")

    assert first == second
    assert math.isclose(math.sqrt(sum(v * v for v in first)), 1.0)


def test_related_texts_score_higher_than_unrelated() -> None:
    embedder = HashingEmbedder()

    expense = embedder.embed("差旅报销流程需要部门主管审批")
    similar = embedder.embed("报销审批流程说明")
    unrelated = embedder.embed("office wifi password reset guide")

    related_score = cosine_similarity(expense, similar)
    unrelated_score = cosine_similarity(expense, unrelated)
    assert related_score > unrelated_score


def test_tokenize_adds_cjk_bigrams() -> None:
    assert "报销" in tokenize("报销流程")
