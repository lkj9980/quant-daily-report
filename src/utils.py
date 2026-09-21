"""
src/utils.py

Gemini API 호출 시 공통으로 사용되는 3회 재시도, 지수 백오프 및 ServerError 방어 로직 모듈.
중복 코드(DRY 원칙)를 방지하기 위해 분리되었습니다.
"""

import time
import logging
from google.genai.errors import ServerError

logger = logging.getLogger(__name__)

def call_gemini_with_retry(client, model_name: str, prompt_text: str, config=None, max_retries: int = 3, delay: int = 30):
    """
    일시적인 서버 과부하(503) 또는 타임아웃 오류 대응을 위한 재시도 및 지수 백오프 로직을 포함한 Gemini API 호출 공통 함수.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🔄 Gemini API 호출 시도 ({attempt}/{max_retries})...")
            if config:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                    config=config
                )
            else:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt_text,
                )
            return response
        except ServerError as e:
            logger.warning(f"⚠️ 서버 과부하(503) 또는 일시적 오류 발생: {e}")
            if attempt == max_retries:
                logger.error("❌ 최대 재시도 횟수 초과.")
                raise e
            wait_time = delay * attempt
            logger.info(f"⏳ {wait_time}초 후 재시도합니다...")
            time.sleep(wait_time)
        except Exception as e:
            logger.error(f"❌ 예상치 못한 에러 발생: {e}")
            raise e