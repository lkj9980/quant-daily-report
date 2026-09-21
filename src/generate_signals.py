import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def generate_signals(
    features_df: pd.DataFrame, threshold: float = 0.05, research_context: dict = None
) -> pd.DataFrame:

  """Generates portfolio target weights and smooths signals using threshold

  rebalancing to prevent high turnover (flickering allocations).

  Args:
      features_df (pd.DataFrame): DataFrame containing price, MA, volatility, and
        regime filter.
      threshold (float): Minimum weight change required to trigger actual
        rebalancing (default 5%).

  Returns:
      pd.DataFrame: DataFrame appended with Target_Equity, Target_Cash, and
      Action columns.
  """
  logger.info(
      "Generating smooth portfolio signals with threshold filter:"
      f" {threshold * 100}%"
  )

  df = features_df.copy()

  equity_weights = []
  cash_weights = []
  actions = []

  # Initial baseline: 50% equity, 50% cash
  current_equity = 0.50
  current_cash = 0.50

  for idx, row in df.iterrows():
    regime = row.get("Regime", "Risk-Off")

    # Determine desired raw target based on market regime filter
    if regime == "Risk-On":
      raw_target_equity = 0.70  # Aggressive stance in bull/stable market
    else:
      raw_target_equity = 0.30  # Defensive stance in volatile/bear market

    # Apply threshold rebalancing (Threshold Band Rebalancing)
    # Only rebalance if the difference exceeds the threshold band (e.g. ±5%)
    if abs(raw_target_equity - current_equity) >= threshold:
      current_equity = raw_target_equity
      current_cash = round(1.0 - current_equity, 2)
      action = "Rebalance"
    else:
      action = "Hold (Threshold Filtered)"

    equity_weights.append(current_equity)
    cash_weights.append(current_cash)
    actions.append(action)

  df["Target_Equity"] = equity_weights
  df["Target_Cash"] = cash_weights
  df["Action"] = actions

  logger.info(
      f"Signal generation complete. Total rows processed: {len(df)}. Latest"
      f" Action: {actions[-1]}"
  )
  return df


if __name__ == "__main__":
  print("--- Testing generate_signals Module ---")
  # Mock test using sample dataframe if run standalone
  import numpy as np

  dates = pd.date_range(end="2026-09-18", periods=10, freq="B").strftime(
      "%Y-%m-%d"
  )
  mock_df = pd.DataFrame({
      "Date": dates,
      "Close": np.linspace(350, 360, 10),
      "Regime": ["Risk-On"] * 8 + ["Risk-Off"] * 2,
  })
  res_df = generate_signals(mock_df)
  print(res_df[["Date", "Regime", "Target_Equity", "Action"]])
