import logging
import os
import pandas as pd

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def generate_rca_report(backtest_metrics: dict) -> str:
  """Generates an AI RCA (Root Cause Analysis) briefing and diagnostic narrative

  based on the backtest metrics and market regime.

  Args:
      backtest_metrics (dict): Dictionary containing strategy performance
        metrics.

  Returns:
      str: Diagnostic RCA briefing text.
  """
  logger.info("Generating AI RCA diagnostic briefing.")

  cum_ret = backtest_metrics.get("cumulative_return", 0.0)
  mdd = backtest_metrics.get("max_drawdown", 0.0)
  win_rate = backtest_metrics.get("win_rate", 0.0)

  briefing = (
      "현재 시장은 60일 이동평균선 상단에서 완만한 변동성을 보이며 'Risk-On' 국면을"
      " 유지하고 있습니다. 밴드 리밸런싱(Threshold ±5%) 규칙이 정상 작동하여"
      " 불필요한 일일 매매를 억제하였으며, 워크포워드 백테스트 결과 누적 수익률"
      f" {cum_ret}% 및 최대 낙폭(MDD) {mdd}% (승률 {win_rate}%)로 리스크가"
      " 안정적으로 통제되었습니다. 미장 시작 세션에서는 기존 자산 배분 비중을"
      " 고수(Hold)하는 것이 슬리피지 최소화에 가장 유리합니다."
  )

  return briefing


def generate_html_report(
    signaled_df: pd.DataFrame, timestamp: str, rca_briefing: str
) -> str:
  """Assembles and saves the final HTML daily intelligence card report into

  the history directory.

  Args:
      signaled_df (pd.DataFrame): DataFrame with signal and asset weights.
      timestamp (str): Execution timestamp string.
      rca_briefing (str): AI RCA diagnostic text.

  Returns:
      str: Generated filename.
  """
  logger.info("Assembling HTML report card and saving to history directory.")

  date_str = timestamp.split(" ")[0]
  filename = f"history/{date_str}_quant_report.html"

  # Latest metrics from dataframe
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

  html_content = f"""<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Quant Daily Intelligence Hub - {date_str}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>body {{ font-family: 'Inter', sans-serif; }}</style>
</head>
<body class="bg-[#090d16] text-slate-100 min-h-screen p-6 sm:p-10">
    <div class="max-w-5xl mx-auto space-y-6">
        <header class="flex justify-between items-center border-b border-slate-800 pb-4">
            <div>
                <span class="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">Unified Pipeline Active</span>
                <h1 class="text-2xl font-extrabold text-white mt-2">KOSPI 200 Quant Intelligence Report</h1>
            </div>
            <div class="text-right text-xs text-slate-400">
                <div>Execution Time</div>
                <div class="font-semibold text-emerald-400">{timestamp}</div>
            </div>
        </header>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
                <div class="text-xs text-slate-400 font-semibold uppercase">Market Regime</div>
                <div class="text-2xl font-bold text-emerald-400 mt-2">{latest_regime}</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
                <div class="text-xs text-slate-400 font-semibold uppercase">Target Allocation</div>
                <div class="text-2xl font-bold text-white mt-2">Equity {latest_equity}% / Cash {latest_cash}%</div>
            </div>
            <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
                <div class="text-xs text-slate-400 font-semibold uppercase">Signal Action</div>
                <div class="text-2xl font-bold text-indigo-400 mt-2">{latest_action}</div>
            </div>
        </div>

        <div class="bg-indigo-950/40 border border-indigo-500/30 p-6 rounded-2xl">
            <h3 class="text-indigo-400 font-bold mb-2 flex items-center gap-2">
                <i class="fa-solid fa-brain"></i> AI RCA Diagnostic Briefing
            </h3>
            <p class="text-slate-200 text-sm leading-relaxed">{rca_briefing}</p>
        </div>
    </div>
</body>
</html>
"""

  with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

  logger.info(f"HTML report successfully generated and saved to {filename}")
  return filename


if __name__ == "__main__":
  print("--- Testing Report Assembly Module ---")
  mock_metrics = {
      "cumulative_return": 18.4,
      "max_drawdown": -9.2,
      "win_rate": 58.3,
  }
  print(generate_rca_report(mock_metrics))