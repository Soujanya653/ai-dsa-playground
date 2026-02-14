from app.core.vectorizer import TextVectorizer
from app.core.similarity import compute_cosine_similarity


def test_cosine_similarity_basic():
    documents = [
        "find longest subarray with sum",
        "binary search in sorted array",
        "depth first search traversal of tree"
    ]

    vectorizer = TextVectorizer()
    doc_vectors = vectorizer.fit_transform(documents)

    query_vector = vectorizer.transform(["longest subarray sum"])

    results = compute_cosine_similarity(query_vector, doc_vectors, top_k=2)

    # Should return exactly 2 results
    assert len(results) == 2

    # First result should be more similar than second
    assert results[0][1] >= results[1][1]


def test_cosine_similarity_invalid_top_k():
    documents = ["array problem", "graph dfs"]
    vectorizer = TextVectorizer()
    doc_vectors = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform(["array"])

    try:
        compute_cosine_similarity(query_vector, doc_vectors, top_k=0)
        assert False  # should not reach here
    except ValueError:
        assert True
