import datetime
import logging
import os
import pandas as pd

# Import our modular pipeline components
from src.build_features import build_features
from src.fetch_data import fetch_data
from src.generate_rca_report import generate_html_report, generate_rca_report
from src.generate_signals import generate_signals
from src.run_backtest import run_walk_forward_backtest

# Configure logging for pipeline orchestration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def main():
  """Orchestrates the entire 6-stage unified quantitative pipeline:

  1. Fetch Data
  2. Build Features & Regime Filter
  3. Generate Signals with Threshold Banding
  4. Run Walk-Forward Backtest
  5. Generate AI RCA Diagnostic Briefing
  6. Assemble and Archive HTML Report Card
  """
  now_kst = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  logger.info(
      f"--- KOSPI 200 Quant Intelligence Pipeline Execution Started [{now_kst}] ---"
  )

  # Ensure history directory exists for HTML report archiving
  os.makedirs("history", exist_ok=True)

  try:
    # [Stage 1] Data Acquisition
    logger.info("Stage 1/6: Fetching market data...")
    raw_df = fetch_data(ticker="KOSPI200", period="2y")

    # [Stage 2] Feature Engineering & Market Regime Filter
    logger.info(
        "Stage 2/6: Calculating technical indicators and market regime..."
    )
    features_df = build_features(raw_df)

    # [Stage 3] Signal Generation with Threshold Banding (Turnover Reduction)
    logger.info(
        "Stage 3/6: Generating smoothed portfolio signals and weights..."
    )
    signaled_df = generate_signals(features_df, threshold=0.05)

    # [Stage 4] Walk-Forward Backtest Verification
    logger.info("Stage 4/6: Executing walk-forward backtest simulation...")
    backtest_metrics = run_walk_forward_backtest(signaled_df)

    # [Stage 5] AI RCA Diagnostic Briefing Generation
    logger.info("Stage 5/6: Generating AI RCA diagnostic analysis...")
    rca_briefing = generate_rca_report(backtest_metrics)

    # [Stage 6] HTML Report Assembly and Archiving
    logger.info("Stage 6/6: Assembling and archiving final HTML intelligence card...")
    report_filename = generate_html_report(
        signaled_df=signaled_df, timestamp=now_kst, rca_briefing=rca_briefing
    )

    logger.info(
        f"--- Pipeline Execution Completed Successfully! Report saved to:"
        f" {report_filename} ---"
    )

  except Exception as e:
    logger.error(
        f"Critical error encountered during pipeline execution: {e}",
        exc_info=True,
    )


if __name__ == "__main__":
  main()
