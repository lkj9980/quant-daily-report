"""
src/generate_research_input.py

Gemini API의 웹 검색(Search Grounding) 기능을 활용한 실시간 딥리서치 인풋 생성 모듈.
제공해주신 레퍼런스(generate_rca_report.py)의 3회 재시도, 지수 백오프 및 예외 방어 패턴을 완벽히 적용하여
일시적인 서버 과부하(503)나 타임아웃 상황을 안전하게 방어합니다.
"""

import os
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from google import genai
from google.genai import types

# 공통 유틸리티 임포트
from utils import call_gemini_with_retry
from config import GEMINI_MODEL


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def load_prompt_template(template_path="templates/deep_research_prompt_template.txt"):
    """
    templates/ 디렉토리에 격리된 프롬프트 템플릿 파일을 읽어옵니다.
    """
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"[Deep Research Gen] 에러: 프롬프트 템플릿을 찾을 수 없습니다 -> {template_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def generate_deep_research_input(output_dir="data/deep_research", template_path="templates/deep_research_prompt_template.txt"):
    """
    Gemini 모델에 Search Grounding 툴을 부여하여 실시간 딥리서치 분석을 수행하고 JSON 인풋 파일을 생성합니다.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("[Deep Research Gen] 경고: GEMINI_API_KEY 환경 변수가 설정되지 않았습니다. 기본 Fallback 데이터를 생성합니다.")
        return save_fallback_research(output_dir)

    try:
        prompt = load_prompt_template(template_path)
    except Exception as e:
        logger.error(f"[Deep Research Gen] 에러: {e}")
        return save_fallback_research(output_dir)

    try:
        client = genai.Client(api_key=api_key)
        model_name = GEMINI_MODEL

        config = types.GenerateContentConfig(
            tools=[{"google_search": {}}],  # 실시간 웹 검색 그라운딩 활성화
            temperature=0.2,
        )

        logger.info(f"[Deep Research Gen] Gemini({model_name}) + Search Grounding을 통한 실시간 딥리서치 수행 중...")
        
        response = call_gemini_with_retry(
            client=client,
            model_name=GEMINI_MODEL,
            prompt_text=prompt,
            config=config,
            max_retries=3,
            delay=10
        )
        
        raw_text = response.text.strip()
        
        # 마크다운 포맷(```json 등) 파싱 방어
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()
            raw_text = raw_text.strip("`").strip()

        research_data = json.loads(raw_text)
        
        # 데이터 정합성 검증 및 기본값 보정
        research_data.setdefault("multiplier", 1.0)
        research_data.setdefault("summary", "딥리서치 요약 정보가 정상 생성되었습니다.")
        research_data.setdefault("risks", [])
        research_data["status"] = "success"

        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        filename = out_path / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(research_data, f, ensure_ascii=False, indent=4)
            
        logger.info(f"[Deep Research Gen] 성공: 실시간 딥리서치 인풋 파일 생성 완료 -> {filename}")
        return True

    except Exception as e:
        logger.error(f"[Deep Research Gen] 에러: 딥리서치 생성 또는 파싱 중 예외 발생 ({e}). Fallback 데이터로 대체합니다.")
        return save_fallback_research(output_dir)

def save_fallback_research(output_dir="data/deep_research"):
    """
    API 장애 또는 키 미설정 시 안전한 Fallback JSON 파일을 생성합니다.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    fallback_data = {
        "multiplier": 1.0,
        "summary": "외부 딥리서치 API 호출 실패로 기본 정량 스코어를 유지합니다.",
        "risks": ["특이사항 없음 (Fallback 모드)"],
        "status": "fallback"
    }
    
    filename = out_path / f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(fallback_data, f, ensure_ascii=False, indent=4)
    logger.info(f"[Deep Research Gen] Fallback 딥리서치 인풋 파일 생성 완료 -> {filename}")
    return True

if __name__ == "__main__":
    generate_deep_research_input()
