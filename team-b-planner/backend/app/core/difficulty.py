"""
Enhanced difficulty adaptation module.

Implements intelligent difficulty adjustment with:
- Exponential moving average for smooth adaptation
- Topic mastery tracking
- Performance analytics
- Multi-factor difficulty updates
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple


class DifficultyAdapter:
    """Handles difficulty adaptation based on user feedback and performance."""

    def __init__(self, learning_rate: float = 0.3):
        """
        Initialize difficulty adapter.

        Args:
            learning_rate: How quickly to adapt (0.0 to 1.0).
                          Higher = faster adaptation.
        """
        self.learning_rate = learning_rate

    def update_difficulty(
        self,
        old_difficulty: float,
        feedback: str,
        user_stats: Optional[Dict] = None,
    ) -> float:
        """
        Update difficulty using exponential moving average.

        Args:
            old_difficulty: Current difficulty (1-10).
            feedback: 'too_easy', 'too_hard', or 'just_right'.
            user_stats: Optional stats for the specific problem.

        Returns:
            Updated difficulty score between 1.0 and 10.0.

        Raises:
            ValueError: If feedback is invalid.
        """
        # Determine target adjustment
        if feedback == "too_easy":
            adjustment = 1.5
        elif feedback == "too_hard":
            adjustment = -1.5
        elif feedback == "just_right":
            adjustment = 0.0
        else:
            raise ValueError(f"Invalid feedback value: {feedback}")

        # Apply exponential moving average
        # new_diff = old_diff + learning_rate * adjustment
        new_difficulty = old_difficulty + (self.learning_rate * adjustment)

        # Consider historical performance if available
        if user_stats:
            attempts = user_stats.get("attempts", 0)
            successes = user_stats.get("successes", 0)

            if attempts > 0:
                success_rate = successes / attempts

                # If consistently too easy (high success rate), increase more
                if feedback == "too_easy" and success_rate > 0.8:
                    new_difficulty += 0.3

                # If consistently too hard (low success rate), decrease more
                elif feedback == "too_hard" and success_rate < 0.3:
                    new_difficulty -= 0.3

        # Clamp to valid range
        return max(1.0, min(10.0, new_difficulty))

    def batch_update_difficulties(
        self,
        feedback_list: List[Dict],
        current_difficulties: Dict[str, float],
        user_history: Optional[Dict] = None,
    ) -> Dict[str, float]:
        """
        Update multiple problem difficulties at once.

        Args:
            feedback_list: List of {problem_id, feedback} dicts.
            current_difficulties: Current difficulty mapping.
            user_history: User's problem history.

        Returns:
            Updated difficulty mapping.
        """
        updated = current_difficulties.copy()

        for item in feedback_list:
            problem_id = str(item["problem_id"])
            feedback = item["feedback"]

            old_diff = current_difficulties.get(problem_id, 5.0)

            # Get user stats for this problem
            user_stats = None
            if user_history:
                user_stats = user_history.get(problem_id)

            new_diff = self.update_difficulty(old_diff, feedback, user_stats)
            updated[problem_id] = new_diff

        return updated


class TopicMasteryTracker:
    """Tracks user's mastery level across different topics."""

    def __init__(self):
        self.topic_scores = {}  # topic -> mastery score (0.0 to 1.0)

    def update_topic_mastery(
        self,
        topic: str,
        feedback: str,
        current_mastery: float = 0.0,
    ) -> float:
        """
        Update mastery for a specific topic.

        Args:
            topic: Topic name.
            feedback: User feedback for the problem.
            current_mastery: Current mastery level (0.0 to 1.0).

        Returns:
            Updated mastery level.
        """
        # Define mastery increments based on feedback
        if feedback == "too_easy":
            increment = 0.15  # Significant mastery gain
        elif feedback == "just_right":
            increment = 0.08  # Moderate mastery gain
        elif feedback == "too_hard":
            increment = -0.05  # Slight mastery decrease (forgot or need review)
        else:
            increment = 0.0

        # Apply exponential moving average
        alpha = 0.2  # Smoothing factor
        new_mastery = current_mastery + alpha * increment

        # Clamp to valid range
        return max(0.0, min(1.0, new_mastery))

    def batch_update_topics(
        self,
        problem_topics: Dict[str, List[str]],
        feedback_list: List[Dict],
        current_mastery: Dict[str, float],
    ) -> Dict[str, float]:
        """
        Update mastery for all topics based on feedback.

        Args:
            problem_topics: Mapping of problem_id -> list of topics.
            feedback_list: List of feedback items.
            current_mastery: Current mastery levels.

        Returns:
            Updated mastery mapping.
        """
        updated = current_mastery.copy()

        for item in feedback_list:
            problem_id = str(item["problem_id"])
            feedback = item["feedback"]

            topics = problem_topics.get(problem_id, [])

            for topic in topics:
                old_mastery = current_mastery.get(topic, 0.0)
                new_mastery = self.update_topic_mastery(
                    topic, feedback, old_mastery
                )
                updated[topic] = new_mastery

        return updated


