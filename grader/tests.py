"""
Individual test functions for each student-implemented function.

Each test:
  - imports only the student function under test
  - feeds it *reference* inputs (so tests are independent)
  - awards partial credit based on output quality
"""

import math

import numpy as np
import pandas as pd

from grader import reference as ref
from grader.config import DATA_PATH, WEIGHTS, RTOL_LOOSE
from grader.utils import GradeResult, df_close, series_close


# ── 1. read_data ───────────────────────────────────────────────

def test_read_data() -> GradeResult:
    gr = GradeResult("read_data", WEIGHTS["read_data"])
    try:
        from src.io import read_data

        student = read_data(DATA_PATH)
        expected = ref.read_data(DATA_PATH)

        if not isinstance(student, pd.DataFrame):
            gr.fail("Return type is not pd.DataFrame")
            return gr
        gr.award(2.0, "Returns a DataFrame")

        if (
            isinstance(student.index, pd.DatetimeIndex)
            and student.index.name == "Date"
        ):
            gr.award(3.0, "DatetimeIndex named 'Date'")
        elif isinstance(student.index, pd.DatetimeIndex):
            gr.award(1.5, "DatetimeIndex present but name incorrect")
        else:
            gr.deduct("Index is not DatetimeIndex")

        if set(student.columns) == set(expected.columns):
            gr.award(2.0, "Correct columns")
        else:
            gr.deduct(
                f"Expected columns {list(expected.columns)}, "
                f"got {list(student.columns)}"
            )

        if student.shape == expected.shape:
            gr.award(2.0, "Correct shape")
        else:
            gr.deduct(
                f"Expected shape {expected.shape}, got {student.shape}"
            )

        if all(student[c].dtype == np.float64 for c in student.columns):
            gr.award(1.0, "Correct dtypes (float64)")
        elif all(
            np.issubdtype(student[c].dtype, np.number)
            for c in student.columns
        ):
            gr.award(0.5, "Numeric dtypes (not float64)")

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr


# ── 2. calculate_returns ──────────────────────────────────────

def test_calculate_returns() -> GradeResult:
    gr = GradeResult("calculate_returns", WEIGHTS["calculate_returns"])
    try:
        from src.returns import calculate_returns

        prices = ref.read_data(DATA_PATH)
        student = calculate_returns(prices)
        expected = ref.calculate_returns(prices)

        if not isinstance(student, pd.DataFrame):
            gr.fail("Return type is not pd.DataFrame")
            return gr
        gr.award(2.0, "Returns a DataFrame")

        if student.shape == expected.shape:
            gr.award(3.0, "Correct shape")
        else:
            gr.deduct(
                f"Shape mismatch: expected {expected.shape}, "
                f"got {student.shape}"
            )
            return gr

        if student.iloc[0].isna().all():
            gr.award(2.0, "First row is NaN")
        else:
            gr.deduct("First row should be NaN")

        ok, frac = df_close(student, expected)
        if ok:
            gr.award(8.0, "All values correct")
        elif frac > 0.9:
            gr.award(6.0, f"Most values correct ({frac:.1%})")
        elif frac > 0.5:
            gr.award(4.0, f"Some values correct ({frac:.1%})")
        elif frac > 0.0:
            gr.award(2.0, f"Few values correct ({frac:.1%})")
        else:
            gr.deduct("Values do not match reference")

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr


# ── 3. calculate_momentum ────────────────────────────────────

def test_calculate_momentum(lookback_days: int) -> GradeResult:
    gr = GradeResult("calculate_momentum", WEIGHTS["calculate_momentum"])
    try:
        from src.momentum import calculate_momentum

        prices = ref.read_data(DATA_PATH)
        daily_returns = ref.calculate_returns(prices)

        student = calculate_momentum(
            daily_returns, lookback_days=lookback_days
        )
        expected = ref.calculate_momentum(
            daily_returns, lookback_days=lookback_days
        )

        if not isinstance(student, pd.DataFrame):
            gr.fail("Return type is not pd.DataFrame")
            return gr
        gr.award(2.0, "Returns a DataFrame")

        if student.shape == expected.shape:
            gr.award(3.0, "Correct shape")
        else:
            gr.deduct(
                f"Shape mismatch: expected {expected.shape}, "
                f"got {student.shape}"
            )

        # NaN pattern check
        ref_first = expected.first_valid_index()
        try:
            stu_first = student.first_valid_index()
            if ref_first == stu_first:
                gr.award(2.0, "NaN pattern correct")
            elif stu_first is not None:
                gr.award(1.0, "Some NaN handling (start index differs)")
            else:
                gr.deduct("All values are NaN")
        except Exception:
            gr.deduct("Could not check NaN pattern")

        ok, frac = df_close(student, expected, rtol=RTOL_LOOSE)
        if ok:
            gr.award(13.0, "All values correct")
        elif frac > 0.9:
            gr.award(10.0, f"Most values correct ({frac:.1%})")
        elif frac > 0.7:
            gr.award(7.0, f"Many values correct ({frac:.1%})")
        elif frac > 0.3:
            gr.award(4.0, f"Some values correct ({frac:.1%})")
        elif frac > 0.0:
            gr.award(2.0, f"Few values correct ({frac:.1%})")
        else:
            gr.deduct("Values do not match reference")

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr


