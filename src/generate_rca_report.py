"""
src/generate_rca_report.py

Gemini API를 활용한 AI RCA(Root Cause Analysis) 진단 브리핑 생성 및
외부 템플릿(templates/quant_report_template.html) 기반 최종 HTML 리포트 조립 모듈.
공통 유틸리티(src/utils.py)의 재시도 로직을 임포트하여 사용합니다.
"""

import os
import logging
import pandas as pd
from google import genai

# 공통 유틸리티 임포트
from utils import call_gemini_with_retry

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def generate_rca_report(backtest_metrics: dict, research_context: dict = None) -> str:
    """
    백테스트 결과 지표와 딥리서치 컨텍스트를 받아 Gemini API를 통해 AI RCA 진단 브리핑을 생성합니다.
    """
    logger.info("Generating AI RCA diagnostic briefing via Gemini API.")

    cum_ret = backtest_metrics.get("cumulative_return", 0.0)
    mdd = backtest_metrics.get("max_drawdown", 0.0)
    win_rate = backtest_metrics.get("win_rate", 0.0)
    latest_regime = backtest_metrics.get("latest_regime", "Risk-On")

    if research_context is None:
        research_context = {}
    research_summary = research_context.get("summary", "외부 리서치 정보 없음")
    research_risks = ", ".join(research_context.get("risks", ["특이사항 없음"]))

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
                win_rate=win_rate,
                research_summary=research_summary
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

    prompt = prompt_template.format(
        latest_regime=latest_regime,
        cum_ret=cum_ret,
        mdd=mdd,
        win_rate=win_rate,
        research_summary=research_summary,
        research_risks=research_risks
    )

    try:
        client = genai.Client(api_key=api_key)
        
        response = call_gemini_with_retry(
            client=client,
            model_name="gemini-2.5-flash", 
            prompt_text=prompt,
            max_retries=3,
            delay=10
        )
        
        briefing = response.text.strip()
        logger.info("Successfully generated RCA briefing from Gemini API.")
        return briefing

    except Exception as e:
        logger.error(f"Gemini API failed after all retries or encountered critical error: {e}. Reading strictly from external fallback template.")
        return load_fallback_template()

def generate_html_report(signaled_df: pd.DataFrame, rca_briefing: str, research_context: dict = None) -> str:
    """
    백테스트 결과 DataFrame과 RCA 브리핑, 딥리서치 요약을 바탕으로 최종 HTML 리포트 카드를 조립하고 아카이브 및 index.html에 동기화합니다.
    """
    logger.info("Assembling HTML report card using external template.")

    os.makedirs("history", exist_ok=True)
    template_path = "templates/quant_report_template.html"

    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
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

    if research_context is None:
        research_context = {}
    research_summary = research_context.get("summary", "딥리서치 데이터 없음")

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
        research_summary=research_summary
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    abs_path = os.path.abspath(filename)
    logger.info(f"HTML report successfully generated, saved to {abs_path}, and synced to root index.html")
    return filename