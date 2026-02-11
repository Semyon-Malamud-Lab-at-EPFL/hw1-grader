"""
Reference implementations for every student function.

These are the ground-truth solutions used to generate expected outputs
for grading.  They must never be visible to students.
"""

import numpy as np
import pandas as pd

from grader.config import TARGET_VOL, TRADING_DAYS_PER_YEAR


# ── io.py ──────────────────────────────────────────────────────

def read_data(filepath: str) -> pd.DataFrame:
    df = pd.read_csv(filepath, parse_dates=["Date"], index_col="Date")
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ── returns.py ─────────────────────────────────────────────────

def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change()


# ── momentum.py ────────────────────────────────────────────────

def calculate_momentum(
    daily_returns: pd.DataFrame, lookback_days: int
) -> pd.DataFrame:
    cum = (1 + daily_returns).cumprod()
    shifted = cum.shift(1)
    lagged = cum.shift(lookback_days + 1)
    return shifted / lagged - 1


# ── signals.py ─────────────────────────────────────────────────

def generate_signals(momentum: pd.DataFrame) -> pd.DataFrame:
    signals = np.sign(momentum)
    return signals.fillna(0.0)


# ── strategy.py ────────────────────────────────────────────────

def calculate_volatility(
    daily_returns: pd.DataFrame, vol_lookback: int = 252
) -> pd.DataFrame:
    return (
        daily_returns
        .rolling(window=vol_lookback, min_periods=vol_lookback)
        .std()
        * np.sqrt(TRADING_DAYS_PER_YEAR)
    )


def calculate_strategy_returns(
    signals: pd.DataFrame,
    daily_returns: pd.DataFrame,
    volatility: pd.DataFrame,
    target_vol: float = TARGET_VOL,
) -> pd.DataFrame:
    lagged_vol = volatility.shift(1)
    asset_cols = signals.columns.tolist()
    strategy = signals * (target_vol / lagged_vol) * daily_returns
    strategy["TSMOM"] = strategy[asset_cols].mean(axis=1)
    return strategy


# ── performance.py ─────────────────────────────────────────────

def calculate_performance(daily_returns: pd.Series) -> dict:
    r = daily_returns.dropna()
    ann_ret = r.mean() * TRADING_DAYS_PER_YEAR
    ann_vol = r.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    sharpe = ann_ret / ann_vol if ann_vol != 0 else 0.0
    wealth = (1 + r).cumprod()
    peak = wealth.cummax()
    dd = (wealth - peak) / peak
    return {
        "annualized_return": ann_ret,
        "annualized_volatility": ann_vol,
        "sharpe_ratio": sharpe,
        "max_drawdown": dd.min(),
        "cumulative_return": wealth.iloc[-1] - 1,
    }
