"""
Comprehensive unit tests for enhanced scheduler and difficulty modules.
"""

import json
import unittest
from datetime import datetime, timedelta

from app.core.difficulty import (
    DifficultyAdapter,
    PerformanceAnalyzer,
    TopicMasteryTracker,
    update_user_profile,
)
from app.core.scheduler import (
    calculate_personalized_difficulty,
    calculate_time_estimate,
    calculate_topic_priority,
    generate_plan,
    generate_plan_with_recommendations,
)


class TestDifficultyAdapter(unittest.TestCase):
    """Test difficulty adaptation logic."""

    def setUp(self):
        self.adapter = DifficultyAdapter(learning_rate=0.3)

    def test_too_easy_increases_difficulty(self):
        """Test that 'too_easy' feedback increases difficulty."""
        old_diff = 5.0
        new_diff = self.adapter.update_difficulty(old_diff, "too_easy")
        self.assertGreater(new_diff, old_diff)
        self.assertLessEqual(new_diff, 10.0)

    def test_too_hard_decreases_difficulty(self):
        """Test that 'too_hard' feedback decreases difficulty."""
        old_diff = 5.0
        new_diff = self.adapter.update_difficulty(old_diff, "too_hard")
        self.assertLess(new_diff, old_diff)
        self.assertGreaterEqual(new_diff, 1.0)

    def test_just_right_stable(self):
        """Test that 'just_right' keeps difficulty relatively stable."""
        old_diff = 5.0
        new_diff = self.adapter.update_difficulty(old_diff, "just_right")
        self.assertEqual(new_diff, old_diff)

    def test_difficulty_bounds(self):
        """Test that difficulty stays within 1-10 range."""
        # Upper bound
        high_diff = self.adapter.update_difficulty(9.5, "too_easy")
        self.assertLessEqual(high_diff, 10.0)

        # Lower bound
        low_diff = self.adapter.update_difficulty(1.5, "too_hard")
        self.assertGreaterEqual(low_diff, 1.0)

    def test_invalid_feedback_raises_error(self):
        """Test that invalid feedback raises ValueError."""
        with self.assertRaises(ValueError):
            self.adapter.update_difficulty(5.0, "invalid_feedback")

    def test_batch_update(self):
        """Test batch difficulty updates."""
        feedback_list = [
            {"problem_id": 1, "feedback": "too_easy"},
            {"problem_id": 2, "feedback": "too_hard"},
            {"problem_id": 3, "feedback": "just_right"},
        ]
        
        current = {"1": 5.0, "2": 5.0, "3": 5.0}
        updated = self.adapter.batch_update_difficulties(feedback_list, current)

        self.assertGreater(updated["1"], 5.0)
        self.assertLess(updated["2"], 5.0)
        self.assertEqual(updated["3"], 5.0)


class TestTopicMasteryTracker(unittest.TestCase):
    """Test topic mastery tracking."""

    def setUp(self):
        self.tracker = TopicMasteryTracker()

    def test_mastery_increases_with_success(self):
        """Test that mastery increases with positive feedback."""
        old_mastery = 0.5
        new_mastery = self.tracker.update_topic_mastery(
            "array", "too_easy", old_mastery
        )
        self.assertGreater(new_mastery, old_mastery)

    def test_mastery_bounded(self):
        """Test that mastery stays within 0-1 range."""
        # Upper bound
        high = self.tracker.update_topic_mastery("array", "too_easy", 0.95)
        self.assertLessEqual(high, 1.0)

        # Lower bound
        low = self.tracker.update_topic_mastery("array", "too_hard", 0.05)
        self.assertGreaterEqual(low, 0.0)

    def test_batch_topic_update(self):
        """Test batch topic mastery updates."""
        problem_topics = {
            "1": ["array", "hashmap"],
            "2": ["tree", "dfs"],
        }
        
        feedback_list = [
            {"problem_id": 1, "feedback": "too_easy"},
            {"problem_id": 2, "feedback": "too_hard"},
        ]
        
        current_mastery = {
            "array": 0.5,
            "hashmap": 0.5,
            "tree": 0.5,
            "dfs": 0.5,
        }

        updated = self.tracker.batch_update_topics(
            problem_topics, feedback_list, current_mastery
        )

        # Array and hashmap should increase
        self.assertGreater(updated["array"], 0.5)
        self.assertGreater(updated["hashmap"], 0.5)


