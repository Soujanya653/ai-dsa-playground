import pytest
from app.core.recommender import ProblemRecommender


def test_recommender_basic_query():
    recommender = ProblemRecommender()

    results = recommender.recommend(
        query="longest subarray using sliding window",
        top_k=5
    )

    assert len(results) == 5
    assert all("title" in r for r in results)
    assert all("score" in r for r in results)


def test_recommender_top_k_limit():
    recommender = ProblemRecommender()

    results = recommender.recommend(
        query="binary search sorted array",
        top_k=3
    )

    assert len(results) == 3


def test_recommender_empty_query_raises_error():
    recommender = ProblemRecommender()

    with pytest.raises(ValueError):
        recommender.recommend(query="", top_k=5)


def test_recommender_invalid_top_k_raises_error():
    recommender = ProblemRecommender()

    with pytest.raises(ValueError):
        recommender.recommend(query="array problem", top_k=0)