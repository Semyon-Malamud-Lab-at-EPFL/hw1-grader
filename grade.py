#!/usr/bin/env python3
"""
HW1 Autograder — Entry Point
=============================

Usage (called by the GitHub Actions workflow):
    python grade.py

Environment:
    GITHUB_REPOSITORY  — set automatically by GitHub Actions
                         (e.g. "course-org/hw0-johndoe")
"""

import sys

from grader.config import get_student_lookback
from grader.runner import run_all, print_report, write_json


def main() -> int:
    lookback = get_student_lookback()
    results = run_all()

    print_report(results, lookback)
    write_json(results, lookback)

    total = sum(r.points for r in results)
    max_total = sum(r.max_points for r in results)
    return 0 if total == max_total else 1


if __name__ == "__main__":
    sys.exit(main())
