import pytest
from app.core.vectorizer import TextVectorizer

def test_vectorizer_fit_and_transform():
    docs = [
        "find longest subarray",
        "binary search in sorted array"
    ]

    vectorizer = TextVectorizer()
    vectorizer.fit(docs)
    vectors = vectorizer.transform(["longest array"])

    print("Vector shape:", vectors.shape)
    print("Vector values:", vectors.toarray())

    assert vectors.shape[0] == 1

def test_vectorizer_without_fit():
    vectorizer = TextVectorizer()
    with pytest.raises(RuntimeError):
        vectorizer.transform(["test"])