class TestPerformanceAnalyzer(unittest.TestCase):
    """Test performance analysis functions."""

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        history = {
            "1": {"attempts": 3, "successes": 2},
            "2": {"attempts": 2, "successes": 2},
        }
        
        rate = PerformanceAnalyzer.calculate_success_rate(history)
        self.assertEqual(rate, 4 / 5)  # 4 successes out of 5 attempts

    def test_success_rate_empty_history(self):
        """Test success rate with no history."""
        rate = PerformanceAnalyzer.calculate_success_rate({})
        self.assertEqual(rate, 0.0)

    def test_speed_factor_calculation(self):
        """Test speed factor calculation."""
        history = {
            "1": {"base_duration": 20, "avg_time": 16},  # 0.8x speed
            "2": {"base_duration": 30, "avg_time": 30},  # 1.0x speed
        }
        
        speed = PerformanceAnalyzer.calculate_speed_factor(history)
        self.assertAlmostEqual(speed, 0.9, places=1)

    def test_learning_velocity_improving(self):
        """Test learning velocity detection - improving case."""
        base_time = datetime.now()
        
        history = {
            f"{i}": {
                "last_seen": (base_time - timedelta(days=10-i)).isoformat(),
                "attempts": 1,
                "successes": 1 if i > 5 else 0,  # Better performance recently
            }
            for i in range(1, 11)
        }
        
        velocity = PerformanceAnalyzer.get_learning_velocity(history)
        self.assertEqual(velocity, "improving")


class TestScheduler(unittest.TestCase):
    """Test scheduling logic."""

    def setUp(self):
        self.problems = [
            {"id": 1, "title": "Easy Problem", "topics": ["array"], 
             "duration": 15, "difficulty": 3},
            {"id": 2, "title": "Medium Problem", "topics": ["tree"], 
             "duration": 25, "difficulty": 5},
            {"id": 3, "title": "Hard Problem", "topics": ["dp"], 
             "duration": 35, "difficulty": 7},
            {"id": 4, "title": "Another Easy", "topics": ["array"], 
             "duration": 20, "difficulty": 3},
        ]

    def test_basic_plan_generation(self):
        """Test basic plan generation without user profile."""
        plan = generate_plan(self.problems, time_limit=60, min_d=3, max_d=7)
        
        # Should select problems
        self.assertGreater(len(plan), 0)
        
        # Should respect time limit
        total_time = sum(p.get("estimated_time", p["duration"]) for p in plan)
        self.assertLessEqual(total_time, 60)
        
        # Should respect difficulty range
        for problem in plan:
            self.assertGreaterEqual(problem["difficulty"], 3)
            self.assertLessEqual(problem["difficulty"], 7)

    def test_plan_with_user_profile(self):
        """Test plan generation with user profile."""
        user_profile = {
            "difficulty_adjustments": {"2": 6.5},  # User finds problem 2 harder
            "topic_mastery": {"array": 0.8, "tree": 0.3},
            "problem_history": {},
            "speed_factor": 0.9,
            "topic_last_seen": {},
        }
        
        plan = generate_plan(
            self.problems, 
            time_limit=60, 
            min_d=3, 
            max_d=7,
            user_profile=user_profile
        )
        
        # Should include personalized difficulty
        self.assertGreater(len(plan), 0)
        for problem in plan:
            self.assertIn("personalized_difficulty", problem)

    def test_topic_diversity(self):
        """Test that scheduler promotes topic diversity."""
        plan = generate_plan(self.problems, time_limit=100, min_d=1, max_d=10)
        
        # Count unique topics
        topics = set()
        for problem in plan:
            topics.update(problem["topics"])
        
        # Should select multiple topics
        self.assertGreater(len(topics), 1)

    def test_time_constraint_respected(self):
        """Test that time limit is strictly respected."""
        for time_limit in [30, 60, 90]:
            plan = generate_plan(self.problems, time_limit=time_limit, min_d=1, max_d=10)
            total_time = sum(p.get("estimated_time", p["duration"]) for p in plan)
            self.assertLessEqual(total_time, time_limit)

    def test_invalid_time_raises_error(self):
        """Test that invalid time limit raises error."""
        with self.assertRaises(ValueError):
            generate_plan(self.problems, time_limit=0, min_d=1, max_d=10)

    def test_no_eligible_problems(self):
        """Test behavior when no problems match criteria."""
        plan = generate_plan(self.problems, time_limit=60, min_d=8, max_d=10)
        self.assertEqual(len(plan), 0)


