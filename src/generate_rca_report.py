import logging
import os
import time
import pandas as pd
from google import genai

# 공통 유틸리티 임포트
from utils import call_gemini_with_retry

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def generate_rca_report(backtest_metrics: dict) -> str:
    """Generates an AI RCA (Root Cause Analysis) briefing by invoking the Gemini API

    with exponential backoff retries, reading strictly from external template files if unavailable or exhausted.

    Args:
        backtest_metrics (dict): Dictionary containing strategy performance metrics.

    Returns:
        str: Diagnostic RCA briefing text.
    """
    logger.info("Generating AI RCA diagnostic briefing via Gemini API.")

    cum_ret = backtest_metrics.get("cumulative_return", 0.0)
    mdd = backtest_metrics.get("max_drawdown", 0.0)
    win_rate = backtest_metrics.get("win_rate", 0.0)
    latest_regime = backtest_metrics.get("latest_regime", "Risk-On")

    prompt_template_path = "templates/rca_prompt_template.txt"
    fallback_template_path = "templates/rca_fallback_template.txt"

    def load_fallback_template():
        if os.path.exists(fallback_template_path):
            with open(fallback_template_path, "r", encoding="utf-8") as f:
                fallback_template = f.read()
            return fallback_template.format(
                latest_regime=latest_regime,
                cum_ret=cum_ret,
                mdd=mdd,
                win_rate=win_rate
            )
        raise FileNotFoundError(f"Critical Error: Required fallback template not found at {fallback_template_path}.")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY environment variable not found. Reading from external fallback template.")
        return load_fallback_template()

    if not os.path.exists(prompt_template_path):
        raise FileNotFoundError(f"Required prompt template not found at {prompt_template_path}.")

    with open(prompt_template_path, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Format the prompt using the available metrics and regime
    prompt = prompt_template.format(
        latest_regime=latest_regime,
        cum_ret=cum_ret,
        mdd=mdd,
        win_rate=win_rate
    )

    try:
        client = genai.Client(api_key=api_key)
        
        response = call_gemini_with_retry(
            client=client,
            model_name="gemini-3.5-flash", 
            prompt_text=prompt,
            max_retries=3,
            delay=30
        )
        
        briefing = response.text.strip()
        logger.info("Successfully generated RCA briefing from Gemini API.")
        return briefing

    except Exception as e:
        logger.error(f"Gemini API failed after all retries or encountered critical error: {e}. Reading strictly from external fallback template.")
        return load_fallback_template()


def generate_html_report(
    signaled_df: pd.DataFrame, timestamp: str, rca_briefing: str
) -> str:
    """Assembles and saves the final HTML daily intelligence card report into

    the history directory and syncs it to root index.html using an external template file.

    Args:
        signaled_df (pd.DataFrame): DataFrame with signal and asset weights.
        timestamp (str): Execution timestamp string.
        rca_briefing (str): AI RCA diagnostic text.

    Returns:
        str: Generated filename.
    """
    logger.info("Assembling HTML report card using external template.")

    os.makedirs("history", exist_ok=True)
    template_path = "templates/quant_report_template.html"

    date_str = timestamp.split(" ")[0]
    filename = f"history/{date_str}_quant_report.html"

    latest_regime = (
        signaled_df["Regime"].iloc[-1]
        if "Regime" in signaled_df.columns
        else "Risk-On"
    )
    latest_equity = (
        int(signaled_df["Target_Equity"].iloc[-1] * 100)
        if "Target_Equity" in signaled_df.columns
        else 50
    )
    latest_cash = 100 - latest_equity
    latest_action = (
        signaled_df["Action"].iloc[-1]
        if "Action" in signaled_df.columns
        else "Hold"
    )

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Required HTML template not found at {template_path}.")

    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    html_content = template_content.format(
        date_str=date_str,
        timestamp=timestamp,
        latest_regime=latest_regime,
        latest_equity=latest_equity,
        latest_cash=latest_cash,
        latest_action=latest_action,
        rca_briefing=rca_briefing,
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    abs_path = os.path.abspath(filename)
    logger.info(f"HTML report successfully generated, saved to {abs_path}, and synced to root index.html")
    return filename
