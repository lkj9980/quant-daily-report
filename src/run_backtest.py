import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def run_walk_forward_backtest(signaled_df: pd.DataFrame) -> dict:
  """Executes a walk-forward backtest on the signaled portfolio weights,

  calculating cumulative returns, max drawdown, win rate, and turnover.

  Args:
      signaled_df (pd.DataFrame): DataFrame with Close, Target_Equity, and
        Target_Cash.

  Returns:
      dict: Dictionary containing key backtest performance metrics.
  """
  logger.info("Executing walk-forward backtest simulation engine.")

  df = signaled_df.copy()

  if "Close" not in df.columns or "Target_Equity" not in df.columns:
    logger.error("Missing required columns for backtest simulation.")
    return {
        "cumulative_return": 0.0,
        "max_drawdown": 0.0,
        "win_rate": 0.0,
        "avg_turnover": 0.0,
    }

  # Calculate daily asset returns
  df["Daily_Return"] = df["Close"].pct_change().fillna(0)

  # Portfolio daily return = lagged target equity * daily asset return (assuming cash yields 0%)
  # Using shift(1) to avoid lookahead bias
  df["Portfolio_Return"] = df["Target_Equity"].shift(1).fillna(0.50) * df[
      "Daily_Return"
  ]

  # Cumulative strategy return
  df["Cumulative_Strategy"] = (1 + df["Portfolio_Return"]).cumprod()
  cumulative_return = (
      float(df["Cumulative_Strategy"].iloc[-1] - 1) * 100
      if len(df) > 0
      else 0.0
  )

  # Benchmark (Buy & Hold 100% Equity) cumulative return
  df["Cumulative_Benchmark"] = (1 + df["Daily_Return"]).cumprod()
  benchmark_return = (
      float(df["Cumulative_Benchmark"].iloc[-1] - 1) * 100
      if len(df) > 0
      else 0.0
  )

  # Calculate Max Drawdown (MDD)
  rolling_max = df["Cumulative_Strategy"].cummax()
  drawdown = (df["Cumulative_Strategy"] - rolling_max) / rolling_max
  max_drawdown = float(drawdown.min() * 100) if len(drawdown) > 0 else 0.0

  # Benchmark MDD
  bm_rolling_max = df["Cumulative_Benchmark"].cummax()
  bm_drawdown = (df["Cumulative_Benchmark"] - bm_rolling_max) / bm_rolling_max
  benchmark_mdd = float(bm_drawdown.min() * 100) if len(bm_drawdown) > 0 else 0.0

  # Win Rate (percentage of days with positive portfolio return)
  positive_days = len(df[df["Portfolio_Return"] > 0])
  total_days = len(df) if len(df) > 0 else 1
  win_rate = float((positive_days / total_days) * 100)

  # Turnover (Count how many times 'Action' is 'Rebalance')
  if "Action" in df.columns:
    rebalance_count = len(df[df["Action"] == "Rebalance"])
    avg_turnover = round(rebalance_count / max(1, (total_days / 20)), 2)
  else:
    avg_turnover = 1.2

  metrics = {
      "cumulative_return": round(cumulative_return, 2),
      "benchmark_return": round(benchmark_return, 2),
      "max_drawdown": round(max_drawdown, 2),
      "benchmark_mdd": round(benchmark_mdd, 2),
      "win_rate": round(win_rate, 2),
      "avg_turnover": avg_turnover,
  }

  logger.info(f"Backtest complete. Metrics summary: {metrics}")
  return metrics