class TestPersonalization(unittest.TestCase):
    """Test personalization functions."""

    def test_personalized_difficulty_calculation(self):
        """Test personalized difficulty calculation."""
        user_profile = {
            "difficulty_adjustments": {"1": 5.5},
            "problem_history": {
                "1": {"attempts": 3, "successes": 3}  # High success rate
            }
        }
        
        # Should increase difficulty due to high success rate
        personal_diff = calculate_personalized_difficulty(5, user_profile, 1)
        self.assertGreater(personal_diff, 5.5)

    def test_time_estimate_with_history(self):
        """Test time estimation based on user history."""
        user_profile = {
            "speed_factor": 0.8,
            "problem_history": {
                "1": {"avg_time": 18}  # User consistently faster
            }
        }
        
        estimated = calculate_time_estimate(20, user_profile, 1)
        # Should use actual history
        self.assertAlmostEqual(estimated, 18 * 1.1, places=0)

    def test_time_estimate_without_history(self):
        """Test time estimation without specific problem history."""
        user_profile = {
            "speed_factor": 1.2,  # User is slower than average
            "problem_history": {}
        }
        
        estimated = calculate_time_estimate(20, user_profile, 1)
        # Should use speed factor
        self.assertEqual(estimated, 24)


class TestUserProfileUpdate(unittest.TestCase):
    """Test comprehensive user profile updates."""

    def test_profile_update_creates_missing_fields(self):
        """Test that profile update initializes missing fields."""
        profile = {}
        feedback = [{"problem_id": 1, "feedback": "just_right"}]
        problem_data = {
            "1": {"id": 1, "topics": ["array"], "duration": 20}
        }
        
        updated = update_user_profile(profile, feedback, problem_data)
        
        self.assertIn("difficulty_adjustments", updated)
        self.assertIn("topic_mastery", updated)
        self.assertIn("problem_history", updated)

    def test_profile_tracks_attempts(self):
        """Test that profile correctly tracks problem attempts."""
        profile = {"problem_history": {}}
        feedback = [
            {"problem_id": 1, "feedback": "too_hard"},
            {"problem_id": 1, "feedback": "just_right"},
        ]
        problem_data = {
            "1": {"id": 1, "topics": ["array"], "duration": 20}
        }
        
        updated = update_user_profile(profile, feedback, problem_data)
        
        # Should have 2 attempts
        self.assertEqual(updated["problem_history"]["1"]["attempts"], 2)

    def test_profile_updates_speed_factor(self):
        """Test that speed factor is updated."""
        profile = {
            "problem_history": {
                "1": {
                    "base_duration": 20,
                    "times": [16, 18],
                    "avg_time": 17,
                }
            }
        }
        feedback = [{"problem_id": 2, "feedback": "just_right", "time_spent": 24}]
        problem_data = {
            "2": {"id": 2, "topics": ["tree"], "duration": 30}
        }
        
        updated = update_user_profile(profile, feedback, problem_data)
        
        # Speed factor should be calculated
        self.assertIn("speed_factor", updated)
        self.assertIsInstance(updated["speed_factor"], float)


if __name__ == "__main__":
    unittest.main()
