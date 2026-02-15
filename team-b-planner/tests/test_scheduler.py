from backend.app.core.loader import load_problems
from backend.app.core.scheduler import generate_plan


def test_generate_plan_basic():

    problems = load_problems("backend/data/problems.json")

    plan = generate_plan(problems, 60, 3, 7)

    assert len(plan) > 0


def test_time_limit():

    problems = load_problems("backend/data/problems.json")

    plan = generate_plan(problems, 30, 1, 10)

    total = sum(p["duration"] for p in plan)

    assert total <= 30


def test_difficulty_range():

    problems = load_problems("backend/data/problems.json")

    plan = generate_plan(problems, 90, 4, 6)

    for p in plan:
        assert 4 <= p["difficulty"] <= 6


def test_empty_result():

    problems = load_problems("backend/data/problems.json")

    plan = generate_plan(problems, 60, 20, 30)

    assert plan == []
