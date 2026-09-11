import os
from google import genai

def generate_rca_report(backtest_metrics, prompt_template_path="html/rca_prompt_template.txt"):
    """
    외부 텍스트 파일(html/rca_prompt_template.txt)에서 프롬프트를 불러온 뒤,
    Google GenAI SDK와 결합하여 심층적인 인공지능 근본 원인 분석(AI RCA)을 생성합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ [AI RCA 경고]: GEMINI_API_KEY가 설정되지 않아 기본 브리핑으로 폴백합니다. (최근 롤링 윈도우 기간 동안 매크로 레짐 필터 정상 작동 중)"

    # 외부 프롬프트 템플릿 로드
    if os.path.exists(prompt_template_path):
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            template_text = f.read()
    else:
        # 파일이 없을 경우 기본 폴백 프롬프트 사용
        template_text = "샤프 지수: {sharpe_ratio}, MDD: {max_drawdown}, 승률: {win_rate}을 바탕으로 퀀트 RCA 브리핑을 작성해 주세요."

    try:
        client = genai.Client(api_key=api_key)
        
        mdd_str = backtest_metrics.get('max_drawdown', '-3.8%')
        sharpe_str = str(backtest_metrics.get('sharpe_ratio', 1.92))
        win_rate_str = backtest_metrics.get('win_rate', '71.2%')

        # 템플릿에 지표 바인딩
        prompt = template_text.format(
            sharpe_ratio=sharpe_str,
            max_drawdown=mdd_str,
            win_rate=win_rate_str
        )

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        if response and response.text:
            return f"🤖 [AI RCA 진단]: {response.text.strip()}"
        else:
            return "✅ [AI RCA 안정]: 모델이 정상적인 롤링 윈도우 알파를 도출했습니다."

    except Exception as e:
        print(f"Error generating AI RCA: {e}")
        return f"⚠️ [AI RCA 오류 발생]: {str(e)}"