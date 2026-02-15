"""
Migration script to convert old difficulty.json to new user_profile.json format.

Usage:
    python migrate_to_v2.py
"""

import json
import os
from datetime import datetime


def load_old_difficulty(filepath):
    """Load old difficulty.json file."""
    if not os.path.exists(filepath):
        print(f"⚠️  No {filepath} found - starting fresh")
        return {}
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data)} difficulty adjustments from old format")
    return data


def create_user_profile(old_difficulty):
    """Create new user profile from old difficulty data."""
    
    profile = {
        "user_id": "default_user",
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat(),
        
        # Migrate old difficulty adjustments
        "difficulty_adjustments": {
            str(k): float(v) for k, v in old_difficulty.items()
        },
        
        # Initialize new features
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
    
    # If we have difficulty adjustments, estimate some statistics
    if old_difficulty:
        # Estimate they've attempted these problems
        profile["statistics"]["total_problems_attempted"] = len(old_difficulty)
        
        # Create basic problem history
        for problem_id, difficulty in old_difficulty.items():
            profile["problem_history"][str(problem_id)] = {
                "attempts": 1,
                "successes": 1 if difficulty >= 3 else 0,  # Estimate success
                "last_seen": datetime.now().isoformat(),
                "times": [],
                "avg_time": None,
                "base_duration": 0,
            }
    
    return profile


def save_user_profile(profile, filepath):
    """Save new user profile."""
    with open(filepath, 'w') as f:
        json.dump(profile, f, indent=2)
    
    print(f"✅ Saved new profile to {filepath}")


def backup_old_file(filepath):
    """Backup old difficulty.json file."""
    if os.path.exists(filepath):
        backup_path = filepath + '.backup'
        
        # Don't overwrite existing backup
        counter = 1
        while os.path.exists(backup_path):
            backup_path = f"{filepath}.backup{counter}"
            counter += 1
        
        os.rename(filepath, backup_path)
        print(f"✅ Backed up old file to {backup_path}")
        return backup_path
    return None


def main():
    """Run migration."""
    print("🚀 Starting migration to v2.0...")
    print()
    
    # Paths
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    old_file = os.path.join(data_dir, 'difficulty.json')
    new_file = os.path.join(data_dir, 'user_profile.json')
    
    # Check if already migrated
    if os.path.exists(new_file):
        response = input(f"⚠️  {new_file} already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("❌ Migration cancelled")
            return
    
    # Load old data
    old_difficulty = load_old_difficulty(old_file)
    
    # Create new profile
    print("🔄 Creating new user profile...")
    profile = create_user_profile(old_difficulty)
    
    # Backup old file
    if os.path.exists(old_file):
        backup_old_file(old_file)
    
    # Save new profile
    save_user_profile(profile, new_file)
    
    print()
    print("=" * 60)
    print("✅ Migration complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  • Migrated {len(old_difficulty)} difficulty adjustments")
    print(f"  • Created profile at: {new_file}")
    print(f"  • Old file backed up")
    print()
    print("Next steps:")
    print("  1. Copy enhanced files to your project:")
    print("     - scheduler.py → backend/app/core/")
    print("     - difficulty.py → backend/app/core/")
    print("     - main.py → backend/")
    print("     - app_enhanced.py → frontend/")
    print()
    print("  2. Restart your backend and frontend")
    print()
    print("  3. Test the new features!")
    print()
    print("💡 Read README_ENHANCED.md for full documentation")


if __name__ == "__main__":
    main()
