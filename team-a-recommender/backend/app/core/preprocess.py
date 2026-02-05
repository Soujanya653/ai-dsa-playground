import re


def preprocess_text(text: str) -> str:
    """
    Normalize input text by lowercasing and removing punctuation.

    Args:
        text: Raw input string.

    Returns:
        Cleaned text suitable for vectorization.
    """
    if not text:
        return ""

    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return text