# ── 4. generate_signals ──────────────────────────────────────

def test_generate_signals(lookback_days: int) -> GradeResult:
    gr = GradeResult("generate_signals", WEIGHTS["generate_signals"])
    try:
        from src.signals import generate_signals

        prices = ref.read_data(DATA_PATH)
        daily_returns = ref.calculate_returns(prices)
        momentum = ref.calculate_momentum(
            daily_returns, lookback_days=lookback_days
        )

        student = generate_signals(momentum)
        expected = ref.generate_signals(momentum)

        if not isinstance(student, pd.DataFrame):
            gr.fail("Return type is not pd.DataFrame")
            return gr
        gr.award(2.0, "Returns a DataFrame")

        unique_vals = set(student.values.flatten())
        valid_vals = unique_vals - {np.nan}
        if valid_vals.issubset({-1.0, 0.0, 1.0}):
            gr.award(2.0, "Values are in {-1, 0, +1}")
        else:
            gr.deduct(
                f"Unexpected values: {valid_vals - {-1.0, 0.0, 1.0}}"
            )

        ok, frac = df_close(student, expected)
        if ok:
            gr.award(6.0, "All signals correct")
        elif frac > 0.9:
            gr.award(4.5, f"Most signals correct ({frac:.1%})")
        elif frac > 0.5:
            gr.award(3.0, f"Some signals correct ({frac:.1%})")
        else:
            gr.deduct("Signals do not match reference")

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr


# ── 5. calculate_volatility ──────────────────────────────────

def test_calculate_volatility() -> GradeResult:
    gr = GradeResult("calculate_volatility", WEIGHTS["calculate_volatility"])
    try:
        from src.strategy import calculate_volatility

        prices = ref.read_data(DATA_PATH)
        daily_returns = ref.calculate_returns(prices)

        student = calculate_volatility(daily_returns, vol_lookback=252)
        expected = ref.calculate_volatility(daily_returns, vol_lookback=252)

        if not isinstance(student, pd.DataFrame):
            gr.fail("Return type is not pd.DataFrame")
            return gr
        gr.award(2.0, "Returns a DataFrame")

        if student.shape == expected.shape:
            gr.award(2.0, "Correct shape")
        else:
            gr.deduct(
                f"Shape mismatch: expected {expected.shape}, "
                f"got {student.shape}"
            )

        ok, frac = df_close(student, expected, rtol=RTOL_LOOSE)
        if ok:
            gr.award(6.0, "All values correct")
        elif frac > 0.9:
            gr.award(4.5, f"Most values correct ({frac:.1%})")
        elif frac > 0.5:
            gr.award(3.0, f"Some values correct ({frac:.1%})")
        elif frac > 0.0:
            gr.award(1.5, f"Few values correct ({frac:.1%})")
        else:
            gr.deduct("Values do not match reference")

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr


# ── 6. calculate_strategy_returns ─────────────────────────────

