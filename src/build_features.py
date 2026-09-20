import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Performs feature engineering on raw OHLCV market data, calculating moving

    averages, volatility, and the Market Regime Filter with robust empty-check safeguards.

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

    if df is None or df.empty:
        raise ValueError("Critical Error: Input DataFrame for feature engineering is empty.")

    feat_df = df.copy()

    # Ensure data is sorted by date
    if "Date" in feat_df.columns:
        feat_df["Date"] = pd.to_datetime(feat_df["Date"])
        feat_df = feat_df.sort_values("Date").reset_index(drop=True)

    # Check if we have enough rows for rolling windows (at least 60 rows required)
    if len(feat_df) < 60:
        logger.warning(
            f"⚠️ Data length ({len(feat_df)}) is less than the 60-day rolling window requirement. "
            "Filling missing rolling values with available Close prices to prevent empty DataFrame crashes."
        )

    # Calculate Technical Indicators
    feat_df["SMA_20"] = feat_df["Close"].rolling(window=20, min_periods=1).mean()
    feat_df["SMA_60"] = feat_df["Close"].rolling(window=60, min_periods=1).mean()

    # Calculate 14-day rolling volatility (Standard Deviation of daily returns)
    feat_df["Daily_Return"] = feat_df["Close"].pct_change().fillna(0)
    feat_df["Volatility_14d"] = (
        feat_df["Daily_Return"].rolling(window=14, min_periods=1).std() * (252**0.5)
    ).fillna(0.0)

    # Define Market Regime Filter (Risk-On vs Risk-Off)
    regimes = []
    for _, row in feat_df.iterrows():
        close = row.get("Close", 0)
        sma_60 = row.get("SMA_60", close)

        if pd.isna(sma_60) or close >= sma_60:
            regimes.append("Risk-On")
        else:
            regimes.append("Risk-Off")

    feat_df["Regime"] = regimes

    # Drop temporary calculation columns if needed
    feat_df.drop(columns=["Daily_Return"], inplace=True, errors="ignore")

    # Guard against empty dataframe after cleaning
    if feat_df.empty:
        raise ValueError("Critical Error: DataFrame became empty after feature engineering and cleaning.")

    latest_regime = feat_df["Regime"].iloc[-1]
    logger.info(
        f"Feature engineering complete. Total valid rows: {len(feat_df)}. Current"
        f" Regime: {latest_regime}"
    )
    return feat_df
