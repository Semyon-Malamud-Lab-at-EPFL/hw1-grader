"""
Grading orchestration: runs all tests, prints results, writes JSON.
"""

from __future__ import annotations

import json

from grader.config import get_student_lookback
from grader.utils import GradeResult
from grader import tests


def run_all() -> list[GradeResult]:
    """Execute every test and return a list of GradeResults."""
    lookback = get_student_lookback()

    return [
        tests.test_read_data(),
        tests.test_calculate_returns(),
        tests.test_calculate_momentum(lookback),
        tests.test_generate_signals(lookback),
        tests.test_calculate_volatility(),
        tests.test_calculate_strategy_returns(lookback),
        tests.test_calculate_performance(lookback),
    ]


def print_report(results: list[GradeResult], lookback: int) -> None:
    """Pretty-print the grading report to stdout."""
    print("=" * 60)
    print("  HW1 Autograder — Time Series Momentum Strategy")
    print(f"  Student look-back period: {lookback} trading days")
    print("=" * 60)
    print()

    print("-" * 60)
    for r in results:
        print(r)
        print()
    print("-" * 60)

    total = sum(r.points for r in results)
    max_total = sum(r.max_points for r in results)
    print(f"  TOTAL SCORE: {total:.1f} / {max_total:.1f}")
    print("-" * 60)


def write_json(
    results: list[GradeResult], lookback: int, path: str = "grading_results.json"
) -> dict:
    """Serialize results to a JSON file (consumed by the CI summary step)."""
    total = sum(r.points for r in results)
    max_total = sum(r.max_points for r in results)

    output = {
        "total": round(total, 2),
        "max_total": round(max_total, 2),
        "lookback_days": lookback,
        "tests": [r.to_dict() for r in results],
    }
    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    return output
