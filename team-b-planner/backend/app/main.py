"""
Enhanced FastAPI backend with personalization support.

New features:
- User profile management
- Performance analytics
- Personalized recommendations
- Session tracking
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from app.core.difficulty import (
    PerformanceAnalyzer,
    update_user_profile,
)
from app.core.loader import load_problems
from app.core.scheduler import generate_plan_with_recommendations
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------
# App Setup
# ---------------------------------

app = FastAPI(title="AI Practice Planner - Enhanced")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROBLEM_FILE = os.path.join(DATA_DIR, "problems.json")
USER_PROFILE_FILE = os.path.join(DATA_DIR, "user_profile.json")

# Legacy support
DIFF_FILE = os.path.join(DATA_DIR, "difficulty.json")


# ---------------------------------
# Request/Response Models
# ---------------------------------


class PlanRequest(BaseModel):
    time: int
    min_d: int
    max_d: int
    user_id: Optional[str] = "default_user"


class FeedbackItem(BaseModel):
    problem_id: int
    feedback: str
    time_spent: Optional[int] = None  # Actual time spent in minutes


class FeedbackRequest(BaseModel):
    feedback: List[FeedbackItem]
    user_id: Optional[str] = "default_user"


class SessionStartRequest(BaseModel):
    user_id: Optional[str] = "default_user"
    session_type: Optional[str] = "practice"


# ---------------------------------
# Helper Functions
# ---------------------------------


def load_user_profile(user_id: str = "default_user") -> Dict:
    """Load user profile from file."""
    try:
        if not os.path.exists(USER_PROFILE_FILE):
            logger.info("No user profile found, creating new one")
            return create_default_profile(user_id)

        with open(USER_PROFILE_FILE, "r") as f:
            profile = json.load(f)
            
        logger.info(f"Loaded profile for user: {user_id}")
        return profile

    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        return create_default_profile(user_id)


def save_user_profile(profile: Dict) -> None:
    """Save user profile to file."""
    try:
        profile["last_updated"] = datetime.now().isoformat()
        
        with open(USER_PROFILE_FILE, "w") as f:
            json.dump(profile, f, indent=2)
            
        logger.info("User profile saved successfully")
        
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        raise


def create_default_profile(user_id: str) -> Dict:
    """Create a new default user profile."""
    return {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        "difficulty_adjustments": {},
        "topic_mastery": {},
        "problem_history": {},
        "topic_last_seen": {},
        "speed_factor": 1.0,
        "preferences": {
            "favorite_topics": [],
            "avoid_topics": [],
            "preferred_time_range": [30, 90],
            "preferred_difficulty_range": [3, 7],
        },
        "statistics": {
            "total_sessions": 0,
            "total_problems_attempted": 0,
            "total_problems_solved": 0,
            "total_practice_time": 0,
            "average_session_length": 0,
            "current_streak": 0,
            "longest_streak": 0,
        },
    }


def load_problems_as_dict(filepath: str) -> Dict[str, Dict]:
    """Load problems and return as dict mapping id -> problem."""
    problems = load_problems(filepath)
    return {str(p["id"]): p for p in problems}


# ---------------------------------
# API Routes
# ---------------------------------


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "Enhanced Planner backend running",
        "version": "2.0",
        "features": [
            "personalized_difficulty",
            "topic_mastery",
            "performance_analytics",
            "spaced_repetition",
        ],
    }


@app.post("/generate_plan")
def generate(req: PlanRequest):
    """
    Generate personalized practice plan.
    
    Now includes:
    - Personalized difficulty adjustments
    - Topic mastery consideration
    - Spaced repetition
    - Time estimation based on user speed
    """
    logger.info(f"Generate plan request: {req.time}min, diff {req.min_d}-{req.max_d}")

    if req.min_d > req.max_d:
        raise HTTPException(
            status_code=400, 
            detail="min_d cannot be greater than max_d"
        )

    try:
        # Load problems and user profile
        problems = load_problems(PROBLEM_FILE)
        user_profile = load_user_profile(req.user_id)

        # Generate personalized plan with recommendations
        plan, recommendations = generate_plan_with_recommendations(
            problems, req.time, req.min_d, req.max_d, user_profile
        )

        logger.info(f"Generated plan with {len(plan)} problems")

        # Update session statistics
        user_profile["statistics"]["total_sessions"] += 1
        save_user_profile(user_profile)

        return {
            "plan": plan,
            "recommendations": recommendations,
            "session_info": {
                "total_sessions": user_profile["statistics"]["total_sessions"],
                "current_streak": user_profile["statistics"]["current_streak"],
            },
        }

    except Exception as e:
        logger.error(f"Error generating plan: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate plan: {str(e)}"
        )


@app.post("/feedback")
def submit_feedback(req: FeedbackRequest):
    """
    Submit feedback and update user profile.
    
    Now updates:
    - Personalized difficulty scores
    - Topic mastery levels
    - Problem history and success rates
    - Speed factor
    """
    logger.info(f"Feedback received for {len(req.feedback)} problems")

    try:
        # Load current profile and problems
        user_profile = load_user_profile(req.user_id)
        problem_data = load_problems_as_dict(PROBLEM_FILE)

        # Convert feedback to list of dicts
        feedback_list = [item.dict() for item in req.feedback]

        # Update comprehensive user profile
        user_profile = update_user_profile(
            user_profile, feedback_list, problem_data
        )

        # Update statistics
        stats = user_profile["statistics"]
        stats["total_problems_attempted"] += len(req.feedback)
        
        # Count successes
        successes = sum(
            1 for item in req.feedback 
            if item.feedback in ["just_right", "too_easy"]
        )
        stats["total_problems_solved"] += successes

        # Update total practice time
        total_time = sum(
            item.time_spent for item in req.feedback 
            if item.time_spent
        )
        if total_time:
            stats["total_practice_time"] += total_time

        # Calculate streak
        if successes > 0:
            stats["current_streak"] += 1
            stats["longest_streak"] = max(
                stats["longest_streak"], 
                stats["current_streak"]
            )
        else:
            stats["current_streak"] = 0

        # Save updated profile
        save_user_profile(user_profile)

        logger.info("User profile updated successfully")

        # Get performance insights
        analyzer = PerformanceAnalyzer()
        insights = analyzer.get_performance_insights(user_profile)

        return {
            "message": "Feedback saved successfully",
            "insights": insights,
            "statistics": stats,
        }

    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to save feedback: {str(e)}"
        )


@app.get("/analytics/{user_id}")
def get_analytics(user_id: str = "default_user"):
    """
    Get comprehensive performance analytics.
    
    Returns:
    - Success rate
    - Learning velocity
    - Topic mastery breakdown
    - Speed factor
    - Recommendations
    """
    try:
        user_profile = load_user_profile(user_id)
        analyzer = PerformanceAnalyzer()
        insights = analyzer.get_performance_insights(user_profile)

        return {
            "user_id": user_id,
            "insights": insights,
            "statistics": user_profile.get("statistics", {}),
            "topic_mastery": user_profile.get("topic_mastery", {}),
            "speed_factor": user_profile.get("speed_factor", 1.0),
        }

    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to fetch analytics"
        )


@app.get("/profile/{user_id}")
def get_profile(user_id: str = "default_user"):
    """Get user profile summary."""
    try:
        profile = load_user_profile(user_id)
        
        # Return sanitized profile (no sensitive data)
        return {
            "user_id": profile["user_id"],
            "created_at": profile["created_at"],
            "statistics": profile.get("statistics", {}),
            "preferences": profile.get("preferences", {}),
            "topic_count": len(profile.get("topic_mastery", {})),
            "problems_attempted": len(profile.get("problem_history", {})),
        }

    except Exception as e:
        logger.error(f"Error fetching profile: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to fetch profile"
        )


@app.post("/reset_profile/{user_id}")
def reset_profile(user_id: str = "default_user"):
    """Reset user profile (for testing or fresh start)."""
    try:
        new_profile = create_default_profile(user_id)
        save_user_profile(new_profile)
        
        logger.info(f"Profile reset for user: {user_id}")
        
        return {
            "message": "Profile reset successfully",
            "user_id": user_id,
        }

    except Exception as e:
        logger.error(f"Error resetting profile: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to reset profile"
        )


# ---------------------------------
# Legacy Endpoints (backward compatibility)
# ---------------------------------


@app.get("/legacy/difficulty")
def get_legacy_difficulty():
    """Get difficulty adjustments in legacy format."""
    try:
        profile = load_user_profile()
        return profile.get("difficulty_adjustments", {})
    except Exception as e:
        logger.error(f"Error in legacy endpoint: {str(e)}")
        return {}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
