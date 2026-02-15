from backend.app.core.difficulty import update_difficulty


def test_too_easy():
    assert update_difficulty(5, "too_easy") == 6


def test_too_hard():
    assert update_difficulty(5, "too_hard") == 4


def test_just_right():
    assert update_difficulty(5, "just_right") == 5


def test_max_limit():
    assert update_difficulty(10, "too_easy") == 10


def test_min_limit():
    assert update_difficulty(1, "too_hard") == 1
