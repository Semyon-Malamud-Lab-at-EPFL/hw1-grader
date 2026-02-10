"""
Configuration and constants for the HW1 autograder.

Handles student-specific parameter derivation and shared constants
used across the grading pipeline.
"""

import hashlib
import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
DATA_PATH = "data/price_data.csv"

# ---------------------------------------------------------------------------
# Grading weights  (must sum to 100)
# ---------------------------------------------------------------------------
WEIGHTS = {
    "read_data": 10.0,
    "calculate_returns": 15.0,
    "calculate_momentum": 20.0,
    "generate_signals": 10.0,
    "calculate_volatility": 10.0,
    "calculate_strategy_returns": 25.0,
    "calculate_performance": 10.0,
}

assert sum(WEIGHTS.values()) == 100.0, "Grading weights must sum to 100"

# ---------------------------------------------------------------------------
# Numerical tolerances
# ---------------------------------------------------------------------------
RTOL_STRICT = 1e-4
ATOL_STRICT = 1e-6
RTOL_LOOSE = 1e-3
ATOL_LOOSE = 1e-5

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
TARGET_VOL = 0.10
TRADING_DAYS_PER_YEAR = 252

# ---------------------------------------------------------------------------
# Student parameter derivation
# ---------------------------------------------------------------------------
LOOKBACK_MIN = 100   
LOOKBACK_MAX = 252  
LOOKBACK_RANGE = LOOKBACK_MAX - LOOKBACK_MIN + 1  


def get_student_lookback() -> int:
    """Derive a deterministic look-back period (in trading days) from
    the GitHub repository name set by the CI environment.

    The repository name follows the GitHub Classroom convention:
        ``<org>/hw0-<username>``

    Returns
    -------
    int
        An integer in [LOOKBACK_MIN, LOOKBACK_MAX]
    """
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    slug = repo.split("/")[-1]  # e.g. "hw0-demirayonur"
    h = int(hashlib.sha256(slug.encode()).hexdigest(), 16)
    return (h % LOOKBACK_RANGE) + LOOKBACK_MIN

