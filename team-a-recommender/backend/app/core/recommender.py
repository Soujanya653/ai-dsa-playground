import json
from pathlib import Path
from typing import List, Dict

from app.core.vectorizer import TextVectorizer
from app.core.similarity import compute_cosine_similarity


class ProblemRecommender:
    def __init__(self):
        # Load problems dataset
        data_path = Path(__file__).resolve().parent.parent / "data" / "problems.json"
        with open(data_path, "r", encoding="utf-8") as f:
            self.problems = json.load(f)

        # Prepare vectorizer and fit once
        self.vectorizer = TextVectorizer()
        descriptions = [p["description"] for p in self.problems]
        self.doc_vectors = self.vectorizer.fit_transform(descriptions)

    def recommend(self, query: str, top_k: int = 5) -> List[Dict]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if top_k <= 0:
            raise ValueError("top_k must be greater than 0")

        # Vectorize query
        query_vector = self.vectorizer.transform([query])

        # Compute similarity
        results = compute_cosine_similarity(
            query_vector,
            self.doc_vectors,
            top_k=top_k
        )

        # Build response
        recommendations = []
        for idx, score in results:
            problem = self.problems[idx]
            recommendations.append({
                "id": problem["id"],
                "title": problem["title"],
                "difficulty": problem["difficulty"],
                "topics": problem["topics"],
                "score": round(score, 4)
            })

        return recommendations