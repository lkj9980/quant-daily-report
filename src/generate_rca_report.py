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
from config import GEMINI_MODEL

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
            model_name=GEMINI_MODEL,
            prompt_text=prompt,
            config=config,
            max_retries=3,
            delay=10
        )
        
        briefing = response.text.strip()
        logger.info("Successfully generated RCA briefing from Gemini API.")
        return briefing

    except Exception as e:
        logger.error(f"Gemini API failed after all retries or encountered critical error: {e}. Reading strictly from external fallback template.")
        return load_fallback_template()

def generate_html_report(signaled_data, rca_briefing: str, research_context: dict = None) -> str:
    """
    백테스트 결과(DataFrame 또는 dict)와 RCA 브리핑, 딥리서치 요약을 바탕으로 최종 HTML 리포트 카드를 조립합니다.
    """
    logger.info("Assembling HTML report card using external template.")

    os.makedirs("history", exist_ok=True)
    template_path = "templates/quant_report_template.html"

    timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = timestamp.split(" ")[0]
    filename = f"history/{date_str}_quant_report.html"

    # signaled_data가 DataFrame인지 dict인지 안전하게 분기 처리
    if isinstance(signaled_data, pd.DataFrame):
        latest_regime = (
            signaled_data["Regime"].iloc[-1]
            if "Regime" in signaled_data.columns
            else "Risk-On"
        )
        latest_equity = (
            int(signaled_data["Target_Equity"].iloc[-1] * 100)
            if "Target_Equity" in signaled_data.columns
            else 50
        )
        latest_action = (
            signaled_data["Action"].iloc[-1]
            if "Action" in signaled_data.columns
            else "Hold"
        )
    elif isinstance(signaled_data, dict):
        latest_regime = signaled_data.get("latest_regime", "Risk-On")
        latest_equity = int(signaled_data.get("target_equity", 0.5) * 100)
        latest_action = signaled_data.get("action", "Hold")
    else:
        latest_regime = "Risk-On"
        latest_equity = 50
        latest_action = "Hold"

    latest_cash = 100 - latest_equity

    if research_context is None:
        research_context = {}
    research_summary = research_context.get("summary", "딥리서치 데이터 없음")
    
    # 딥리서치 리스크 항목들을 HTML 리스트 마크업으로 변환하여 템플릿에 주입
    risks = research_context.get("risks", [])
    if risks:
        risks_items_html = "".join([f'<li class="flex items-start space-x-2 text-sm text-amber-200/90"><span class="text-amber-400 mt-0.5">•</span><span>{risk}</span></li>' for risk in risks])
        research_risks_html = f"""
        <div class="bg-slate-950/60 rounded-xl p-4 border border-slate-800/80 mt-3">
            <span class="text-xs font-semibold text-amber-400 uppercase tracking-wide">식별된 주요 거시/수급 리스크</span>
            <ul class="mt-2 space-y-1.5">
                {risks_items_html}
            </ul>
        </div>
        """
    else:
        research_risks_html = ""

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
        research_summary=research_summary,
        research_risks_html=research_risks_html
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    abs_path = os.path.abspath(filename)
    logger.info(f"HTML report successfully generated, saved to {abs_path}, and synced to root index.html")
    return filename
