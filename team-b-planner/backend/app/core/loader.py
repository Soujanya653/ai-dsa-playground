"""
Problem data loader module.

Loads problem metadata from JSON files and returns
structured Python objects for use in scheduling.
"""

import json
from typing import Dict, List


def load_problems(path: str) -> List[Dict]:
    """
    Load problems from a JSON file.

    Args:
        path: Path to problems.json file.

    Returns:
        List of problem dictionaries.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
