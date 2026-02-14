from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
from .preprocess import preprocess_text


class TextVectorizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            preprocessor=preprocess_text,
            stop_words="english"
        )
        self.fitted = False

    def fit(self, documents: List[str]):
        if not documents:
            raise ValueError("Document list cannot be empty")
        self.vectorizer.fit(documents)
        self.fitted = True

    def transform(self, documents: List[str]):
        if not self.fitted:
            raise RuntimeError("Vectorizer must be fitted before transform")
        return self.vectorizer.transform(documents)

    def fit_transform(self, documents: List[str]):
        if not documents:
            raise ValueError("Document list cannot be empty")
        self.fitted = True
        return self.vectorizer.fit_transform(documents)
