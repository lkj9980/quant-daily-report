import os
import time
from google import genai
from google.genai.errors import ServerError
from src.config import PATHS

def call_gemini_with_retry(client, model_name, prompt_text, max_retries=3, delay=5):
    """
    Gemini API 호출 시 서버 과부하(503) 또는 일시적 오류에 대응하여
    지수 백오프(Exponential Backoff) 방식으로 재시도합니다.
    """
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🔄 Gemini API 호출 시도 ({attempt}/{max_retries})...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
            )
            return response
        except ServerError as e:
            print(f"⚠️ 서버 과부하(503) 또는 일시적 오류 발생: {e}")
            if attempt == max_retries:
                print("❌ 최대 재시도 횟수 초과.")
                raise e
            wait_time = delay * attempt
            print(f"⏳ {wait_time}초 후 재시도합니다...")
            time.sleep(wait_time)
        except Exception as e:
            print(f"❌ 예상치 못한 에러 발생: {e}")
            raise e

def generate_rca_report(backtest_metrics):
    """
    백테스트 성과 지표가 온전하게 전달되었는지 엄격 검증하고,
    중앙 설정된 프롬프트 템플릿 경로를 로드하여 AI 진단을 수행합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ [AI RCA 경고]: GEMINI_API_KEY가 설정되지 않았습니다."

    # 필수 지표 누락 여부 엄격 검증 (가짜 기본값 금지)
    required_keys = ['max_drawdown', 'sharpe_ratio', 'win_rate']
    for key in required_keys:
        if key not in backtest_metrics:
            return f"❌ [AI RCA 에러]: 필수 백테스트 지표('{key}')가 누락되어 AI 진단을 중단합니다."

    mdd_str = str(backtest_metrics.get('max_drawdown'))
    sharpe_str = str(backtest_metrics.get('sharpe_ratio'))
    win_rate_str = str(backtest_metrics.get('win_rate'))

    # 중앙 설정에서 프롬프트 템플릿 경로 가져오기
    prompt_template_path = PATHS["rca_prompt_txt"]
    if os.path.exists(prompt_template_path):
        with open(prompt_template_path, "r", encoding="utf-8") as f:
            template_text = f.read()
    else:
        return f"❌ [AI RCA 에러]: 프롬프트 템플릿 파일을 찾을 수 없습니다 ({prompt_template_path})."

    try:
        client = genai.Client(api_key=api_key)

        prompt = template_text.format(
            sharpe_ratio=sharpe_str,
            max_drawdown=mdd_str,
            win_rate=win_rate_str
        )

        response = call_gemini_with_retry(
            client=client,
            model_name="gemini-3.6-flash",
            prompt_text=prompt,
            max_retries=3,
            delay=5
        )
        
        if response and response.text:
            return f"🤖 [AI RCA 진단]: {response.text.strip()}"
        else:
            return "⚠️ [AI RCA 경고]: 모델로부터 빈 응답이 반환되었습니다."

    except Exception as e:
        print(f"Error generating AI RCA: {e}")
        return f"⚠️ [AI RCA 오류 발생]: {str(e)}"
