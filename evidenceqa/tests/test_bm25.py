from app.bm25 import BM25Index


DOCUMENTS = [
    "差旅报销发票需要在三十天内提交，超过五百元需要消费说明。",
    "远程办公需要提前一周申请并填写审批表。",
    "公司 Wi-Fi 密码每季度更换一次。",
]


def test_bm25_ranks_keyword_match_first() -> None:
    index = BM25Index(DOCUMENTS)

    scores = index.score_all("报销发票提交期限")

    assert scores[0] > scores[1]
    assert scores[0] > scores[2]


def test_bm25_penalizes_terms_common_to_all_documents() -> None:
    index = BM25Index(DOCUMENTS)

    common_idf = index.idf("一")
    rare_idf = index.idf("报销")

    assert common_idf < rare_idf
    assert rare_idf > 0


def test_bm25_empty_query_scores_zero() -> None:
    index = BM25Index(DOCUMENTS)

    assert index.score("", 0) == 0.0
    assert index.score_all("") == [0.0, 0.0, 0.0]


def test_bm25_unknown_term_scores_zero() -> None:
    index = BM25Index(DOCUMENTS)

    assert index.score("量子计算", 0) == 0.0
