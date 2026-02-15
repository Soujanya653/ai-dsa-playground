"""
Enhanced practice plan scheduler module.

Implements intelligent scheduling with:
- Personalized difficulty adjustment
- Topic mastery tracking
- Spaced repetition
- Performance-based recommendations
"""

import heapq
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def calculate_personalized_difficulty(
    base_difficulty: int,
    user_profile: Dict,
    problem_id: int,
) -> float:
    """
    Calculate personalized difficulty based on user's history.

    Args:
        base_difficulty: Problem's base difficulty (1-10).
        user_profile: User's performance profile.
        problem_id: Problem identifier.

    Returns:
        Adjusted difficulty score (float).
    """
    # Get user's difficulty adjustments
    adjustments = user_profile.get("difficulty_adjustments", {})
    personal_diff = adjustments.get(str(problem_id), base_difficulty)

    # Get user's problem history
    history = user_profile.get("problem_history", {})
    problem_stats = history.get(str(problem_id), {})

    # Factor in success rate
    attempts = problem_stats.get("attempts", 0)
    successes = problem_stats.get("successes", 0)

    if attempts > 0:
        success_rate = successes / attempts
        # If user consistently succeeds, increase difficulty
        if success_rate > 0.8 and attempts >= 2:
            personal_diff += 0.5
        # If user struggles, decrease difficulty
        elif success_rate < 0.4 and attempts >= 2:
            personal_diff -= 0.5

    return max(1.0, min(10.0, personal_diff))


def calculate_topic_priority(
    topic: str,
    user_profile: Dict,
    topic_count: Dict[str, int],
) -> float:
    """
    Calculate priority score for a topic based on user mastery.

    Args:
        topic: Topic name.
        user_profile: User's performance profile.
        topic_count: Current topic distribution in plan.

    Returns:
        Priority score (lower is better).
    """
    topic_mastery = user_profile.get("topic_mastery", {})
    mastery_level = topic_mastery.get(topic, 0.0)  # 0.0 to 1.0

    # Prioritize topics with lower mastery (need more practice)
    mastery_penalty = mastery_level * 2.0

    # Penalize overrepresented topics in current plan
    balance_penalty = topic_count.get(topic, 0) * 1.5

    # Check when user last practiced this topic
    last_practiced = user_profile.get("topic_last_seen", {}).get(topic)
    recency_bonus = 0.0

    if last_practiced:
        days_since = (datetime.now() - datetime.fromisoformat(last_practiced)).days
        # Spaced repetition: bonus for topics not seen in 2-7 days
        if 2 <= days_since <= 7:
            recency_bonus = -1.0  # Negative to increase priority
        elif days_since > 14:
            recency_bonus = -2.0  # Higher priority for long-unseen topics

    return mastery_penalty + balance_penalty + recency_bonus


def calculate_time_estimate(
    base_duration: int,
    user_profile: Dict,
    problem_id: int,
) -> int:
    """
    Estimate actual time needed based on user's speed.

    Args:
        base_duration: Problem's base duration.
        user_profile: User's performance profile.
        problem_id: Problem identifier.

    Returns:
        Estimated duration in minutes.
    """
    # Get user's average speed multiplier
    speed_factor = user_profile.get("speed_factor", 1.0)

    # Check if user has solved this specific problem before
    history = user_profile.get("problem_history", {})
    problem_stats = history.get(str(problem_id), {})

    if problem_stats.get("avg_time"):
        # Use actual historical time
        return int(problem_stats["avg_time"] * 1.1)  # Add 10% buffer

    # Otherwise, use general speed factor
    return int(base_duration * speed_factor)


def get_diversity_bonus(
    problem: Dict,
    selected_topics: set,
) -> float:
    """
    Calculate bonus for topic diversity.

    Args:
        problem: Problem dictionary.
        selected_topics: Set of already selected topics.

    Returns:
        Diversity bonus (negative to increase priority).
    """
    new_topics = set(problem["topics"]) - selected_topics
    return -0.5 * len(new_topics)  # Bonus for introducing new topics