class PerformanceAnalyzer:
    """Analyzes user performance and provides insights."""

    @staticmethod
    def calculate_success_rate(problem_history: Dict) -> float:
        """Calculate overall success rate."""
        total_attempts = 0
        total_successes = 0

        for stats in problem_history.values():
            total_attempts += stats.get("attempts", 0)
            total_successes += stats.get("successes", 0)

        if total_attempts == 0:
            return 0.0

        return total_successes / total_attempts

    @staticmethod
    def calculate_speed_factor(problem_history: Dict) -> float:
        """
        Calculate user's speed factor (1.0 = average speed).

        Returns:
            Speed multiplier (e.g., 0.8 = 20% faster than average).
        """
        speed_ratios = []

        for stats in problem_history.values():
            base_time = stats.get("base_duration", 0)
            actual_time = stats.get("avg_time", 0)

            if base_time > 0 and actual_time > 0:
                speed_ratios.append(actual_time / base_time)

        if not speed_ratios:
            return 1.0

        return sum(speed_ratios) / len(speed_ratios)

    @staticmethod
    def get_learning_velocity(problem_history: Dict) -> str:
        """
        Analyze learning velocity (improving, stable, declining).

        Returns:
            One of: 'improving', 'stable', 'declining', 'insufficient_data'
        """
        # Get problems sorted by last_seen date
        sorted_problems = sorted(
            [
                (stats.get("last_seen"), stats)
                for stats in problem_history.values()
                if stats.get("last_seen")
            ],
            key=lambda x: x[0],
        )

        if len(sorted_problems) < 5:
            return "insufficient_data"

        # Split into recent and older half
        mid = len(sorted_problems) // 2
        older_half = sorted_problems[:mid]
        recent_half = sorted_problems[mid:]

        # Calculate success rates
        def avg_success_rate(problems):
            rates = []
            for _, stats in problems:
                attempts = stats.get("attempts", 0)
                successes = stats.get("successes", 0)
                if attempts > 0:
                    rates.append(successes / attempts)
            return sum(rates) / len(rates) if rates else 0.0

        older_rate = avg_success_rate(older_half)
        recent_rate = avg_success_rate(recent_half)

        # Determine trend
        if recent_rate > older_rate + 0.1:
            return "improving"
        elif recent_rate < older_rate - 0.1:
            return "declining"
        else:
            return "stable"

    @staticmethod
    def get_performance_insights(
        user_profile: Dict,
    ) -> Dict:
        """
        Generate comprehensive performance insights.

        Args:
            user_profile: Complete user profile.

        Returns:
            Dictionary with insights and recommendations.
        """
        history = user_profile.get("problem_history", {})

        if not history:
            return {
                "status": "no_data",
                "message": "Complete some problems to see insights!",
            }

        success_rate = PerformanceAnalyzer.calculate_success_rate(history)
        speed_factor = PerformanceAnalyzer.calculate_speed_factor(history)
        velocity = PerformanceAnalyzer.get_learning_velocity(history)

        # Generate recommendations
        recommendations = []

        if success_rate < 0.4:
            recommendations.append(
                "Consider lowering difficulty range - current problems may be too challenging"
            )
        elif success_rate > 0.85:
            recommendations.append(
                "You're crushing it! Try increasing difficulty range for more challenge"
            )

        if speed_factor < 0.7:
            recommendations.append(
                "You solve problems quickly! Consider tackling harder problems"
            )
        elif speed_factor > 1.3:
            recommendations.append(
                "Take your time to understand concepts deeply - speed will come naturally"
            )

        if velocity == "declining":
            recommendations.append(
                "Consider reviewing fundamentals or taking a short break to avoid burnout"
            )
        elif velocity == "improving":
            recommendations.append(
                "Great progress! Keep up the consistent practice"
            )

        return {
            "status": "active",
            "success_rate": round(success_rate * 100, 1),
            "speed_factor": round(speed_factor, 2),
            "learning_velocity": velocity,
            "total_problems": len(history),
            "recommendations": recommendations,
        }