def test_calculate_strategy_returns(lookback_days: int) -> GradeResult:
    gr = GradeResult(
        "calculate_strategy_returns",
        WEIGHTS["calculate_strategy_returns"],
    )
    try:
        from src.strategy import calculate_strategy_returns

        prices = ref.read_data(DATA_PATH)
        daily_returns = ref.calculate_returns(prices)
        momentum = ref.calculate_momentum(
            daily_returns, lookback_days=lookback_days
        )
        signals = ref.generate_signals(momentum)
        volatility = ref.calculate_volatility(daily_returns)

        student = calculate_strategy_returns(
            signals=signals,
            daily_returns=daily_returns,
            volatility=volatility,
            target_vol=0.40,
        )
        expected = ref.calculate_strategy_returns(
            signals=signals,
            daily_returns=daily_returns,
            volatility=volatility,
            target_vol=0.40,
        )

        if not isinstance(student, pd.DataFrame):
            gr.fail("Return type is not pd.DataFrame")
            return gr
        gr.award(2.0, "Returns a DataFrame")

        if "TSMOM" in student.columns:
            gr.award(3.0, "'TSMOM' column present")
        else:
            gr.deduct("Missing 'TSMOM' column")

        expected_asset_cols = {"SP500", "NASDAQ", "DJIA"}
        if expected_asset_cols.issubset(set(student.columns)):
            gr.award(2.0, "Asset columns present")
        else:
            gr.deduct(
                "Missing asset columns: "
                f"{expected_asset_cols - set(student.columns)}"
            )

        common_cols = [
            c
            for c in expected.columns
            if c in student.columns and c != "TSMOM"
        ]
        if common_cols:
            asset_ok, asset_frac = df_close(
                student[common_cols], expected[common_cols], rtol=RTOL_LOOSE
            )
            if asset_ok:
                gr.award(10.0, "Asset strategy returns correct")
            elif asset_frac > 0.8:
                gr.award(7.5, f"Asset returns mostly correct ({asset_frac:.1%})")
            elif asset_frac > 0.5:
                gr.award(5.0, f"Asset returns partially correct ({asset_frac:.1%})")
            elif asset_frac > 0.0:
                gr.award(2.5, f"Some asset returns correct ({asset_frac:.1%})")
            else:
                gr.deduct("Asset strategy returns incorrect")

        if "TSMOM" in student.columns and "TSMOM" in expected.columns:
            tsmom_ok, tsmom_frac = series_close(
                student["TSMOM"], expected["TSMOM"], rtol=RTOL_LOOSE
            )
            if tsmom_ok:
                gr.award(8.0, "TSMOM portfolio returns correct")
            elif tsmom_frac > 0.8:
                gr.award(6.0, f"TSMOM mostly correct ({tsmom_frac:.1%})")
            elif tsmom_frac > 0.5:
                gr.award(3.0, f"TSMOM partially correct ({tsmom_frac:.1%})")
            else:
                gr.deduct("TSMOM values incorrect")

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr


# ── 7. calculate_performance ─────────────────────────────────

def test_calculate_performance(lookback_days: int) -> GradeResult:
    gr = GradeResult(
        "calculate_performance", WEIGHTS["calculate_performance"]
    )
    try:
        from src.performance import calculate_performance

        # Build full reference pipeline to get TSMOM series
        prices = ref.read_data(DATA_PATH)
        daily_returns = ref.calculate_returns(prices)
        momentum = ref.calculate_momentum(
            daily_returns, lookback_days=lookback_days
        )
        signals = ref.generate_signals(momentum)
        volatility = ref.calculate_volatility(daily_returns)
        strategy_rets = ref.calculate_strategy_returns(
            signals, daily_returns, volatility
        )
        tsmom = strategy_rets["TSMOM"]
        expected = ref.calculate_performance(tsmom)

        student = calculate_performance(tsmom)

        if not isinstance(student, dict):
            gr.fail("Return type is not dict")
            return gr
        gr.award(1.0, "Returns a dict")

        expected_keys = {
            "annualized_return",
            "annualized_volatility",
            "sharpe_ratio",
        }
        if expected_keys.issubset(set(student.keys())):
            gr.award(2.0, "All expected keys present")
        else:
            missing = expected_keys - set(student.keys())
            gr.deduct(f"Missing keys: {missing}")

        metrics = [
            ("annualized_return", 1.5),
            ("annualized_volatility", 1.5),
            ("sharpe_ratio", 1.5)
        ]
        for key, pts in metrics:
            if key in student and key in expected:
                s_val = float(student[key])
                r_val = float(expected[key])
                if math.isclose(s_val, r_val, rel_tol=1e-3, abs_tol=1e-6):
                    gr.award(pts, f"{key} correct")
                elif math.isclose(s_val, r_val, rel_tol=5e-2, abs_tol=1e-4):
                    gr.award(pts * 0.5, f"{key} approximately correct")
                else:
                    gr.deduct(
                        f"{key}: expected {r_val:.6f}, got {s_val:.6f}"
                    )

    except Exception as e:
        gr.fail(f"Exception: {e}")
    return gr
