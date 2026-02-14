from backend.app.core.preprocess import preprocess_text


def test_preprocess_lowercase_and_punctuation():
    assert preprocess_text("Hello!!!") == "hello"


def test_preprocess_numbers_kept():
    assert preprocess_text("DSA 101!!!") == "dsa 101"


def test_preprocess_empty_string():
    assert preprocess_text("") == ""


def test_preprocess_none_input():
    assert preprocess_text(None) == ""