def generate_plan(
    problems: List[Dict],
    time_limit: int,
    min_d: int,
    max_d: int,
    user_profile: Optional[Dict] = None,
) -> List[Dict]:
    """
    Generate a personalized daily practice plan.

    Uses heap-based greedy algorithm with:
    - Personalized difficulty adjustment
    - Topic mastery tracking
    - Spaced repetition
    - Time estimation based on user speed

    Args:
        problems: List of problem dictionaries.
        time_limit: Daily time budget in minutes.
        min_d: Minimum difficulty.
        max_d: Maximum difficulty.
        user_profile: User's performance data (optional).

    Returns:
        List of selected problems with personalized metadata.

    Raises:
        ValueError: If time_limit is invalid.
    """
    if time_limit <= 0:
        raise ValueError("Time limit must be positive")

    # Initialize user profile if not provided
    if user_profile is None:
        user_profile = {
            "difficulty_adjustments": {},
            "topic_mastery": {},
            "problem_history": {},
            "speed_factor": 1.0,
            "topic_last_seen": {},
        }

    heap = []
    topic_count = {}
    selected_topics = set()

    # Calculate user's current skill level
    adjustments = user_profile.get("difficulty_adjustments", {})
    if adjustments:
        avg_adjusted_diff = sum(adjustments.values()) / len(adjustments)
        skill_level = avg_adjusted_diff
    else:
        skill_level = (min_d + max_d) / 2

    # Target difficulty: slightly above user's comfort zone (challenge zone)
    target_difficulty = min(skill_level + 0.5, max_d)

    # Build priority queue
    for p in problems:
        # Calculate personalized difficulty
        personal_diff = calculate_personalized_difficulty(
            p["difficulty"], user_profile, p["id"]
        )

        # Only include if within user's range
        if min_d <= personal_diff <= max_d:
            # Calculate topic priority
            topic_priority = sum(
                calculate_topic_priority(topic, user_profile, topic_count)
                for topic in p["topics"]
            ) / len(p["topics"])

            # Calculate difficulty match score
            diff_match = abs(personal_diff - target_difficulty)

            # Calculate diversity bonus
            diversity = get_diversity_bonus(p, selected_topics)

            # Check for spaced repetition
            last_seen = user_profile.get("problem_history", {}).get(
                str(p["id"]), {}
            ).get("last_seen")

            spaced_rep_bonus = 0.0
            if last_seen:
                days_since = (
                    datetime.now() - datetime.fromisoformat(last_seen)
                ).days
                if 3 <= days_since <= 10:
                    spaced_rep_bonus = -1.5  # Optimal review window

            # Combined score (lower is better)
            score = (
                diff_match * 2.0  # Weight difficulty match highly
                + topic_priority
                + diversity
                + spaced_rep_bonus
            )

            # Add to heap
            heapq.heappush(
                heap,
                (
                    score,
                    p["id"],  # Tiebreaker
                    p,
                    personal_diff,
                ),
            )

    plan = []
    total_time = 0

    # Greedy selection with smart time estimation
    while heap and total_time < time_limit:
        score, _, problem, personal_diff = heapq.heappop(heap)

        # Estimate actual time needed
        estimated_time = calculate_time_estimate(
            problem["duration"], user_profile, problem["id"]
        )

        if total_time + estimated_time <= time_limit:
            # Add to plan with personalized metadata
            plan_item = {
                **problem,
                "personalized_difficulty": round(personal_diff, 1),
                "estimated_time": estimated_time,
                "priority_score": round(score, 2),
            }

            plan.append(plan_item)
            total_time += estimated_time

            # Update topic tracking
            for topic in problem["topics"]:
                topic_count[topic] = topic_count.get(topic, 0) + 1
                selected_topics.add(topic)

    return plan


def generate_plan_with_recommendations(
    problems: List[Dict],
    time_limit: int,
    min_d: int,
    max_d: int,
    user_profile: Optional[Dict] = None,
) -> Tuple[List[Dict], Dict]:
    """
    Generate plan with additional recommendations.

    Returns:
        Tuple of (plan, recommendations) where recommendations include:
        - Weak topics to focus on
        - Suggested difficulty adjustment
        - Learning velocity trends
    """
    plan = generate_plan(problems, time_limit, min_d, max_d, user_profile)

    if user_profile is None:
        return plan, {"message": "Build your profile by completing problems!"}

    # Analyze weak topics
    topic_mastery = user_profile.get("topic_mastery", {})
    weak_topics = sorted(
        [(topic, mastery) for topic, mastery in topic_mastery.items()],
        key=lambda x: x[1],
    )[:3]

    # Calculate learning velocity
    history = user_profile.get("problem_history", {})
    recent_performance = []

    for prob_id, stats in history.items():
        if stats.get("last_seen"):
            recent_performance.append(
                {
                    "date": stats["last_seen"],
                    "success": stats.get("successes", 0) > 0,
                }
            )

    # Calculate total time from plan
    total_time = sum(p.get("estimated_time", p.get("duration", 0)) for p in plan)

    # Calculate current skill level safely
    adjustments = user_profile.get("difficulty_adjustments", {})
    if adjustments:
        current_skill = round(sum(adjustments.values()) / len(adjustments), 1)
    else:
        current_skill = round((min_d + max_d) / 2, 1)  # Default to mid-range

    recommendations = {
        "weak_topics": [
            {"topic": t, "mastery": round(m * 100, 1)} for t, m in weak_topics
        ],
        "current_skill_level": current_skill,
        "total_problems_solved": len(history),
        "plan_efficiency": f"{total_time}/{time_limit} minutes",
    }

    return plan, recommendations