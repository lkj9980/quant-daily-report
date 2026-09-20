import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
  """Performs feature engineering on raw OHLCV market data, calculating moving

  averages, volatility, and the Market Regime Filter.

  Args:
      df (pd.DataFrame): Cleaned DataFrame with Date, Open, High, Low, Close,
        Volume.

  Returns:
      pd.DataFrame: DataFrame appended with SMA_20, SMA_60, Volatility_14d, and
      Regime.
  """
  logger.info(
      "Starting feature engineering and market regime filter calculations."
  )

  feat_df = df.copy()

  # Ensure data is sorted by date
  if "Date" in feat_df.columns:
    feat_df["Date"] = pd.to_datetime(feat_df["Date"])
    feat_df = feat_df.sort_values("Date").reset_index(drop=True)

  # Calculate Technical Indicators
  feat_df["SMA_20"] = feat_df["Close"].rolling(window=20).mean()
  feat_df["SMA_60"] = feat_df["Close"].rolling(window=60).mean()

  # Calculate 14-day rolling volatility (Standard Deviation of daily returns)
  feat_df["Daily_Return"] = feat_df["Close"].pct_change()
  feat_df["Volatility_14d"] = (
      feat_df["Daily_Return"].rolling(window=14).std() * (252**0.5)
  )

  # Define Market Regime Filter (Risk-On vs Risk-Off)
  # Risk-On if Close price is above the 60-day SMA, otherwise Risk-Off
  regimes = []
  for _, row in feat_df.iterrows():
    close = row.get("Close", 0)
    sma_60 = row.get("SMA_60", close)

    # Handle initial NaN values from rolling windows gracefully
    if pd.isna(sma_60):
      regimes.append("Risk-On")
    elif close >= sma_60:
      regimes.append("Risk-On")
    else:
      regimes.append("Risk-Off")

  feat_df["Regime"] = regimes

  # Drop temporary calculation columns if needed
  feat_df.drop(columns=["Daily_Return"], inplace=True, errors="ignore")

  # Drop rows with NaN values resulting from rolling windows
  feat_df = feat_df.dropna().reset_index(drop=True)

  logger.info(
      f"Feature engineering complete. Total valid rows: {len(feat_df)}. Current"
      f" Regime: {feat_df['Regime'].iloc[-1]}"
  )
  return feat_df


if __name__ == "__main__":
  print("--- Testing build_features Module ---")
  import numpy as np

  dates = pd.date_range(end="2026-09-18", periods=100, freq="B").strftime(
      "%Y-%m-%d"
  )
  mock_df = pd.DataFrame({
      "Date": dates,
      "Open": np.linspace(340, 360, 100),
      "High": np.linspace(345, 365, 100),
      "Low": np.linspace(335, 355, 100),
      "Close": np.linspace(340, 360, 100),
      "Volume": [1000000] * 100,
  })
  res_df = build_features(mock_df)
  print(res_df[["Date", "Close", "SMA_60", "Regime"]].tail())