def update_user_profile(
    user_profile: Dict,
    feedback_list: List[Dict],
    problem_data: Dict[str, Dict],
) -> Dict:
    """
    Comprehensive user profile update based on feedback.

    Args:
        user_profile: Current user profile.
        feedback_list: List of {problem_id, feedback, time_spent?} dicts.
        problem_data: Problem metadata (id -> problem dict).

    Returns:
        Updated user profile.
    """
    # Initialize profile components if missing
    if "difficulty_adjustments" not in user_profile:
        user_profile["difficulty_adjustments"] = {}
    if "topic_mastery" not in user_profile:
        user_profile["topic_mastery"] = {}
    if "problem_history" not in user_profile:
        user_profile["problem_history"] = {}
    if "topic_last_seen" not in user_profile:
        user_profile["topic_last_seen"] = {}

    # Initialize adapters
    diff_adapter = DifficultyAdapter(learning_rate=0.3)
    topic_tracker = TopicMasteryTracker()

    # Update difficulties
    user_profile["difficulty_adjustments"] = diff_adapter.batch_update_difficulties(
        feedback_list,
        user_profile["difficulty_adjustments"],
        user_profile["problem_history"],
    )

    # Build problem -> topics mapping
    problem_topics = {
        str(pid): prob["topics"]
        for pid, prob in problem_data.items()
    }

    # Update topic mastery
    user_profile["topic_mastery"] = topic_tracker.batch_update_topics(
        problem_topics,
        feedback_list,
        user_profile["topic_mastery"],
    )

    # Update problem history
    current_time = datetime.now().isoformat()

    for item in feedback_list:
        problem_id = str(item["problem_id"])

        if problem_id not in user_profile["problem_history"]:
            user_profile["problem_history"][problem_id] = {
                "attempts": 0,
                "successes": 0,
                "times": [],
                "base_duration": problem_data[problem_id].get("duration", 0),
            }

        stats = user_profile["problem_history"][problem_id]
        stats["attempts"] += 1
        stats["last_seen"] = current_time

        # Track success
        if item["feedback"] in ["just_right", "too_easy"]:
            stats["successes"] += 1

        # Track time if provided
        if "time_spent" in item and item["time_spent"]:
            stats["times"].append(item["time_spent"])
            stats["avg_time"] = sum(stats["times"]) / len(stats["times"])

        # Update topic last seen
        topics = problem_topics.get(problem_id, [])
        for topic in topics:
            user_profile["topic_last_seen"][topic] = current_time

    # Update speed factor
    analyzer = PerformanceAnalyzer()
    user_profile["speed_factor"] = analyzer.calculate_speed_factor(
        user_profile["problem_history"]
    )

    return user_profile


# Backward compatibility function
def update_difficulty(old: int, feedback: str) -> int:
    """
    Legacy function for simple difficulty update.
    Maintained for backward compatibility.

    Args:
        old: Current difficulty (1-10).
        feedback: 'too_easy', 'too_hard', or 'just_right'.

    Returns:
        Updated difficulty score between 1 and 10.
    """
    adapter = DifficultyAdapter(learning_rate=0.3)
    new_diff = adapter.update_difficulty(float(old), feedback)
    return int(round(new_diff))
