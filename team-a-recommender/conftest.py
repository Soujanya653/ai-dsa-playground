import sys
from pathlib import Path

# Add project root to Python path for tests
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))
