from typing import List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


def compute_cosine_similarity(
    query_vector,
    doc_vectors,
    top_k: int = 5
) -> List[Tuple[int, float]]:
    """
    Compute cosine similarity between a query vector and document vectors.

    Args:
        query_vector: TF-IDF vector of shape (1, n_features)
        doc_vectors: TF-IDF matrix of shape (n_docs, n_features)
        top_k: Number of top similar documents to return

    Returns:
        List of (document_index, similarity_score) sorted by score descending
    """
    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    if query_vector.shape[0] != 1:
        raise ValueError("query_vector must have shape (1, n_features)")

    similarities = cosine_similarity(query_vector, doc_vectors)[0]

    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [(int(i), float(similarities[i])) for i in top_indices]
