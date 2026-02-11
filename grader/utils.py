"""
Grading utilities: result container and numerical comparison helpers.
"""

from __future__ import annotations

import time
from typing import Any, Callable

import numpy as np
import pandas as pd

from grader.config import RTOL_STRICT, ATOL_STRICT, SLOWDOWN_FACTOR


# ---------------------------------------------------------------------------
# Grade result container
# ---------------------------------------------------------------------------

class GradeResult:
    """Accumulates points and diagnostic messages for a single test."""

    def __init__(self, name: str, max_points: float):
        self.name = name
        self.max_points = max_points
        self.points = 0.0
        self.messages: list[str] = []

    # -- mutators -----------------------------------------------------------

    def award(self, pts: float, msg: str = "") -> None:
        self.points = min(self.points + pts, self.max_points)
        if msg:
            self.messages.append(f"  [+{pts:.1f}] {msg}")

    def deduct(self, msg: str) -> None:
        self.messages.append(f"  [  ] {msg}")

    def fail(self, msg: str) -> None:
        self.points = 0.0
        self.messages = [f"  [FAIL] {msg}"]

    # -- display ------------------------------------------------------------

    @property
    def status(self) -> str:
        if self.points == self.max_points:
            return "PASS"
        return "PARTIAL" if self.points > 0 else "FAIL"

    def __repr__(self) -> str:
        header = (
            f"[{self.status}] {self.name}: "
            f"{self.points:.1f}/{self.max_points:.1f}"
        )
        body = "\n".join(self.messages)
        return f"{header}\n{body}" if body else header

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "points": round(self.points, 2),
            "max_points": round(self.max_points, 2),
            "messages": self.messages,
        }


# ---------------------------------------------------------------------------
# Numerical comparison helpers
# ---------------------------------------------------------------------------

def df_close(
    student_df: pd.DataFrame,
    ref_df: pd.DataFrame,
    rtol: float = RTOL_STRICT,
    atol: float = ATOL_STRICT,
) -> tuple[bool, float]:
    """Element-wise comparison of two DataFrames.

    Returns
    -------
    all_close : bool
        True only if every element matches within tolerance and NaN
        positions are identical.
    fraction_close : float
        Fraction of elements that are correct (0.0 – 1.0), where
        NaN-pattern agreement counts for half and value agreement
        counts for the other half.
    """
    try:
        if student_df.shape != ref_df.shape:
            return False, 0.0

        ref_vals = ref_df.values.astype(float)
        stu_vals = student_df.values.astype(float)

        ref_nan = np.isnan(ref_vals)
        stu_nan = np.isnan(stu_vals)

        nan_match = np.array_equal(ref_nan, stu_nan)
        nan_frac = np.mean(ref_nan == stu_nan) if not nan_match else 1.0

        mask = ~ref_nan & ~stu_nan
        if mask.sum() == 0:
            return nan_match, nan_frac

        close = np.isclose(
            ref_vals[mask], stu_vals[mask], rtol=rtol, atol=atol
        )
        val_frac = close.mean()

        total_frac = 0.5 * nan_frac + 0.5 * val_frac
        all_close = nan_match and (val_frac == 1.0)
        return all_close, total_frac

    except Exception:
        return False, 0.0


def series_close(
    student_s: pd.Series,
    ref_s: pd.Series,
    rtol: float = RTOL_STRICT,
    atol: float = ATOL_STRICT,
) -> tuple[bool, float]:
    """Convenience wrapper around :func:`df_close` for Series."""
    return df_close(
        student_s.to_frame(), ref_s.to_frame(), rtol=rtol, atol=atol
    )


# ---------------------------------------------------------------------------
# Timing helpers
# ---------------------------------------------------------------------------

# Reference functions that run in under this threshold (seconds) are
# too fast to measure reliably on CI runners, so we skip the speed
# check for those.
_MIN_REF_TIME = 0.05


def time_call(fn: Callable, *args: Any, **kwargs: Any) -> tuple[Any, float]:
    """Call *fn* and return (result, elapsed_seconds)."""
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return result, elapsed


def check_speed(
    gr: "GradeResult",
    ref_seconds: float,
    student_seconds: float,
) -> bool:
    """Compare student vs reference runtime.

    If the student function exceeds SLOWDOWN_FACTOR × reference time,
    the GradeResult is zeroed and a message is added.

    Returns True if the check passes (or is skipped), False if failed.
    """
    if SLOWDOWN_FACTOR <= 0:
        return True  # disabled

    if ref_seconds < _MIN_REF_TIME:
        return True  # too fast to measure reliably

    ratio = student_seconds / ref_seconds
    if ratio > SLOWDOWN_FACTOR:
        gr.fail(
            f"Too slow: your code took {student_seconds:.3f}s, "
            f"reference took {ref_seconds:.3f}s "
            f"({ratio:.1f}× slower, limit is {SLOWDOWN_FACTOR}×)"
        )
        return False
    return True
